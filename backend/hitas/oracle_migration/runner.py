import datetime
import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple, Type, TypeVar

import pytz
from django.contrib.auth import get_user_model
from django.db import models
from sqlalchemy import create_engine
from sqlalchemy.engine import LegacyRow
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql import select

from hitas.models import (
    AbstractCode,
    Apartment,
    ApartmentState,
    ApartmentType,
    Building,
    BuildingType,
    Developer,
    FinancingMethod,
    HitasPostalCode,
    HousingCompany,
    HousingCompanyState,
    Ownership,
    Person,
    PropertyManager,
    RealEstate,
)
from hitas.oracle_migration.cost_areas import hitas_cost_area, init_cost_areas
from hitas.oracle_migration.globals import anonymize_data
from hitas.oracle_migration.oracle_schema import (
    additional_infos,
    apartment_ownerships,
    apartments,
    codebooks,
    codes,
    companies,
    property_managers,
    real_estates,
    users,
)

TZ = pytz.timezone("Europe/Helsinki")


@dataclass
class CreatedBuilding:
    value: Building = None
    apartments: List[Apartment] = field(default_factory=list)


@dataclass
class CreatedRealEstate:
    value: RealEstate = None
    buildings: List[CreatedBuilding] = field(default_factory=list)


@dataclass
class CreatedHousingCompany:
    value: HousingCompany = None
    real_estates: List[CreatedRealEstate] = field(default_factory=list)


@dataclass
class ConvertedData:
    created_housing_companies_by_oracle_id: Dict[int, CreatedHousingCompany] = None
    apartments_by_oracle_id: Dict[int, Apartment] = None

    users_by_username: Dict[str, get_user_model()] = None
    property_managers_by_oracle_id: Dict[int, PropertyManager] = None

    building_types_by_code_number: Dict[str, BuildingType] = None
    developers_by_code_number: Dict[str, Developer] = None
    financing_methods_by_code_number: Dict[str, FinancingMethod] = None
    postal_codes_by_postal_code: Dict[str, HitasPostalCode] = None
    apartment_types_by_code_numer: Dict[str, ApartmentType] = None


def run(
    oracle_host: str,
    oracle_port: str,
    oracle_user: str,
    oracle_pw: str,
    debug: bool,
    anonymize: bool,
    truncate: bool,
    truncate_only: bool,
) -> None:

    if debug:
        logging.basicConfig()
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    if anonymize:
        anonymize_data()

    if truncate or truncate_only:
        do_truncate()

    if truncate_only:
        return

    init_cost_areas()

    # Disable auto_now as we want not to update the last_modified_datetime but instead migrate the old value
    turn_off_auto_now(HousingCompany, "last_modified_datetime")

    converted_data = ConvertedData()

    engine = create_engine(
        f"oracle+cx_oracle://{oracle_user}:{oracle_pw}@{oracle_host}:{oracle_port}/xe?" "encoding=UTF-8&nencoding=UTF-8"
    )

    with engine.connect() as connection:
        with connection.begin():
            print(f"Connected to oracle database at {oracle_host}:{oracle_port}.")
            print()

            # Codebooks by id
            codebooks_by_id = read_codebooks(connection)

            # Users
            converted_data.users_by_username = create_users(connection)

            # Codebooks
            converted_data.building_types_by_code_number = create_codes(
                codebooks_by_id["TALOTYYPPI"], BuildingType, modify_fn=format_building_type
            )
            converted_data.developers_by_code_number = create_codes(codebooks_by_id["RAKENTAJA"], Developer)
            converted_data.financing_methods_by_code_number = create_codes(
                codebooks_by_id["RAHMUOTO"], FinancingMethod, modify_fn=format_financing_method
            )
            converted_data.apartment_types_by_code_numer = create_codes(codebooks_by_id["HUONETYYPPI"], ApartmentType)

            # Postal codes
            converted_data.postal_codes_by_postal_code = create_unsaved_postal_codes(codebooks_by_id["POSTINROT"])

            # Property managers
            converted_data.property_managers_by_oracle_id = create_property_managers(connection)

            # Housing companies
            converted_data.created_housing_companies_by_oracle_id = create_housing_companies(connection, converted_data)

            # Real estates (and buildings) and apartments
            converted_data.apartments_by_oracle_id = {}
            for chc in converted_data.created_housing_companies_by_oracle_id.values():
                chc.real_estates = create_real_estates_and_buildings(chc.value, connection)
                created_building = chc.real_estates[0].buildings[0]

                # Create apartments
                created_apartments = create_apartments(created_building.value, connection, converted_data)
                created_building.apartments = created_apartments.values()
                converted_data.apartments_by_oracle_id.update(created_apartments)

            total_real_estates = sum(
                map(lambda hc: len(hc.real_estates), converted_data.created_housing_companies_by_oracle_id.values())
            )

            print(f"Loaded {total_real_estates} real estates.")
            print()
            print(f"Loaded {total_real_estates} buildings.")
            print()
            print(f"Loaded {len(converted_data.apartments_by_oracle_id)} apartments.")
            print()

            # Apartment owners
            create_ownerships(connection, converted_data)


def create_housing_companies(connection: Connection, converted_data: ConvertedData) -> Dict[str, CreatedHousingCompany]:
    housing_companies_by_id = {}

    for hc in connection.execute(select(companies, additional_infos).join(additional_infos, isouter=True)).fetchall():
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
        new.building_type = converted_data.building_types_by_code_number[hc["building_type_code"]]
        new.developer = converted_data.developers_by_code_number[hc["developer_code"]]
        new.postal_code = converted_data.postal_codes_by_postal_code[hc["postal_code_code"]]
        new.financing_method = converted_data.financing_methods_by_code_number[hc["financing_method_code"]]
        new.property_manager = converted_data.property_managers_by_oracle_id[hc["property_manager_id"]]
        new.last_modified_by = converted_data.users_by_username.get(hc["last_modified_by"])

        # Only save postal codes linked to housing companies
        if new.postal_code._state.adding:
            new.postal_code.save()

        new.save()
        housing_companies_by_id[new.legacy_id] = CreatedHousingCompany(value=new)

    print(f"Loaded {len(housing_companies_by_id)} housing companies.")
    print()

    return housing_companies_by_id


def create_real_estates_and_buildings(
    housing_company: HousingCompany,
    connection: Connection,
) -> List[CreatedRealEstate]:
    created_real_estates = []

    for real_estate in connection.execute(
        select(real_estates).where(real_estates.c.company_id == housing_company.legacy_id)
    ).fetchall():
        new = RealEstate()
        new.housing_company = housing_company
        new.property_identifier = real_estate["property_identifier"]
        new.street_address = housing_company.street_address

        new.save()

        b = Building()
        b.real_estate = new
        b.street_address = new.street_address
        b.building_identifier = ""

        b.save()

        created_real_estates.append(CreatedRealEstate(value=new, buildings=[CreatedBuilding(value=b)]))

    return created_real_estates


def create_apartments(
    building: Building, connection: Connection, converted_data: ConvertedData
) -> Dict[int, Apartment]:
    apartments_by_id = {}

    bulk_apartments = []

    for apartment in connection.execute(
        select(apartments, additional_infos)
        .join(additional_infos, isouter=True)
        .where(apartments.c.company_id == building.real_estate.housing_company.legacy_id)
    ).fetchall():
        new = Apartment()
        new.building = building
        new.state = ApartmentState.SOLD
        new.apartment_type = converted_data.apartment_types_by_code_numer[apartment["apartment_type_code"]]
        new.surface_area = apartment["surface_area"]
        new.street_address = apartment["street_address"]
        new.apartment_number = apartment["apartment_number"]
        new.floor = apartment["floor"]
        new.stair = apartment["stair"]
        new.first_purchase_date = apartment["first_purchase_date"]
        new.second_purchase_date = apartment["second_purchase_date"]
        new.debt_free_purchase_price = apartment["debt_free_purchase_price"]
        new.purchase_price = apartment["purchase_price"]
        new.additional_work_during_construction = apartment["additional_work_during_construction"]
        new.primary_loan_amount = apartment["primary_loan_amount"]
        new.loans_during_construction = apartment["loans_during_construction"]
        new.interest_during_construction = apartment["interest_during_construction"]
        new.debt_free_purchase_price_during_construction = apartment["debt_free_purchase_price_during_construction"]
        new.completion_date = apartment["completion_date"]
        new.notes = combine_notes(apartment)

        if apartment["share_number_start"] != 0 and apartment["share_number_end"] != 0:
            new.share_number_start = apartment["share_number_start"]
            new.share_number_end = apartment["share_number_end"]

        bulk_apartments.append(new)

        if len(bulk_apartments) == 1000:
            Apartment.objects.bulk_create(bulk_apartments)
            bulk_apartments = []

        apartments_by_id[apartment[apartments.c.id]] = new

    if len(bulk_apartments):
        Apartment.objects.bulk_create(bulk_apartments)

    return apartments_by_id


def split_person_name(name) -> Tuple[str, str]:
    if name:
        splitted_name = name.split(", ", maxsplit=1)
        if len(splitted_name) == 2:
            return splitted_name
        else:
            return "", name

    return "", ""


def create_ownerships(connection: Connection, converted_data: ConvertedData) -> None:
    count = 0
    bulk_persons = []
    bulk_ownerships = []

    for ownership in connection.execute(
        select(apartment_ownerships).where(apartment_ownerships.c.apartment_id != 0)
    ).fetchall():
        new_person = Person()
        new_person.first_name, new_person.last_name = split_person_name(ownership["name"])
        new_person.social_security_number = ownership["social_security_number"]
        new_person.legacy_social_security_number = True
        new_person.clean()
        bulk_persons.append(new_person)

        new = Ownership()
        new.apartment = converted_data.apartments_by_oracle_id[ownership["apartment_id"]]
        new.owner = new_person
        new.percentage = ownership["percentage"]
        new.start_date = None
        new.end_date = None

        bulk_ownerships.append(new)
        count += 1

        if len(bulk_persons) == 1000:
            Person.objects.bulk_create(bulk_persons)
            Ownership.objects.bulk_create(bulk_ownerships)

            bulk_persons = []
            bulk_ownerships = []

    if len(bulk_persons):
        Person.objects.bulk_create(bulk_persons)
        Ownership.objects.bulk_create(bulk_ownerships)

    print(f"Loaded {count} owners.")
    print()


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

        property_managers_by_id[pm[property_managers.c.id]] = new

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
            is_superuser=True,
            is_staff=True,
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


def date_to_datetime(d: datetime.date) -> Optional[datetime.datetime]:
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


def turn_off_auto_now(model: Type[models.Model], field_name: str) -> None:
    model._meta.get_field(field_name).auto_now = False


def do_truncate():
    Ownership.objects.all().delete()
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
