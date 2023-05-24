import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from difflib import SequenceMatcher
from typing import Callable, Dict, List, Optional, TypeVar

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db import connection as django_connection
from django.db.models import Max, OuterRef, Prefetch, Subquery
from django.utils import timezone
from safedelete import HARD_DELETE
from sqlalchemy import create_engine, desc, func
from sqlalchemy.engine import LegacyRow
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql import select

from hitas.calculations.construction_time_interest import Payment, total_construction_time_interest
from hitas.models import (
    AbstractCode,
    Apartment,
    ApartmentConstructionPriceImprovement,
    ApartmentMarketPriceImprovement,
    ApartmentMaximumPriceCalculation,
    ApartmentSale,
    ApartmentState,
    ApartmentType,
    Building,
    BuildingType,
    ConstructionPriceIndex,
    ConstructionPriceIndex2005Equal100,
    DepreciationPercentage,
    Developer,
    FinancingMethod,
    HitasPostalCode,
    HousingCompany,
    HousingCompanyConstructionPriceImprovement,
    HousingCompanyMarketPriceImprovement,
    MarketPriceIndex,
    MarketPriceIndex2005Equal100,
    MaximumPriceIndex,
    MigrationDone,
    Owner,
    Ownership,
    PropertyManager,
    RealEstate,
    SurfaceAreaPriceCeiling,
)
from hitas.models.housing_company import HitasType
from hitas.models.indices import AbstractIndex
from hitas.models.utils import check_business_id, check_social_security_number
from hitas.oracle_migration.cost_areas import hitas_cost_area, init_cost_areas
from hitas.oracle_migration.financing_types import (
    FINANCING_METHOD_TO_HITAS_TYPE_MAP,
    format_financing_method,
    strip_financing_method_id,
)
from hitas.oracle_migration.globals import anonymize_data, faker, should_anonymize
from hitas.oracle_migration.oracle_schema import (
    additional_infos,
    apartment_construction_price_indices,
    apartment_market_price_indices,
    apartment_ownerships,
    apartment_payments,
    apartments,
    codebooks,
    codes,
    companies,
    company_addresses,
    company_construction_price_indices,
    company_market_price_indices,
    construction_price_indices,
    hitas_monitoring,
    market_price_indices,
    property_managers,
    real_estates,
    users,
)
from hitas.oracle_migration.utils import (
    ApartmentSaleMonitoringState,
    combine_notes,
    date_to_datetime,
    format_building_type,
    housing_company_regulation_status_from,
    str_to_year_month,
    value_to_depreciation_percentage,
)
from hitas.utils import monthify

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
    interest_rate: Decimal = None
    addresses: set[str] = field(default_factory=list)
    real_estates: list[CreatedRealEstate] = field(default_factory=list)


@dataclass(frozen=True)
class OwnerKey:
    identifier: str
    name: str


@dataclass
class ConvertedData:
    created_housing_companies_by_oracle_id: Dict[int, CreatedHousingCompany] = None
    apartments_by_oracle_id: Dict[int, Apartment] = None

    users_by_username: Dict[str, get_user_model()] = None
    property_managers_by_oracle_id: Dict[int, PropertyManager] = None

    building_types_by_code_number: Dict[str, BuildingType] = None
    developers_by_code_number: Dict[str, Developer] = None
    financing_methods_by_code_number: Dict[str, FinancingMethod] = None
    hitas_types_by_code_number: Dict[str, HitasType] = None
    postal_codes_by_postal_code: Dict[str, HitasPostalCode] = None
    apartment_types_by_code_number: Dict[str, ApartmentType] = None

    owners: Dict[str, Owner] = None
    current_ownerships_by_oracle_apartment_id: dict[int, list[Ownership]] = None


BULK_INSERT_THRESHOLD: int = 1000
APARTMENTS_WITH_OWNER_CHANGES_WITHOUT_SALES: list[int] = [
    # These changes are due to periodic checks of
    # the sales catalog or from estate inventory deeds
    14335,
    14906,
    15332,
    12059,
    12959,
    20136,
    17938,
    18433,
    18688,
    21919,
    22503,
    21235,
]
APARTMENTS_WITH_ALLOWED_OWNER_CHANGES: list[int] = [
    # These changes are valid,
    # but could not be determined programmatically
    14547,
    14561,
    14829,
    15196,
    15214,
    11848,
    12136,
    12142,
    12539,
    12588,
    12749,
    13110,
    13809,
    17123,
    17937,
    18200,
    18627,
    20992,
    # These changes are can be corrected
    # before or after the migration to the new system
    11866,
]


def run(
    oracle_host: str,
    oracle_port: str,
    oracle_user: str,
    oracle_pw: str,
    debug: bool,
    anonymize: bool,
    truncate: bool,
    truncate_only: bool,
    minimal_dataset: bool,
    regulated_only: bool,
) -> None:
    if debug:
        logging.basicConfig()
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        logger.setLevel(logging.DEBUG)

    if anonymize:
        logger.info("Creating anonymized data...\n")
        anonymize_data()
    else:
        logger.info("Creating *REAL* non-anonymized data...\n")

    if truncate or truncate_only:
        logger.info("Removing existing data...\n")
        do_truncate()

    if truncate_only:
        return

    init_cost_areas()

    converted_data = ConvertedData()

    engine = create_engine(
        f"oracle+cx_oracle://{oracle_user}:{oracle_pw}@{oracle_host}:{oracle_port}/xe?" "encoding=UTF-8&nencoding=UTF-8"
    )

    with engine.connect() as connection:
        with connection.begin():
            logger.info(f"Connected to oracle database at {oracle_host}:{oracle_port}.\n")

            # Codebooks by id
            codebooks_by_id = read_codebooks(connection)

            # Users
            converted_data.users_by_username = create_users(connection)

            # Codebooks
            converted_data.building_types_by_code_number = create_codes(
                codebooks_by_id["TALOTYYPPI"], BuildingType, modify_fn=format_building_type
            )
            converted_data.developers_by_code_number = create_codes(
                codebooks_by_id["RAKENTAJA"], Developer, sensitive=True
            )
            converted_data.financing_methods_by_code_number = create_codes(
                codebooks_by_id["RAHMUOTO"], FinancingMethod, modify_fn=format_financing_method
            )
            converted_data.hitas_types_by_code_number = create_hitas_types(codebooks_by_id["RAHMUOTO"])

            converted_data.apartment_types_by_code_number = create_codes(codebooks_by_id["HUONETYYPPI"], ApartmentType)

            # Indices
            create_indices(codebooks_by_id["HITASEHIND"], MaximumPriceIndex)
            create_indices(codebooks_by_id["MARKHINTAIND"], MarketPriceIndex)
            create_indices(codebooks_by_id["MARKHINTAIND2005"], MarketPriceIndex2005Equal100)
            create_indices(codebooks_by_id["RAKUSTIND"], ConstructionPriceIndex)
            create_indices(codebooks_by_id["RAKUSTIND2005"], ConstructionPriceIndex2005Equal100)
            create_indices(codebooks_by_id["RAJAHINNAT"], SurfaceAreaPriceCeiling)

            # Postal codes
            converted_data.postal_codes_by_postal_code = create_unsaved_postal_codes(codebooks_by_id["POSTINROT"])

            # Property managers
            converted_data.property_managers_by_oracle_id = create_property_managers(connection)

            # Housing companies
            converted_data.created_housing_companies_by_oracle_id = create_housing_companies(
                connection, converted_data, minimal_dataset, regulated_only
            )

            # Housing company improvements
            create_housing_company_improvements(connection, converted_data)

            # Real estates (and buildings) and apartments
            converted_data.apartments_by_oracle_id = {}
            for chc in converted_data.created_housing_companies_by_oracle_id.values():
                chc.real_estates = create_real_estates_and_buildings(chc.value, chc.addresses, connection)
                created_building = chc.real_estates[0].buildings[0]

                # Create apartments
                created_apartments = create_apartments(created_building.value, connection, converted_data)
                created_building.apartments = created_apartments.values()
                converted_data.apartments_by_oracle_id.update(created_apartments)

            total_real_estates = sum(
                len(hc.real_estates) for hc in converted_data.created_housing_companies_by_oracle_id.values()
            )

            logger.info(f"Loaded {total_real_estates} real estates.\n")
            logger.info(f"Loaded {total_real_estates} buildings.\n")
            logger.info(f"Loaded {len(converted_data.apartments_by_oracle_id)} apartments.\n")

            # Apartment improvements
            create_apartment_improvements(connection, converted_data)

            # Apartment maximum price calculations
            create_apartment_max_price_calculations(connection, converted_data)

            # Apartment owners
            create_owners_and_ownerships(connection, converted_data)

            # Apartment sales history
            create_apartment_sales(connection, converted_data)

            # Remove apartments owned by housing companies
            remove_apartments_owned_by_housing_companies()

    MigrationDone.objects.create()


def do_truncate():
    for model_class in [
        Apartment,
        ApartmentType,
        Building,
        RealEstate,
        HousingCompany,
        PropertyManager,
        BuildingType,
        Developer,
        FinancingMethod,
        Owner,
        HitasPostalCode,
    ]:
        model_class.objects.all_with_deleted().delete(force_policy=HARD_DELETE)

    for model_class in [
        get_user_model(),
        SurfaceAreaPriceCeiling,
        ConstructionPriceIndex2005Equal100,
        ConstructionPriceIndex,
        MarketPriceIndex,
        MarketPriceIndex2005Equal100,
        ApartmentMaximumPriceCalculation,
        MigrationDone,
    ]:
        model_class.objects.all().delete()


def create_indices(codes: List[LegacyRow], model_class: type[AbstractIndex]) -> None:
    for code in codes:
        index = model_class()

        code_id = code["code_id"]

        # Convert a few special cases in advance
        if code_id == "000369":
            code_id = "202302"
        elif code_id == "020210":
            code_id = "202103"

        index.value = float(code["value"])
        index.month = str_to_year_month(code_id)

        # Skip indices with '0' values
        if index.value == 0:
            continue

        index.save()


def create_housing_companies(
    connection: Connection, converted_data: ConvertedData, minimal_dataset: bool, regulated_only: bool
) -> dict[int, CreatedHousingCompany]:
    def fetch_housing_companies():
        command = select(companies, additional_infos).join(additional_infos, isouter=True)
        if minimal_dataset:
            # Only migrate a pre-specified set of housing companies e.g. for a testing environment
            logger.info("Running migration with a minimal housing company dataset.")
            ids = (441, 461, 468, 504, 514, 657, 658, 659, 696, 709, 763, 779, 805)
            command = command.where(companies.c.id.in_(ids))
        if regulated_only:
            logger.info("Running migration with only regulated housing companies.")
            command = command.where(companies.c.state_code.in_(("001", "002")))
        return connection.execute(command).fetchall()

    housing_companies_by_id = {}

    for hc in fetch_housing_companies():
        new = HousingCompany()
        new.id = hc[companies.c.id]  # Keep original IDs as archive id
        new.official_name = hc["official_name"]
        new.display_name = hc["display_name"]
        new.exclude_from_statistics = False  # Can be set in the new system
        new.regulation_status = housing_company_regulation_status_from(hc["state_code"])
        new.business_id = ""
        new.street_address = hc["address"]
        new.acquisition_price = hc["acquisition_price"]
        new.primary_loan = hc["primary_loan"]
        new.sales_price_catalogue_confirmation_date = date_to_datetime(hc["sales_price_catalogue_confirmation_date"])
        new.legacy_release_date = date_to_datetime(hc["legacy_release_date"])
        new.notes = combine_notes(hc)
        new.building_type = converted_data.building_types_by_code_number[hc["building_type_code"]]
        new.developer = converted_data.developers_by_code_number[hc["developer_code"]]
        new.postal_code = converted_data.postal_codes_by_postal_code[hc["postal_code_code"]]
        new.financing_method = converted_data.financing_methods_by_code_number[hc["financing_method_code"]]
        new.hitas_type = converted_data.hitas_types_by_code_number[hc["financing_method_code"]]
        new.property_manager = converted_data.property_managers_by_oracle_id[hc["property_manager_id"]]

        # FIXME: this name is in the test dataset file but will be fixed in test/prod environments
        # This is a temporary solution to ignore the only instance of housing companies with non-unique name
        if new.display_name == "Auroranlinna":
            import uuid

            suffix = "-" + str(uuid.uuid4())

            new.display_name += suffix
            new.official_name += suffix

        # Only save postal codes linked to housing companies
        if new.postal_code._state.adding:
            new.postal_code.save()

        new.save()

        addresses = connection.execute(
            select(company_addresses).where(company_addresses.c.company_id == hc["id"])
        ).fetchall()

        housing_companies_by_id[new.id] = CreatedHousingCompany(
            value=new,
            interest_rate=hc["construction_time_interest_rate"],
            addresses={address["street_address"] for address in addresses} | {new.street_address},
        )

    # Update ID sequence as we forced same IDs as Oracle DB had
    max_id = HousingCompany.objects.aggregate(Max("id"))["id__max"]
    with django_connection.cursor() as cursor:
        cursor.execute("ALTER SEQUENCE hitas_housingcompany_id_seq RESTART WITH %s", [max_id + 1])

    logger.info(f"Loaded {len(housing_companies_by_id)} housing companies.\n")

    return housing_companies_by_id


def create_housing_company_improvements(connection: Connection, converted_data: ConvertedData):
    count = 0
    bulk_cpi = []
    bulk_mpi = []

    for company_oracle_id, housing_company in converted_data.created_housing_companies_by_oracle_id.items():
        #
        # Construction price index
        #
        # Get all improvements from all maximum price calculations.
        cpi_improvements = list(
            connection.execute(
                select(construction_price_indices, company_construction_price_indices)
                .join(
                    construction_price_indices,
                    (company_construction_price_indices.c.max_price_index_id == construction_price_indices.c.id),
                )
                .where(construction_price_indices.c.company_id == company_oracle_id)
                .order_by(desc(construction_price_indices.c.calculation_date), desc(construction_price_indices.c.id))
            )
        )
        # Filter improvements to only the latest max price calculation.
        cpi_improvements = [
            i for i in cpi_improvements if i.max_price_index_id == cpi_improvements[0].max_price_index_id
        ]

        for cpi_improvement in cpi_improvements:
            new = HousingCompanyConstructionPriceImprovement(
                housing_company=housing_company.value,
                name=cpi_improvement["name"],
                completion_date=cpi_improvement["completion_date"],
                value=cpi_improvement["value"],
            )
            bulk_cpi.append(new)
            count += 1

        if len(bulk_cpi) >= BULK_INSERT_THRESHOLD:
            HousingCompanyConstructionPriceImprovement.objects.bulk_create(bulk_cpi)
            bulk_cpi = []

        #
        # Market price index
        #
        # Get all improvements from all maximum price calculations.
        mpi_improvements = list(
            connection.execute(
                select(market_price_indices, company_market_price_indices, additional_infos)
                .join(
                    market_price_indices,
                    (company_market_price_indices.c.max_price_index_id == market_price_indices.c.id),
                )
                .join(additional_infos, isouter=True)
                .where(market_price_indices.c.company_id == company_oracle_id)
                .order_by(desc(market_price_indices.c.calculation_date), desc(market_price_indices.c.id))
            )
        )
        # Filter improvements to only the latest max price calculation.
        mpi_improvements = [
            i for i in mpi_improvements if i.max_price_index_id == mpi_improvements[0].max_price_index_id
        ]

        for mpi_improvement in mpi_improvements:
            # Can always be deduced from the improvement name
            no_deductions = mpi_improvement["name"] in [
                "Hissien rakentaminen",
                "Rakennusvirheistä johtuvat korjauskustannukset",
            ]
            if no_deductions:
                improvement_notes = combine_notes(mpi_improvement)
                if improvement_notes:
                    housing_company.value.notes = "\n".join([housing_company.value.notes, improvement_notes])
                    housing_company.value.save()

            new = HousingCompanyMarketPriceImprovement(
                housing_company=housing_company.value,
                name=mpi_improvement["name"],
                completion_date=mpi_improvement["completion_date"],
                value=mpi_improvement["value"],
                no_deductions=no_deductions,
            )
            bulk_mpi.append(new)
            count += 1

        if len(bulk_mpi) >= BULK_INSERT_THRESHOLD:
            HousingCompanyMarketPriceImprovement.objects.bulk_create(bulk_mpi)
            bulk_mpi = []

    if bulk_cpi:
        HousingCompanyConstructionPriceImprovement.objects.bulk_create(bulk_cpi)
    if bulk_mpi:
        HousingCompanyMarketPriceImprovement.objects.bulk_create(bulk_mpi)

    logger.info(f"Loaded {count} housing company improvements.\n")


def create_real_estates_and_buildings(
    housing_company: HousingCompany,
    addresses: set[str],
    connection: Connection,
) -> List[CreatedRealEstate]:
    created_real_estates = []

    for real_estate in connection.execute(
        select(real_estates).where(real_estates.c.company_id == housing_company.id)
    ).fetchall():
        new = RealEstate()
        new.housing_company = housing_company
        new.property_identifier = real_estate["property_identifier"]
        new.save()
        created_real_estates.append(CreatedRealEstate(value=new, buildings=[]))

    buildings: list[CreatedBuilding] = []
    for address in addresses:
        b = Building()
        b.real_estate = created_real_estates[0].value
        b.street_address = address
        b.building_identifier = ""
        b.save()
        buildings.append(CreatedBuilding(value=b))

    created_real_estates[0].buildings = buildings

    return created_real_estates


def create_apartments(
    building: Building, connection: Connection, converted_data: ConvertedData
) -> Dict[int, Apartment]:
    def fetch_payments(connection: Connection, apartment_id: int):
        retval = []
        for payment in connection.execute(
            select(apartment_payments).where(apartment_payments.c.apartment_id == apartment_id)
        ).fetchall():
            retval.append(Payment(date=payment.date, percentage=Decimal(payment.percentage)))
        return retval

    apartments_by_id = {}
    bulk_apartments = []

    for apartment in connection.execute(
        select(apartments, additional_infos)
        .join(additional_infos, isouter=True)
        .where(apartments.c.company_id == building.real_estate.housing_company.id)
    ).fetchall():
        new = Apartment()
        new.building = building
        new.state = ApartmentState.SOLD
        new.apartment_type = converted_data.apartment_types_by_code_number[apartment["apartment_type_code"]]
        new.surface_area = apartment["surface_area"]
        new.street_address = apartment["street_address"]
        new.apartment_number = apartment["apartment_number"]
        new.floor = apartment["floor"]
        new.stair = apartment["stair"]
        new.rooms = apartment["rooms"]
        new.purchase_price = apartment["purchase_price"]
        new.additional_work_during_construction = apartment["additional_work_during_construction"]
        new.loans_during_construction = apartment["loans_during_construction"]

        if apartment["completion_date"]:
            new.interest_during_construction_6 = total_construction_time_interest(
                loan_rate=Decimal(6.0),
                apartment_completion_date=apartment["completion_date"],
                apartment_transfer_price=Decimal(apartment["debt_free_purchase_price"]),
                apartment_loans_during_construction=Decimal(apartment["loans_during_construction"]),
                payments=fetch_payments(connection, apartment["id"]),
            )

            new.interest_during_construction_14 = total_construction_time_interest(
                loan_rate=Decimal(14.0),
                apartment_completion_date=apartment["completion_date"],
                apartment_transfer_price=Decimal(apartment["debt_free_purchase_price"]),
                apartment_loans_during_construction=Decimal(apartment["loans_during_construction"]),
                payments=fetch_payments(connection, apartment["id"]),
            )

        new.debt_free_purchase_price_during_construction = apartment["debt_free_purchase_price_during_construction"]
        new.completion_date = apartment["completion_date"]
        new.notes = combine_notes(apartment)

        if apartment["share_number_start"] != 0 and apartment["share_number_end"] != 0:
            new.share_number_start = apartment["share_number_start"]
            new.share_number_end = apartment["share_number_end"]

        bulk_apartments.append(new)

        if len(bulk_apartments) == BULK_INSERT_THRESHOLD:
            Apartment.objects.bulk_create(bulk_apartments)
            bulk_apartments = []

        apartments_by_id[apartment[apartments.c.id]] = new

    if len(bulk_apartments):
        Apartment.objects.bulk_create(bulk_apartments)

    return apartments_by_id


def create_apartment_improvements(connection: Connection, converted_data: ConvertedData) -> None:  # noqa: C901
    """
    Create improvements for apartments from the latest maximum price calculation that has any improvements
    Detect improvements that are 'Additional work during construction' and move their values to the Apartment model
    """

    def get_latest_improvements(index_table, improvements_table, apartment_oracle_id):
        # Get all calculations that have improvements
        improvements_list = list(
            connection.execute(
                select(index_table, improvements_table)
                .join(
                    index_table,
                    (improvements_table.c.max_price_index_id == index_table.c.id),
                )
                .where(index_table.c.apartment_id == apartment_oracle_id and improvements_table.c.value > 0)
                .order_by(desc(index_table.c.calculation_date), desc(index_table.c.id))
            )
        )

        if not improvements_list:
            return []

        # Only include improvements from the latest max price calculation.
        # Improvements are ignored if they don't have any original value.
        return [
            i
            for i in improvements_list
            if i.max_price_index_id == improvements_list[0].max_price_index_id and i.value > 0
        ]

    def is_date_within_one_month(date1: date, date2: date):
        return abs(date1 - date2).days <= 31

    count = 0
    bulk_cpi = []
    bulk_mpi = []

    for apartment_oracle_id, v in converted_data.apartments_by_oracle_id.items():
        # awdc = Additional Work During Construction
        cpi_awdc = {"improvements": [], "date": None}
        mpi_awdc = {"improvements": [], "date": None}

        #
        # Construction price index improvements
        #

        cpi_improvements = get_latest_improvements(
            construction_price_indices, apartment_construction_price_indices, apartment_oracle_id
        )
        for cpi_improvement in cpi_improvements:
            new = ApartmentConstructionPriceImprovement(
                apartment=v,
                name=cpi_improvement["name"],
                completion_date=cpi_improvement["completion_date"],
                value=cpi_improvement["value"],
                depreciation_percentage=value_to_depreciation_percentage(cpi_improvement["depreciation_percentage"]),
            )

            # Check if CPI improvement value should be moved to apartment.additional_work_during_construction instead
            if (
                # awdc Improvements do not depreciate
                new.depreciation_percentage == DepreciationPercentage.ZERO
                # and is completed at almost the same time as the apartment
                and is_date_within_one_month(new.completion_date, monthify(v.completion_date))
                # and the improvements accepted value should not be less than the original value
                and cpi_improvement["accepted_value"] > cpi_improvement["value"]
            ):
                if new.name == "Ullakkohuoneen rakentaminen":
                    # 'Attic room' improvements are not considered awdc improvements, as they require special handling
                    # The special handling is done only for MPI improvements, but we can't consider CPI as AWDC either
                    pass
                else:
                    cpi_awdc["improvements"].append(new)
                    cpi_awdc["date"] = cpi_improvement.calculation_date
                    continue

            bulk_cpi.append(new)
            count += 1

        if len(bulk_cpi) >= BULK_INSERT_THRESHOLD:
            ApartmentConstructionPriceImprovement.objects.bulk_create(bulk_cpi)
            bulk_cpi = []

        #
        # Market price index improvements
        #

        mpi_improvements = get_latest_improvements(
            market_price_indices, apartment_market_price_indices, apartment_oracle_id
        )
        for mpi_improvement in mpi_improvements:
            new = ApartmentMarketPriceImprovement(
                apartment=v,
                name=mpi_improvement["name"],
                completion_date=mpi_improvement["completion_date"],
                value=mpi_improvement["value"],
            )

            # Check if improvement value should be moved to apartment.additional_work_during_construction instead
            if (
                # awdc Improvements have no excess
                mpi_improvement["excess"] == "000"
                # and is completed at almost the same time as the apartment
                and is_date_within_one_month(new.completion_date, monthify(v.completion_date))
                # and the improvements accepted value should not be less than the original value
                and mpi_improvement["accepted_value"] >= mpi_improvement["value"]
            ):
                if new.name == "Ullakkohuoneen rakentaminen":
                    # 'Attic room' improvements are not considered awdc improvements, as they require special handling
                    new.no_deductions = True
                else:
                    mpi_awdc["improvements"].append(new)
                    mpi_awdc["date"] = mpi_improvement.calculation_date
                    continue

            bulk_mpi.append(new)
            count += 1
        if len(bulk_mpi) >= BULK_INSERT_THRESHOLD:
            ApartmentMarketPriceImprovement.objects.bulk_create(bulk_mpi)
            bulk_mpi = []

        #
        # Additional work during construction improvements
        #

        # One index improvements may contain the same improvements, but they are split into multiple separate
        # improvements, so we need to compare the sums of both indices and if they match the sum value can be moved.
        sum_cpi = sum(i.value for i in cpi_awdc["improvements"])
        sum_mpi = sum(i.value for i in mpi_awdc["improvements"])
        awdc = 0

        if sum_cpi == sum_mpi or sum_cpi == 0 or sum_mpi == 0:
            # CPI and MPI sums match, or one index is missing is completely.
            awdc = max(sum_cpi, sum_mpi)
        elif cpi_awdc["date"] != mpi_awdc["date"]:
            # Mismatch on index improvement sums, use the latest calculation instead as its most up to date.
            if cpi_awdc["date"] > mpi_awdc["date"]:
                awdc = sum_cpi
            else:
                awdc = sum_mpi
        else:
            # Unable to convert improvements automatically.
            # Print out and add them as normal improvements to be handled manually later.
            bulk_cpi.extend(cpi_awdc["improvements"])
            bulk_mpi.extend(mpi_awdc["improvements"])
            logger.info(
                f"Unhandled 'Additional work during construction' improvement, adding it as a regular improvement:\n"
                f"{v.housing_company.id}, {v.housing_company.display_name}\n"
                f"{apartment_oracle_id}, {v.address}, Calculation: {cpi_awdc['date']}\n"
                f"RKI, {sum_cpi} €, {[str(i) for i in cpi_awdc['improvements']]}\n"
                f"MHI, {sum_mpi} €, {[str(i) for i in mpi_awdc['improvements']]}\n"
            )

        v.additional_work_during_construction = v.additional_work_during_construction + awdc
        v.save()

    if bulk_cpi:
        ApartmentConstructionPriceImprovement.objects.bulk_create(bulk_cpi)
    if bulk_mpi:
        ApartmentMarketPriceImprovement.objects.bulk_create(bulk_mpi)

    logger.info(f"Loaded {count} apartment improvements.\n")


def create_owners_and_ownerships(connection: Connection, converted_data: ConvertedData) -> None:
    def get_all_current_ownerships() -> list[apartment_ownerships]:
        return connection.execute(
            # As some apartments have duplicate owners, we can't simply select all owners, and instead
            # we need to `group_by` owners to remove duplicates, and sum any percentages of the duplicate ownerships.
            select(
                [
                    apartment_ownerships.c.apartment_id,
                    func.coalesce(apartment_ownerships.c.name, "Ei tiedossa").label("name"),
                    apartment_ownerships.c.social_security_number,
                    func.sum(apartment_ownerships.c.percentage).label("percentage"),
                ]
            )
            .group_by(
                apartment_ownerships.c.apartment_id,
                apartment_ownerships.c.name,
                apartment_ownerships.c.social_security_number,
            )
            .where(apartment_ownerships.c.apartment_id != 0)
        ).fetchall()

    def create_owner(_ownership: apartment_ownerships) -> tuple[Owner, bool]:
        nonlocal count
        identifier: Optional[str] = _ownership["social_security_number"]
        if identifier:
            identifier = identifier.upper()

        _new_owner = Owner(
            name=_ownership["name"],
            identifier=identifier,
            valid_identifier=check_social_security_number(identifier) or check_business_id(identifier),
        )

        # Check if this owner has been already added (has the same valid identifier).
        # If it is, do not create a new one but combine them into one.
        if _new_owner.valid_identifier:
            key = _new_owner.identifier
            if key in already_created:
                return already_created[key], True
            already_created[key] = _new_owner

        bulk_owners.append(_new_owner)
        count += 1
        return _new_owner, False

    count = 0
    bulk_owners: list[Owner] = []
    already_created: dict[str, Owner] = {}
    converted_data.current_ownerships_by_oracle_apartment_id = {}

    for ownership in get_all_current_ownerships():
        # Skip importing ownership if the apartment has not been imported
        if not converted_data.apartments_by_oracle_id.get(ownership["apartment_id"]):
            continue

        new_owner, duplicate = create_owner(ownership)
        if duplicate:
            # Take care of cases where same apartment has owners with the same identifier but different name.
            # These are errors, but should be combined into one ownership for now.
            this_apartment_owners: list[Ownership] = converted_data.current_ownerships_by_oracle_apartment_id.get(
                ownership["apartment_id"], []
            )
            combined: bool = False
            for _ownership in this_apartment_owners:
                if _ownership.owner.identifier == new_owner.identifier:
                    logger.info("Error: Duplicate owner with same identifier but different name. Combining them...")
                    _ownership.percentage += ownership["percentage"]
                    combined = True
                    break
            if combined:
                continue

        new = Ownership(
            owner=new_owner,
            percentage=ownership["percentage"],
        )

        # Save ownerships for sale creation
        converted_data.current_ownerships_by_oracle_apartment_id.setdefault(ownership["apartment_id"], [])
        converted_data.current_ownerships_by_oracle_apartment_id[ownership["apartment_id"]].append(new)

        if len(bulk_owners) == BULK_INSERT_THRESHOLD:
            Owner.objects.bulk_create(bulk_owners)
            bulk_owners = []

    if len(bulk_owners):
        Owner.objects.bulk_create(bulk_owners)

    converted_data.owners = already_created
    logger.info(f"Loaded {count} owners.\n")


def create_apartment_max_price_calculations(connection: Connection, converted_data: ConvertedData) -> None:
    for mpc in (
        connection.execute(select(construction_price_indices)).fetchall()
        + connection.execute(select(market_price_indices)).fetchall()
    ):
        if mpc["apartment_id"] not in converted_data.apartments_by_oracle_id:
            continue

        ApartmentMaximumPriceCalculation.objects.create(
            apartment=converted_data.apartments_by_oracle_id[mpc["apartment_id"]],
            created_at=date_to_datetime(mpc["last_modified"]),
            confirmed_at=date_to_datetime(mpc["last_modified"]),
            calculation_date=mpc["calculation_date"],
            valid_until=mpc["calculation_date"] + relativedelta(months=3),
            maximum_price=mpc["max_price"],
            json=None,
            json_version=None,
        )


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

    logger.info(f"Loaded {len(property_managers_by_id)} property managers.\n")

    return property_managers_by_id


def create_users(connection: Connection) -> Dict[str, Dict[str, get_user_model()]]:
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

    logger.info(f"Loaded {len(users_by_id)} users.\n")

    return users_by_id


def create_unsaved_postal_codes(codes: List[LegacyRow]) -> Dict[str, HitasPostalCode]:
    retval = {}

    for code in codes:
        postal_code = HitasPostalCode()

        postal_code.value = code["code_id"]
        postal_code.city = code["value"].capitalize()
        postal_code.cost_area = hitas_cost_area(code["code_id"])

        retval[postal_code.value] = postal_code

    return retval


def read_codebooks(connection: Connection) -> Dict[str, List[LegacyRow]]:
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

    logger.info(f"Loaded {len(codebooks_by_id)} codebooks with total of {total_codes} codes.\n")

    return codebooks_by_id


T = TypeVar("T", bound=AbstractCode)


def create_codes(
    codes: List[LegacyRow], fn: Callable[[], T], modify_fn: Callable[[T], None] = None, sensitive: bool = False
) -> Dict[str, T]:
    retval = {}

    for code in codes:
        new = fn()

        if sensitive and should_anonymize():
            new.value = faker().company()
        else:
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


def create_hitas_types(financing_methods: List[LegacyRow]) -> dict[str, HitasType]:
    hitas_types_by_code_number: dict[str, HitasType] = {}

    for financing_method in financing_methods:
        financing_method_name = strip_financing_method_id(financing_method["value"])
        hitas_type = FINANCING_METHOD_TO_HITAS_TYPE_MAP[financing_method_name]
        hitas_types_by_code_number[financing_method["code_id"]] = hitas_type

    return hitas_types_by_code_number


# @prints_to_file("log.txt")
def create_apartment_sales(connection: Connection, converted_data: ConvertedData) -> None:  # noqa: C901
    def get_oracle_apartment(_apartment_oracle_id: int) -> apartments:
        return connection.execute(select(apartments).where(apartments.c.id == _apartment_oracle_id)).first()

    def get_all_apartment_sales(_apartment_oracle_id: int) -> list[hitas_monitoring]:
        """Fetch all sales for given apartment"""
        return list(
            connection.execute(
                select(hitas_monitoring)
                .where(hitas_monitoring.c.apartment_id == _apartment_oracle_id)
                .where(
                    hitas_monitoring.c.monitoring_state.in_(
                        (
                            ApartmentSaleMonitoringState.ACTIVE.value,
                            ApartmentSaleMonitoringState.COMPLETE.value,
                            ApartmentSaleMonitoringState.RELATIVE_SALE.value,
                        )
                    )
                )
                .order_by(desc(hitas_monitoring.c.purchase_date), desc(hitas_monitoring.c.id))
            )
        )

    def create_ownerships_for_buyers(_oracle_sale: hitas_monitoring, _sale: ApartmentSale) -> list[Ownership]:
        """Get buyers (Owner) from already converted data, or create new ones."""
        _buyers: dict[OwnerKey, Owner] = {}

        # Handle both Buyer 1 and Buyer 2
        for i in ["1", "2"]:
            name = _oracle_sale["buyer_name_" + i]

            # Owner is unknown, can be skipped
            if not name or name == "Ei tiedossa":
                continue

            name = name.replace("\x00", "")
            name = strip_percentage(name)

            identifier: Optional[str] = _oracle_sale["buyer_identifier_" + i]
            if identifier is not None:
                identifier = identifier.upper()

            new_owner = Owner(
                name=name,
                identifier=identifier,
                valid_identifier=check_social_security_number(identifier) or check_business_id(identifier),
            )

            # Check if this owner has been already added (has the same valid identifier).
            # If it is, do not create a new one but combine them into one.
            if new_owner.valid_identifier:
                key = new_owner.identifier
                if key in converted_data.owners:
                    new_owner = converted_data.owners[key]
                else:
                    converted_data.owners[key] = new_owner
                    bulk_owners.append(new_owner)
            else:
                bulk_owners.append(new_owner)

            owner_key = OwnerKey(new_owner.identifier, new_owner.name)
            if owner_key in _buyers:
                logger.info("Duplicate buyer found in sale, skipping.")
                continue

            _buyers[owner_key] = new_owner

        return [
            Ownership(
                owner=_buyer,
                sale=_sale,
                # Assume equal split, as there is no way to know the real percentages
                percentage=100 / len(_buyers),
                # Old sale, so ownership is deleted
                deleted=timezone.now(),
            )
            for _buyer in _buyers.values()
        ]

    count = 0
    error_1 = 0
    error_2 = 0
    error_3 = 0
    error_4 = 0
    error_5 = 0
    error_6 = 0
    note_1 = 0
    note_2 = 0
    note_3 = 0
    note_4 = 0
    note_5 = 0
    note_6 = 0
    note_7 = 0
    note_8 = 0
    today = date.today()
    year_ago = today - relativedelta(years=1)
    bulk_apartment_sales: list[ApartmentSale] = []
    bulk_owners: list[Owner] = []
    bulk_ownerships: list[Ownership] = []

    for apartment_oracle_id, apartment in converted_data.apartments_by_oracle_id.items():
        oracle_apartment = get_oracle_apartment(apartment_oracle_id)
        oracle_sales = get_all_apartment_sales(apartment_oracle_id)
        latest_owners = converted_data.current_ownerships_by_oracle_apartment_id.pop(apartment_oracle_id, None)

        sales: dict[tuple[int, date], ApartmentSale] = {}
        ownerships: dict[int, list[Ownership]] = {}

        logger.debug("----------------------------------------------------------------------------------------\n")
        logger.debug(
            f"Housing company: ({apartment.housing_company.id})\n"
            f"  | display_name={apartment.housing_company.display_name}\n"
            f"  | regulation_status={apartment.housing_company.regulation_status.value}\n"
            f"  | hitas_type={apartment.housing_company.hitas_type.value}"
        )
        logger.debug(
            f"Apartment: ({apartment_oracle_id})\n"
            f"  | address={apartment.address}\n"
            f"  | completion_date={oracle_apartment['completion_date']}\n"
            f"  | first_purchase_date={oracle_apartment['first_purchase_date']}\n"
            f"  | latest_purchase_date={oracle_apartment['latest_purchase_date']}\n"
            f"  | first_sale_purchase_price={oracle_apartment['debt_free_purchase_price']}\n"
            f"  | first_sale_loan_amount={oracle_apartment['primary_loan_amount']}"
        )
        logger.debug(f"Current ownerships: {latest_owners}")
        logger.debug(f"Number of Sales: {len(oracle_sales)}\n")

        for num, oracle_sale in enumerate(oracle_sales):
            logger.debug(
                f"  {num + 1}) Sale: ({oracle_sale['id']})\n"
                f"    | purchase_date={oracle_sale['purchase_date']}\n"
                f"    | buyer1={oracle_sale['buyer_name_1']}\n"
                f"    | buyer2={oracle_sale['buyer_name_2']}\n"
                f"    | purchase_price={oracle_sale['purchase_price']}\n"
                f"    | loan_amount={oracle_sale['apartment_share_of_housing_company_loans']}\n"
                f"    | monitoring_state={ApartmentSaleMonitoringState(oracle_sale['monitoring_state'])}\n"
                f"    | seller={oracle_sale['seller_name']}\n"
                f"    | maximum_price={oracle_sale['maximum_price']}\n"
                f"    | calculation_date={oracle_sale['calculation_date']}\n"
                f"    | notification_date={oracle_sale['notification_date']}"
            )

            # Skip any calculations with missing buyer or purchase date, as it is most likely
            # only a calculation, and couldn't be imported anyway due to missing data.
            # The only exception to this rule is the latest calculation (the active one).
            if oracle_sale["monitoring_state"] != ApartmentSaleMonitoringState.ACTIVE.value and (
                not oracle_sale["purchase_date"]
                or not oracle_sale["buyer_name_1"]
                or oracle_sale["buyer_name_1"] == "Ei tiedossa"
            ):
                alt_date: Optional[date] = (
                    oracle_sale["purchase_date"] or oracle_sale["calculation_date"] or oracle_sale["notification_date"]
                )
                if alt_date and alt_date >= year_ago:
                    note_1 += 1
                    note_6 += 1
                    logger.debug(
                        "\nNote 1! Non-active sale does not have purchase date or buyer information."
                        "\nNote 6! Skipping recent sale!\n"
                    )
                else:
                    logger.debug("\nNote 1! Non-active sale does not have purchase date or buyer information.\n")
                    note_1 += 1
                continue

            # Last active calculation can use latest sale date if it's missing purchase date,
            # and the calculation is still valid.
            if (
                oracle_sale["monitoring_state"] == ApartmentSaleMonitoringState.ACTIVE.value
                and not oracle_sale["purchase_date"]
            ):
                purchase_date: Optional[date] = oracle_apartment["latest_purchase_date"]
                alt_date: Optional[date] = oracle_sale["calculation_date"] or oracle_sale["notification_date"]

                if not purchase_date:
                    if alt_date is not None and alt_date >= year_ago:
                        note_4 += 1
                        note_6 += 1
                        logger.debug(
                            "\nNote 4! No latest purchase date. Can't determine if active calculation is valid."
                            "\nNote 6! Skipping recent sale!\n"
                        )
                    else:
                        note_4 += 1
                        logger.debug(
                            "\nNote 4! No latest purchase date. Can't determine if active calculation is valid.\n"
                        )
                    continue

                if not alt_date:
                    logger.debug(
                        "\nNote 3! No calculation date or notification date. "
                        "Can't determine if active calculation is valid.\n"
                    )
                    note_3 += 1
                    continue

                # Check if the calculation was at valid the last time apartment was sold.
                # 4 Months is the longest a calculation can be active (when using Surface Area Price Ceiling)
                if not (alt_date <= purchase_date <= (alt_date + relativedelta(months=4))):
                    if alt_date >= year_ago:
                        note_2 += 1
                        note_6 += 1
                        logger.debug("\nNote 2! Active calculation not valid anymore.\nNote 6! Skipping recent sale!\n")
                    else:
                        logger.debug("\nNote 2! Active calculation not valid anymore.\n")
                        note_2 += 1
                    continue

                # If purchase price is missing, the price is almost certainly missing as well.
                purchase_price = oracle_sale["purchase_price"]
                apartment_share_of_housing_company_loans = oracle_sale["apartment_share_of_housing_company_loans"]
                exclude_from_statistics = False
                if not purchase_price:
                    note_5 += 1
                    logger.debug("\nNote 5! Purchase price missing, creating sale with purchase price of 1.")
                    if purchase_date >= year_ago:
                        error_2 += 1
                        logger.debug(
                            "\nError 2! Creating a sale from active sale without purchase price that is recent."
                        )

                    purchase_price = 1
                    apartment_share_of_housing_company_loans = 0
                    exclude_from_statistics = True

                if purchase_date >= year_ago:
                    logger.debug("\nNote 7: Creating a sale from active calculation that is quite recent.\n")
                    note_7 += 1

                sale = ApartmentSale(
                    apartment=apartment,
                    notification_date=oracle_sale["notification_date"],
                    purchase_date=purchase_date,
                    purchase_price=purchase_price,
                    apartment_share_of_housing_company_loans=apartment_share_of_housing_company_loans,
                    exclude_from_statistics=exclude_from_statistics,
                )
                sales[(oracle_sale["id"], sale.purchase_date)] = sale
                count += 1

                logger.debug(
                    f"    -> Created a sale for an active calculation without purchase date "
                    f"using apartment latest purchase date {purchase_date}\n"
                )

                ownerships[oracle_sale["id"]] = create_ownerships_for_buyers(oracle_sale, sale)
                continue

            # Normal logic for sales that have all the necessary data.
            sale = ApartmentSale(
                apartment=apartment,
                notification_date=oracle_sale["notification_date"],
                purchase_date=oracle_sale["purchase_date"],
                purchase_price=oracle_sale["purchase_price"],
                apartment_share_of_housing_company_loans=oracle_sale["apartment_share_of_housing_company_loans"],
                exclude_from_statistics=(
                    oracle_sale["monitoring_state"] == ApartmentSaleMonitoringState.RELATIVE_SALE.value
                    or oracle_sale["purchase_price"] == 0
                ),
            )
            sales[(oracle_sale["id"], sale.purchase_date)] = sale
            count += 1

            logger.debug("    -> Created a sale using normal logic\n")

            ownerships[oracle_sale["id"]] = create_ownerships_for_buyers(oracle_sale, sale)

        # All sales related for an apartment have now been created.
        # Check against apartment data to see if first and latest sale need to be created.
        #
        # If there aren't any sales on the first purchase date, then one must be created.
        # Assume that this sale will have the earliest purchase date.
        if oracle_apartment["first_purchase_date"] and not any(
            sale.purchase_date == oracle_apartment["first_purchase_date"] for sale in sales.values()
        ):
            sale = ApartmentSale(
                apartment=apartment,
                notification_date=oracle_apartment["first_purchase_date"],
                purchase_date=oracle_apartment["first_purchase_date"],
                purchase_price=oracle_apartment["debt_free_purchase_price"],
                apartment_share_of_housing_company_loans=oracle_apartment["primary_loan_amount"],
                exclude_from_statistics=False,
            )
            sales[(-sys.maxsize + 1, sale.purchase_date)] = sale
            count += 1
            logger.debug("  -> Created first sale based on apartment data.\n")
        elif oracle_apartment["first_purchase_date"]:
            logger.debug("  First sale already exists.\n")

        # If there aren't any sales on the latest purchase date, then one must be created.
        # Assume that this sale will have the latest purchase date.
        if oracle_apartment["latest_purchase_date"] and not any(
            sale.purchase_date == oracle_apartment["latest_purchase_date"] for sale in sales.values()
        ):
            if oracle_apartment["latest_purchase_date"] >= year_ago:
                logger.debug("Note 8: Creating latest sale from apartment data that is quite recent.")
                note_8 += 1

            sale = ApartmentSale(
                apartment=apartment,
                notification_date=oracle_apartment["latest_purchase_date"],
                purchase_date=oracle_apartment["latest_purchase_date"],
                purchase_price=1,  # There is no way to get the actual value
                apartment_share_of_housing_company_loans=0,  # There is no way to get the actual value
                exclude_from_statistics=True,  # Since the price is hardcoded to 1, exclude sale automatically
            )
            sales[(sys.maxsize - 1, sale.purchase_date)] = sale
            count += 1
            logger.debug("  -> Created latest sale based on apartment data.\n")
        elif oracle_apartment["latest_purchase_date"]:
            logger.debug("  Latest sale already exists.\n")

        # These apartments have had owner changes without sales, e.g., with sales catalog checks, etc.
        # Should create a 1 priced sale that is excluded from statistics.
        if apartment_oracle_id in APARTMENTS_WITH_OWNER_CHANGES_WITHOUT_SALES:
            if oracle_apartment["latest_purchase_date"] >= year_ago:
                logger.debug("Note 8: Creating latest sale from apartment data that is quite recent.")
                note_8 += 1

            sale = ApartmentSale(
                apartment=apartment,
                notification_date=oracle_apartment["latest_purchase_date"],
                purchase_date=oracle_apartment["latest_purchase_date"],
                purchase_price=1,  # There is no way to get the actual value
                apartment_share_of_housing_company_loans=0,  # There is no way to get the actual value
                exclude_from_statistics=True,  # Since the price is hardcoded to 1, exclude sale automatically
            )
            sales[(sys.maxsize, sale.purchase_date)] = sale
            count += 1
            logger.debug(
                "  -> Created latest sale based on apartment data for apartment with owner changes without a sale.\n"
            )

        # If there are no sales, the apartment might have sales catalog prices
        if not sales:
            if (
                latest_owners
                and len(latest_owners) == 1
                and latest_owners[0].owner.name
                in (
                    "Helsingin kaupunki",
                    "Helsingin Kaupunki",
                    "Helsingin Asuntohankinta",
                )
            ):
                if not oracle_apartment["completion_date"]:
                    error_6 += 1
                    logger.debug(
                        "Error 6! Completion date missing, cannot create sale for apartment "
                        "owned by Helsinki City on its completion date.\n"
                    )
                else:
                    sale = ApartmentSale(
                        apartment=apartment,
                        notification_date=oracle_apartment["completion_date"],
                        purchase_date=oracle_apartment["completion_date"],
                        purchase_price=oracle_apartment["debt_free_purchase_price"],
                        apartment_share_of_housing_company_loans=oracle_apartment["primary_loan_amount"],
                        exclude_from_statistics=True,
                    )
                    sales[(sys.maxsize, sale.purchase_date)] = sale
                    count += 1
                    logger.debug("  -> Created sale for apartment owner by Helsinki City on its completion date.\n")

            elif latest_owners:
                error_1 += 1
                logger.debug(
                    f"Error 1! Apartment does not have any sales, "
                    f"but it has owners for some reason... "
                    f"Updating sales catalog prices and ignoring owners!\n"
                    f"Owners: {latest_owners}\n"
                )
            else:
                logger.debug("Apartment does not have any sales. Updating sales catalog prices.\n")

            apartment.catalog_purchase_price = oracle_apartment["debt_free_purchase_price"]
            apartment.catalog_primary_loan_amount = oracle_apartment["primary_loan_amount"]
            apartment.save()
            continue

        # Sort sales by purchase date and oracle id, from oldest to newest
        sorted_sales = sorted(sales.items(), key=lambda s: (s[0][1], s[0][0]))
        (first_sale_oracle_id, _), first_sale = next(iter(sorted_sales))
        (latest_sale_oracle_id, _), latest_sale = next(reversed(sorted_sales))

        logger.debug(
            f"First Sale ({first_sale_oracle_id}):\n"
            f"  | purchase_date={first_sale.purchase_date}\n"
            f"  | purchase_price={first_sale.purchase_price}\n"
            f"  | loan_amount={first_sale.apartment_share_of_housing_company_loans}\n"
            f"  | owners: {ownerships.get(first_sale_oracle_id)}"
        )
        logger.debug(
            f"Latest Sale ({latest_sale_oracle_id}):\n"
            f"  | purchase_date={latest_sale.purchase_date}\n"
            f"  | purchase_price={latest_sale.purchase_price}\n"
            f"  | loan_amount={latest_sale.apartment_share_of_housing_company_loans}\n"
            f"  | owners: {ownerships.get(latest_sale_oracle_id)}\n"
        )

        # Check that latest sale purchase price and loans amount match apartment details
        if first_sale.purchase_price != oracle_apartment["debt_free_purchase_price"]:
            logger.debug(
                f"Updated first sale purchase price from "
                f"{first_sale.purchase_price} to {oracle_apartment['debt_free_purchase_price']}\n"
            )
            first_sale.purchase_price = oracle_apartment["debt_free_purchase_price"]

        if first_sale.apartment_share_of_housing_company_loans != oracle_apartment["primary_loan_amount"]:
            logger.debug(
                f"Updated first sale apartment share of housing company loans from "
                f"{first_sale.apartment_share_of_housing_company_loans} to {oracle_apartment['primary_loan_amount']}\n"
            )
            first_sale.apartment_share_of_housing_company_loans = oracle_apartment["primary_loan_amount"]

        if not latest_owners:
            # Owners from sale might not be empty, but should be...
            if ownerships:
                logger.debug(f"Error 4! Apartment does not have latest owners, but sale does: {ownerships}\n")
                error_4 += 1
                continue
            logger.debug("Error 3! Apartment does not have any latest owners.\n")
            error_3 += 1
            continue

        # Current ownerships should be added to the latest sale
        for ownership in latest_owners:
            ownership.sale = latest_sale

        owners_at_sale: set[OwnerKey] = {
            OwnerKey(identifier=ownership.owner.identifier or "", name=strip_percentage(ownership.owner.name or ""))
            for ownership in ownerships.get(latest_sale_oracle_id, [])
        }
        current_owners: set[OwnerKey] = {
            OwnerKey(identifier=ownership.owner.identifier or "", name=strip_percentage(ownership.owner.name or ""))
            for ownership in latest_owners
        }
        if owners_at_sale and owners_at_sale != current_owners:
            # Try to categorize changes to determine if there are "bad" owner changes
            current_identifiers = {owner.identifier for owner in current_owners}
            identifiers_at_sale = {owner.identifier for owner in owners_at_sale}
            current_names = {owner.name for owner in current_owners}
            names_at_sale = {owner.name for owner in owners_at_sale}

            # This can happen in if:
            # - Owner name is not the same as at the time of sale, e.g. changed name, used some other name, typo
            # - Sale data can only include two buyers, but there are more
            # - Original buyers have given parts of their ownership to their relatives, e.g. their children
            if current_identifiers.issuperset(identifiers_at_sale):
                logger.debug(
                    "Latest sale owners changed, but all identifiers of the owners at sale "
                    "are included in the current owners, which is allowed.\n"
                    f"     {owners_at_sale}\n"
                    f"  -> {current_owners}\n"
                )

            # This can happen in if:
            # - Some people have given up their share of the house from the time of purchase, e.g. divorce
            elif identifiers_at_sale.issuperset(current_identifiers):
                logger.debug(
                    "Latest sale owners changed, but all identifiers of the current owners "
                    "are included in the owners at the time of sale, which is allowed.\n"
                    f"     {owners_at_sale}\n"
                    f"  -> {current_owners}\n"
                )

            # This can happen if:
            # - Owner identifier is not the same as at the time of sale, e.g. identifier corrected or removed
            elif current_names.issuperset(names_at_sale):
                logger.debug(
                    "Latest sale owners changed, but all names of the current owners "
                    "are included in the owners at the time of sale, which is allowed.\n"
                    f"     {owners_at_sale}\n"
                    f"  -> {current_owners}\n"
                )

            # This can happen if:
            # - There are some cases where identifiers differ by one letter.
            #   This can be considered a typo, and should be allowed.
            elif least_similar_identifier(current_owners, owners_at_sale) > 0.9:
                logger.debug(
                    "Latest sale owners changed, but it seems like there is a typo of one letter in "
                    "one or more of the identifiers, so trust that the typo was fixed in the current owners.\n"
                    f"     {owners_at_sale}\n"
                    f"  -> {current_owners}\n"
                )

            # Keep a list of apartment whose latest sales have been looked through and changes allowed.
            elif apartment_oracle_id in APARTMENTS_WITH_ALLOWED_OWNER_CHANGES:
                logger.debug(
                    "Latest sale owners changed, but these changes have been approved already.\n"
                    f"     {owners_at_sale}\n"
                    f"  -> {current_owners}\n"
                )

            # These changes and should be looked at
            else:
                logger.debug(
                    f"Error 5: Latest sale owners changed unexpectedly!"
                    f"\n     {owners_at_sale}"
                    f"\n  -> {current_owners}\n"
                )
                error_5 += 1

        ownerships[latest_sale_oracle_id] = latest_owners

        bulk_apartment_sales += list(sales.values())
        bulk_ownerships += [ownership for sale_ownerships in ownerships.values() for ownership in sale_ownerships]

        if max(len(bulk_apartment_sales), len(bulk_owners), len(bulk_ownerships)) >= BULK_INSERT_THRESHOLD:
            ApartmentSale.objects.bulk_create(bulk_apartment_sales)
            Owner.objects.bulk_create(bulk_owners)
            Ownership.objects.bulk_create(bulk_ownerships)
            bulk_apartment_sales = []
            bulk_owners = []
            bulk_ownerships = []

    if len(bulk_apartment_sales) or len(bulk_owners) or len(bulk_ownerships):
        ApartmentSale.objects.bulk_create(bulk_apartment_sales)
        Owner.objects.bulk_create(bulk_owners)
        Ownership.objects.bulk_create(bulk_ownerships)

    logger.info("\n----------------------------------------------------------------------------------------\n\n")
    logger.info(f"Loaded {count} apartment sales.")
    logger.info(f"- Error 1: {error_1} apartments do not have any sales, but they do have current owners.")
    logger.info(f"- Error 2: {error_2} recent sales created from active calculation without purchase price.")
    logger.info(f"- Error 3: {error_3} apartments do not have any current owners.")
    logger.info(f"- Error 4: {error_4} apartments do not have any current owners, but their sales do.")
    logger.info(f"- Error 5: {error_5} apartments had their current owners changed unexpectedly.")
    logger.info(
        f"- Error 6: {error_6} apartments do not have any sales, but they do have current owners (Helsinki City)."
    )
    logger.info(f"- Note 1: {note_1} sales skipped due to missing purchase date or buyer information (not active).")
    logger.info(f"- Note 2: {note_2} sales skipped due to an active calculation not being valid anymore.")
    logger.info(
        f"- Note 3: {note_3} sales skipped since we cannot check if active calculation is active "
        f"due to missing sale calculation and notification date."
    )
    logger.info(
        f"- Note 4: {note_4} sales skipped since we cannot check if active calculation is active "
        f"due to missing apartment latest sale date."
    )
    logger.info(f"- Note 5: {note_5} cases where active calculation is zero-priced.")
    logger.info(f"- Note 6: {note_6} sales skipped that are recent enough to affect regulations.")
    logger.info(
        f"- Note 7: {note_7} sales created from active calculation that are recent enough to affect regulations."
    )
    logger.info(
        f"- Note 8: {note_7} zero priced sales created from latest purchase date "
        f"that are recent enough to affect regulations."
    )

    if converted_data.current_ownerships_by_oracle_apartment_id:
        logger.info("- Ownerships not used:")
        for apartment_oracle_id, ownerships in converted_data.current_ownerships_by_oracle_apartment_id.items():
            apartment = converted_data.apartments_by_oracle_id[apartment_oracle_id]
            ownerships_print = ", ".join((f"({ownership})" for ownership in ownerships))
            logger.info(
                f"  - apartment: ({apartment_oracle_id}) '{apartment.address}', "
                f"housing company: '{apartment.housing_company}', "
                f"ownerships: {ownerships_print}"
            )
    else:
        logger.info("- All current ownerships used!")
    logger.info("\n")


def least_similar_identifier(current_owners: set[OwnerKey], owners_at_sale: set[OwnerKey]) -> float:
    identifier_similarities: set[float] = {1.0}

    for current in current_owners:
        # If current ownership is missing identifier, it is likely we won't find similar
        # identifiers, or the match will be a false positive, so skip it
        if not current.identifier:
            continue

        max_similarity = 0.0
        for at_sale in owners_at_sale:
            # If the owner is the same, but identifier was missing at the time of sale,
            # it might have been corrected to current owners. This should be ok.
            if current.name == at_sale.name and not at_sale.identifier:
                similarity = 1.0
            else:
                similarity = SequenceMatcher(None, current.identifier, at_sale.identifier).ratio()

            if similarity > max_similarity:
                max_similarity = similarity

        identifier_similarities.add(max_similarity)

    return min(identifier_similarities)


def strip_percentage(name: str) -> str:
    strip_percentages_pattern = re.compile(r"^(?P<name>.+)\(\d+(?:,?\d+)?\s*%\)\s*$")
    match = re.match(strip_percentages_pattern, name)
    if match:
        name = match.group("name").strip()
    return name


def remove_apartments_owned_by_housing_companies() -> None:
    ownerships = (
        Ownership.objects.select_related(
            "owner",
            "sale__apartment",
        )
        .prefetch_related(
            # Prefetch only the last sale
            Prefetch(
                "sale__apartment__sales",
                ApartmentSale.objects.filter(
                    id__in=Subquery(
                        ApartmentSale.objects.filter(apartment_id=OuterRef("apartment_id"))
                        .order_by("-purchase_date", "-id")
                        .values_list("id", flat=True)[:1]
                    )
                ),
            ),
        )
        .filter(
            owner__name__in=[
                "Yhtiön hallinnassa",
                "TYhtiön hallinnassa",
                "Yhtiön omistuksessa",
                "Taloyhtiön hallintaan jäävä huoneisto",
                "Huoltomiehen asunto",
                "Talonmiehen asunto",
                "( Talonmies )",
                "Talonmies",
            ],
        )
        .all()
    )
    to_remove: set[Apartment] = set()
    for ownership in ownerships:
        if ownership.sale.apartment.sales.all()[0] == ownership.sale:
            to_remove.add(ownership.apartment)

    for apartment in to_remove:
        apartment.delete(force_policy=HARD_DELETE)

    logger.info(f"Deleted {len(to_remove)} apartments owned by housing companies.\n")
