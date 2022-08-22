import datetime
import logging
from dataclasses import dataclass
from typing import Callable, Dict, List, TypeVar

import pytz
from django.contrib.auth import get_user_model
from sqlalchemy import and_, create_engine
from sqlalchemy.engine import LegacyRow
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql import select

from hitas.models import (
    AbstractCode,
    Apartment,
    ApartmentType,
    Building,
    BuildingType,
    Developer,
    FinancingMethod,
    HitasPostalCode,
    HousingCompany,
    HousingCompanyState,
    Owner,
    Person,
    PropertyManager,
    RealEstate,
)
from hitas.oracle_migration.cost_areas import hitas_cost_area, init_cost_areas
from hitas.oracle_migration.globals import anonymize_data
from hitas.oracle_migration.oracle_schema import (
    additional_infos,
    codebooks,
    codes,
    companies,
    company_addresses,
    property_managers,
    users,
)

TZ = pytz.timezone("Europe/Helsinki")


@dataclass
class ConvertedData:
    users: Dict[str, get_user_model()] = None
    building_types: Dict[str, BuildingType] = None
    postal_codes: Dict[str, HitasPostalCode] = None
    developers: Dict[str, Developer] = None
    financing_methods: Dict[str, FinancingMethod] = None
    property_managers: Dict[str, PropertyManager] = None


def run(
    oracle_host: str,
    oracle_port: str,
    oracle_user: str,
    oracle_pw: str,
    debug: bool,
    anonymize: bool,
    truncate: bool,
) -> None:

    if debug:
        logging.basicConfig()
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    if anonymize:
        anonymize_data()

    if truncate:
        do_truncate()

    init_cost_areas()

    # Disable auto_now as we want not to update the last_modified_datetime but instead migrate the old value
    turn_off_auto_now(HousingCompany, "last_modified_datetime")

    converted_data = ConvertedData()

    engine = create_engine(
        f"oracle+cx_oracle://{oracle_user}:{oracle_pw}@{oracle_host}:{oracle_port}/xe?" "encoding=UTF-8&nencoding=UTF-8"
    )

    with engine.connect() as connection:
        with connection.begin():
            # Codebooks by id
            codebooks_by_id = read_codebooks(connection)

            # Users
            converted_data.users = create_users(connection)

            # Codebooks
            converted_data.building_types = create_codes(
                codebooks_by_id["TALOTYYPPI"], BuildingType, modify_fn=format_building_type
            )
            converted_data.developers = create_codes(codebooks_by_id["RAKENTAJA"], Developer)
            converted_data.financing_methods = create_codes(
                codebooks_by_id["RAHMUOTO"], FinancingMethod, modify_fn=format_financing_method
            )

            # Postal codes
            converted_data.postal_codes = create_unsaved_postal_codes(codebooks_by_id["POSTINROT"])

            # Property managers
            converted_data.property_managers = create_property_managers(connection)

            # Housing companies
            converted_data.housing_companies = create_housing_companies(connection, converted_data)


def create_housing_companies(connection: Connection, converted_data: ConvertedData) -> HousingCompany:
    housing_companies_by_id = {}

    a = additional_infos.alias("AI_COMPANY")
    b = additional_infos.alias("AI_PROPERTY_MANAGER")

    for hc in connection.execute(
        select(companies, company_addresses, property_managers, a, b)
        .join(company_addresses, isouter=True)
        .join(property_managers, isouter=True)
        .join(
            a,
            and_(companies.c.additional_info_key == a.c.type, companies.c.id == a.c.object_id),
            isouter=True,
        )
        .join(
            b,
            and_(property_managers.c.additional_info_key == b.c.type, property_managers.c.id == b.c.object_id),
            isouter=True,
        )
    ).fetchall():
        new = HousingCompany()
        new.official_name = hc["official_name"]
        new.display_name = hc["display_name"]
        new.state = housing_company_state_from(hc["state_code"])
        new.business_id = ""
        new.street_address = hc["address"]
        new.acquisition_price = hc["acquisition_price"]
        new.realized_acquisition_price = hc["realized_acquisition_price"]
        new.primary_loan = hc["primary_loan"]
        new.sales_price_catalogue_confirmation_date = date_to_datetime(hc["sales_price_catalogue_confirmation_date"])
        new.notification_date = date_to_datetime(hc["notification_date"])
        new.legacy_id = hc[companies.c.id]
        new.notes = combine_notes(hc)
        new.last_modified_datetime = date_to_datetime(hc["last_modified"])
        new.building_type = converted_data.building_types[hc["building_type_code"]]
        new.developer = converted_data.developers[hc["developer_code"]]
        new.postal_code = converted_data.postal_codes[hc["postal_code_code"]]
        new.financing_method = converted_data.financing_methods[hc["financing_method_code"]]
        new.property_manager = converted_data.property_managers[hc["property_manager_id"]]
        new.last_modified_by = converted_data.users.get(hc["last_modified_by"])

        # Only save postal codes linked to housing companies
        if new.postal_code._state.adding:
            new.postal_code.save()

        new.save()
        housing_companies_by_id[new.legacy_id] = new

    print(f"Loaded {len(housing_companies_by_id)} housing companies.")
    print()

    return housing_companies_by_id


def create_property_managers(connection: Connection) -> Dict[str, PropertyManager]:
    property_managers_by_id = {}

    #
    # Fetch all codebooks
    #
    for pm in connection.execute(select(property_managers)).fetchall():
        new = PropertyManager()
        new.name = pm["name"]
        new.email = pm["email"] or ""
        new.street_address = pm["address"]
        new.postal_code = pm["postal_code"]
        new.city = pm["city"].capitalize()
        new.save()

        property_managers_by_id[pm.id] = new

    print(f"Loaded {len(property_managers_by_id)} property managers.")
    print()

    return property_managers_by_id


def read_codebooks(
    connection: Connection,
) -> Dict[str, List[LegacyRow]]:
    codebooks_by_id = {}
    total_codes = 0

    #
    # Fetch all codebooks
    #
    for codebook in connection.execute(select(codebooks)).fetchall():
        new_codes = []
        codebooks_by_id[codebook["code_type"]] = new_codes

        #
        # Fetch all codes by codebook
        #
        for code in connection.execute(select(codes).where(codes.c.code_type == codebook["code_type"])).fetchall():
            new_codes.append(code)
            total_codes += 1

    print(f"Loaded {len(codebooks_by_id)} codebooks with total of {total_codes} codes.")
    print()

    return codebooks_by_id


def create_users(
    connection: Connection,
) -> Dict[str, Dict[str, get_user_model()]]:
    users_by_id = {}

    #
    # Fetch all enabled users
    #

    for user in connection.execute(select(users)).fetchall():  # noqa
        splitted_name = user["name"].split(" ", maxsplit=1)
        first_name, last_name = splitted_name[0].capitalize(), splitted_name[1].capitalize()

        created_user = get_user_model().objects.create_user(
            user["username"],
            password=user["password"],
            first_name=first_name,
            last_name=last_name,
            is_active=user["is_active"],
        )

        users_by_id[user["username"]] = created_user

    print(f"Loaded {len(users_by_id)} users.")
    print()

    return users_by_id


def combine_notes(a: LegacyRow) -> str:
    return "\n".join(
        [note for note in [a["TEKSTI1"], a["TEKSTI2"], a["TEKSTI3"], a["TEKSTI4"], a["TEKSTI5"]] if note is not None]
    )


def format_building_type(bt: BuildingType) -> None:
    bt.value = bt.value.capitalize()


def format_financing_method(fm: FinancingMethod) -> None:
    # Only capitalize those with first letter lowercased
    # Don't capitalize all - there's some that would suffer from it
    if fm.value[0].islower():
        fm.value = fm.value[0].upper() + fm.value[1:]


def housing_company_state_from(code: str) -> HousingCompanyState:
    # These are hardcoded as the code number (C_KOODISTOID) and
    # the name (C_NAME) are the only ones that can be used to
    # identify these types
    match code:
        case "000":
            return HousingCompanyState.NOT_READY
        case "001":
            return HousingCompanyState.LESS_THAN_30_YEARS
        case "002":
            return HousingCompanyState.GREATER_THAN_30_YEARS_NOT_FREE
        case "003":
            return HousingCompanyState.GREATER_THAN_30_YEARS_FREE
        case "004":
            return HousingCompanyState.GREATER_THAN_30_YEARS_PLOT_DEPARTMENT_NOTIFICATION
        case "005":
            return HousingCompanyState.HALF_HITAS


def printc(column: str, value: str) -> None:
    print(f"{column: <40} - {value}")


def print_codebook(codebooks: Dict[str, Dict[str, LegacyRow]], code_type: str) -> None:
    for code in codebooks[code_type].values():
        for column in codes.c:
            printc(str(column), code[column])
        print()


def printm(model, instance):
    for f in model._meta.get_fields():
        if f.is_relation:
            from django.core.exceptions import ObjectDoesNotExist

            try:
                printc(f.name, getattr(instance, f.name))
            except ObjectDoesNotExist:
                printc(f.name, None)
        else:
            printc(f.name, f.value_from_object(instance))

    print()


def date_to_datetime(d: datetime.date) -> datetime.datetime:
    if d is None:
        return None

    return TZ.localize(datetime.datetime.combine(d, datetime.datetime.min.time()))


def create_unsaved_postal_codes(codes: List[LegacyRow]) -> Dict[str, HitasPostalCode]:
    retval = {}

    for code in codes:
        postal_code = HitasPostalCode()

        postal_code.value = code["code_id"]
        postal_code.city = code["value"].capitalize()
        postal_code.cost_area = hitas_cost_area(code["code_id"])

        retval[postal_code.value] = postal_code

    return retval


T = TypeVar("T", bound=AbstractCode)


def create_codes(codes: List[LegacyRow], fn: Callable[[], T], modify_fn: Callable[[T], None] = None) -> Dict[str, T]:
    retval = {}

    for code in codes:
        new = fn()

        new.value = code["value"]
        new.description = code["description"] or ""
        new.in_use = code["in_use"]
        new.order = code["order"]
        new.legacy_code_number = code["code_id"]
        new.legacy_start_date = date_to_datetime(code["start_date"])
        new.legacy_end_date = date_to_datetime(code["end_date"])

        retval[new.legacy_code_number] = new
        if modify_fn:
            modify_fn(new)
        new.save()

    return retval


def turn_off_auto_now(model, field_name):
    model._meta.get_field(field_name).auto_now = False


def do_truncate():
    Owner.objects.all().delete()
    Apartment.objects.all().delete()
    ApartmentType.objects.all().delete()
    Building.objects.all().delete()
    RealEstate.objects.all().delete()
    HousingCompany.objects.all().delete()
    PropertyManager.objects.all().delete()
    BuildingType.objects.all().delete()
    Developer.objects.all().delete()
    FinancingMethod.objects.all().delete()
    Person.objects.all().delete()
    HitasPostalCode.objects.all().delete()
    get_user_model().objects.all().delete()
