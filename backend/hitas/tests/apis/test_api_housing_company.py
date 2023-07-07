import datetime
from datetime import date
from decimal import Decimal
from typing import Any, Optional

import pytest
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status

from hitas import exceptions
from hitas.models import (
    Apartment,
    Building,
    BuildingType,
    ConditionOfSale,
    Developer,
    HitasPostalCode,
    HousingCompany,
    HousingCompanyConstructionPriceImprovement,
    HousingCompanyMarketPriceImprovement,
    PropertyManager,
    RealEstate,
)
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.models.thirty_year_regulation import (
    FullSalesData,
    RegulationResult,
    ThirtyYearRegulationResults,
    ThirtyYearRegulationResultsRow,
)
from hitas.services.audit_log import last_log
from hitas.tests.apis.helpers import HitasAPIClient, parametrize_invalid_foreign_key
from hitas.tests.factories import (
    ApartmentFactory,
    BuildingFactory,
    BuildingTypeFactory,
    ConditionOfSaleFactory,
    DeveloperFactory,
    HitasPostalCodeFactory,
    HousingCompanyConstructionPriceImprovementFactory,
    HousingCompanyFactory,
    HousingCompanyMarketPriceImprovementFactory,
    PropertyManagerFactory,
    RealEstateFactory,
)

# List tests


@pytest.mark.django_db
def test__api__housing_company__list__empty(api_client: HitasAPIClient):
    response = api_client.get(reverse("hitas:housing-company-list"))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == []
    assert response.json()["page"] == {
        "size": 0,
        "current_page": 1,
        "total_items": 0,
        "total_pages": 1,
        "links": {
            "next": None,
            "previous": None,
        },
    }


@pytest.mark.django_db
def test__api__housing_company__list(api_client: HitasAPIClient, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    hc1: HousingCompany = HousingCompanyFactory.create()
    hc2: HousingCompany = HousingCompanyFactory.create()
    ap1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=hc1,
        completion_date=date(2020, 1, 1),
    )
    ApartmentFactory.create(
        building__real_estate__housing_company=hc1,
        completion_date=date(2000, 1, 1),
    )

    response = api_client.get(reverse("hitas:housing-company-list"))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == [
        {
            "id": hc2.uuid.hex,
            "name": hc2.display_name,
            "hitas_type": hc2.hitas_type.value,
            "completed": False,
            "over_thirty_years_old": False,
            "exclude_from_statistics": hc2.exclude_from_statistics,
            "regulation_status": hc2.regulation_status.value,
            "address": {
                "street_address": hc2.street_address,
                "postal_code": hc2.postal_code.value,
                "city": hc2.postal_code.city,
            },
            "area": {"name": hc2.postal_code.city, "cost_area": hc2.postal_code.cost_area},
            "completion_date": None,
        },
        {
            "id": hc1.uuid.hex,
            "name": hc1.display_name,
            "hitas_type": hc1.hitas_type.value,
            "completed": True,
            "over_thirty_years_old": False,
            "exclude_from_statistics": hc1.exclude_from_statistics,
            "regulation_status": hc1.regulation_status.value,
            "address": {
                "street_address": hc1.street_address,
                "postal_code": hc1.postal_code.value,
                "city": hc1.postal_code.city,
            },
            "area": {"name": hc1.postal_code.city, "cost_area": hc1.postal_code.cost_area},
            "completion_date": str(ap1.completion_date),
        },
    ]
    assert response.json()["page"] == {
        "size": 2,
        "current_page": 1,
        "total_items": 2,
        "total_pages": 1,
        "links": {
            "next": None,
            "previous": None,
        },
    }


@pytest.mark.django_db
def test__api__housing_company__list__paging(api_client: HitasAPIClient):
    HousingCompanyFactory.create_batch(size=45)

    response = api_client.get(reverse("hitas:housing-company-list"))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["page"] == {
        "size": 10,
        "current_page": 1,
        "total_items": 45,
        "total_pages": 5,
        "links": {
            "next": "http://testserver/api/v1/housing-companies?page=2",
            "previous": None,
        },
    }

    # Make the second page request
    response = api_client.get(reverse("hitas:housing-company-list"), {"page": 2})
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["page"] == {
        "size": 10,
        "current_page": 2,
        "total_items": 45,
        "total_pages": 5,
        "links": {
            "next": "http://testserver/api/v1/housing-companies?page=3",
            "previous": "http://testserver/api/v1/housing-companies",
        },
    }

    # Make the last page request
    response = api_client.get(reverse("hitas:housing-company-list"), {"page": 5})
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["page"] == {
        "size": 5,
        "current_page": 5,
        "total_items": 45,
        "total_pages": 5,
        "links": {
            "next": None,
            "previous": "http://testserver/api/v1/housing-companies?page=4",
        },
    }


@pytest.mark.parametrize("page_number", ["a", "#", " ", ""])
@pytest.mark.django_db
def test__api__housing_company__list__paging__invalid(api_client: HitasAPIClient, page_number):
    response = api_client.get(
        reverse("hitas:housing-company-list"), {"page": page_number}, openapi_validate_request=False
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == exceptions.InvalidPage().data


@pytest.mark.django_db
def test__api__housing_company__list__paging__too_high(api_client: HitasAPIClient):
    response = api_client.get(reverse("hitas:housing-company-list"), {"page": 2})
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["contents"] == []
    assert response.json()["page"] == {
        "size": 0,
        "current_page": 1,
        "total_items": 0,
        "total_pages": 1,
        "links": {
            "next": None,
            "previous": None,
        },
    }


# Retrieve tests


@pytest.mark.parametrize("apt_with_null_prices", [False, True])
@pytest.mark.django_db
def test__api__housing_company__retrieve(api_client: HitasAPIClient, apt_with_null_prices: bool, freezer):
    day = datetime.datetime(2023, 2, 1)
    freezer.move_to(day)

    hc1: HousingCompany = HousingCompanyFactory.create()
    hc1_re1: RealEstate = RealEstateFactory.create(housing_company=hc1)
    hc1_re1_bu1: Building = BuildingFactory.create(real_estate=hc1_re1)
    hc1_re1_bu1_ap1: Apartment = ApartmentFactory.create(
        building=hc1_re1_bu1,
        completion_date=date(2022, 1, 1),
        surface_area=10.5,
        share_number_end=100,
        share_number_start=1,
        sales__purchase_price=100.5,
        sales__apartment_share_of_housing_company_loans=200.0,
    )
    ApartmentFactory.create(
        building=hc1_re1_bu1,
        completion_date=date(2020, 1, 1),
        surface_area=20.5,
        share_number_end=200,
        share_number_start=101,
        sales__purchase_price=300.5,
        sales__apartment_share_of_housing_company_loans=400.0,
    )
    hc1_re1_bu2: Building = BuildingFactory.create(real_estate=hc1_re1)
    ApartmentFactory.create(
        building=hc1_re1_bu2,
        completion_date=date(2021, 1, 1),
        surface_area=20.0,
        share_number_end=450,
        share_number_start=201,
        sales__purchase_price=500.0,
        sales__apartment_share_of_housing_company_loans=600.5,
    )
    hc1_re2: RealEstate = RealEstateFactory.create(housing_company=hc1)
    hc1_re2_bu1: Building = BuildingFactory.create(real_estate=hc1_re2)
    if apt_with_null_prices:
        # Make sure an Apartment with null prices doesn't affect Housing Company's summary values
        ApartmentFactory.create(
            surface_area=50,
            sales=[],
            completion_date=date(2021, 1, 1),
            additional_work_during_construction=None,
            loans_during_construction=None,
            interest_during_construction_6=None,
            interest_during_construction_14=None,
            debt_free_purchase_price_during_construction=None,
        )

    mpi: HousingCompanyConstructionPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=hc1
    )
    cpi: HousingCompanyConstructionPriceImprovement = HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=hc1
    )

    # Second HousingCompany with a building
    BuildingFactory.create()

    log = last_log(HousingCompany, model_id=hc1.id)

    response = api_client.get(reverse("hitas:housing-company-detail", args=[hc1.uuid.hex]))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "id": hc1.uuid.hex,
        "business_id": hc1.business_id,
        "name": {"display": hc1.display_name, "official": hc1.official_name},
        "hitas_type": hc1.hitas_type.value,
        "completed": True,
        "exclude_from_statistics": False,
        "over_thirty_years_old": False,
        "regulation_status": hc1.regulation_status.value,
        "address": {"city": "Helsinki", "postal_code": hc1.postal_code.value, "street_address": hc1.street_address},
        "area": {"name": hc1.postal_code.city, "cost_area": hc1.postal_code.cost_area},
        "completion_date": hc1_re1_bu1_ap1.completion_date.isoformat(),
        "summary": {
            # (100.5+200+300.5+400+500+600.5) = 2101.5
            "realized_acquisition_price": 2101.5,
            # (100+200+300+400+500+600) / (10.5+20.5+20.5) = 2101.5 / 51.0 ~= 41.21
            "average_price_per_square_meter": 41.21,
            # (100 - 1 + 1) + (200 - 101 + 1) + (450 - 201 + 1) = 100 + 100 + 250 = 450
            "total_shares": 450,
            # 10.5+20.5+20
            "total_surface_area": 51.0,
        },
        "real_estates": [
            {
                "id": hc1_re1.uuid.hex,
                "address": {
                    "city": "Helsinki",
                    "postal_code": hc1_re1.postal_code.value,
                    "street_address": hc1_re1.street_address,
                },
                "property_identifier": hc1_re1.property_identifier,
                "buildings": [
                    {
                        "id": hc1_re1_bu1.uuid.hex,
                        "address": {
                            "city": "Helsinki",
                            "postal_code": hc1_re1_bu1.postal_code.value,
                            "street_address": hc1_re1_bu1.street_address,
                        },
                        "building_identifier": hc1_re1_bu1.building_identifier,
                        "apartment_count": 2,
                    },
                    {
                        "id": hc1_re1_bu2.uuid.hex,
                        "address": {
                            "city": "Helsinki",
                            "postal_code": hc1_re1_bu2.postal_code.value,
                            "street_address": hc1_re1_bu2.street_address,
                        },
                        "building_identifier": hc1_re1_bu2.building_identifier,
                        "apartment_count": 1,
                    },
                ],
            },
            {
                "id": hc1_re2.uuid.hex,
                "address": {
                    "city": "Helsinki",
                    "postal_code": hc1_re2.postal_code.value,
                    "street_address": hc1_re2.street_address,
                },
                "property_identifier": hc1_re2.property_identifier,
                "buildings": [
                    {
                        "id": hc1_re2_bu1.uuid.hex,
                        "address": {
                            "city": "Helsinki",
                            "postal_code": hc1_re2_bu1.postal_code.value,
                            "street_address": hc1_re2_bu1.street_address,
                        },
                        "building_identifier": hc1_re2_bu1.building_identifier,
                        "apartment_count": 0,
                    }
                ],
            },
        ],
        "building_type": {
            "id": hc1.building_type.uuid.hex,
            "value": hc1.building_type.value,
            "description": hc1.building_type.description,
        },
        "developer": {
            "id": hc1.developer.uuid.hex,
            "value": hc1.developer.value,
            "description": hc1.developer.description,
        },
        "property_manager": {
            "id": hc1.property_manager.uuid.hex,
            "name": hc1.property_manager.name,
            "email": hc1.property_manager.email,
        },
        "acquisition_price": float(hc1.acquisition_price),
        "primary_loan": float(hc1.primary_loan),
        "sales_price_catalogue_confirmation_date": str(hc1.sales_price_catalogue_confirmation_date),
        "notes": hc1.notes,
        "archive_id": hc1.id,
        "release_date": hc1.legacy_release_date,
        "last_modified": {
            "datetime": log.timestamp.isoformat().replace("+00:00", "Z"),
            "user": {
                # User not set since housing company created outside an api request
                "username": None,
                "first_name": None,
                "last_name": None,
            },
        },
        "improvements": {
            "construction_price_index": [
                {
                    "name": cpi.name,
                    "value": float(cpi.value),
                    "completion_date": cpi.completion_date.strftime("%Y-%m"),
                },
            ],
            "market_price_index": [
                {
                    "name": mpi.name,
                    "value": float(mpi.value),
                    "completion_date": mpi.completion_date.strftime("%Y-%m"),
                    "no_deductions": False,
                },
            ],
        },
    }


@pytest.mark.django_db
def test__api__housing_company__retrieve_rounding(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    ApartmentFactory.create(
        building__real_estate__housing_company=hc,
        surface_area=1,
        sales__purchase_price=1,
        sales__apartment_share_of_housing_company_loans=2,
    )
    ApartmentFactory.create(
        building__real_estate__housing_company=hc,
        surface_area=1,
        sales__purchase_price=1,
        sales__apartment_share_of_housing_company_loans=1,
    )

    response = api_client.get(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["summary"]["average_price_per_square_meter"] == 2.5  # ((1 + 2) + (1 + 1)) / (1 + 1)


@pytest.mark.django_db
def test__api__housing_company__retrieve__release_date__legacy(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create(
        legacy_release_date=date(2022, 1, 1),
        regulation_status=RegulationStatus.RELEASED_BY_HITAS,
    )

    response = api_client.get(reverse("hitas:housing-company-detail", args=[housing_company.uuid.hex]))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["release_date"] == date(2022, 1, 1).isoformat()


@pytest.mark.django_db
def test__api__housing_company__retrieve__release_date__regulation(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create(regulation_status=RegulationStatus.RELEASED_BY_HITAS)
    results = ThirtyYearRegulationResults.objects.create(
        calculation_month=date(2022, 1, 1),
        regulation_month=date(2000, 1, 1),
        surface_area_price_ceiling=Decimal("5000"),
        sales_data=FullSalesData(internal={}, external={}, price_by_area={}),
        replacement_postal_codes=[],
    )
    ThirtyYearRegulationResultsRow.objects.create(
        parent=results,
        housing_company=housing_company,
        completion_date=date(2001, 1, 1),
        surface_area=10,
        postal_code="00001",
        realized_acquisition_price=Decimal("60000.0"),
        unadjusted_average_price_per_square_meter=Decimal("6000.0"),
        adjusted_average_price_per_square_meter=Decimal("12000.0"),
        completion_month_index=Decimal("100"),
        calculation_month_index=Decimal("200"),
        regulation_result=RegulationResult.RELEASED_FROM_REGULATION,
    )

    response = api_client.get(reverse("hitas:housing-company-detail", args=[housing_company.uuid.hex]))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["release_date"] == date(2022, 1, 1).isoformat()


@pytest.mark.django_db
def test__api__housing_company__retrieve__release_date__regulation__dont_count_if_stays(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    results = ThirtyYearRegulationResults.objects.create(
        calculation_month=date(2022, 1, 1),
        regulation_month=date(2000, 1, 1),
        surface_area_price_ceiling=Decimal("5000"),
        sales_data=FullSalesData(internal={}, external={}, price_by_area={}),
        replacement_postal_codes=[],
    )
    ThirtyYearRegulationResultsRow.objects.create(
        parent=results,
        housing_company=housing_company,
        completion_date=date(2001, 1, 1),
        surface_area=10,
        postal_code="00001",
        realized_acquisition_price=Decimal("60000.0"),
        unadjusted_average_price_per_square_meter=Decimal("6000.0"),
        adjusted_average_price_per_square_meter=Decimal("12000.0"),
        completion_month_index=Decimal("100"),
        calculation_month_index=Decimal("200"),
        regulation_result=RegulationResult.STAYS_REGULATED,
    )

    response = api_client.get(reverse("hitas:housing-company-detail", args=[housing_company.uuid.hex]))
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json()["release_date"] is None


@pytest.mark.parametrize("invalid_id", ["foo", "38432c233a914dfb9c2f54d9f5ad9063"])
@pytest.mark.django_db
def test__api__housing_company__read__not_found(api_client: HitasAPIClient, invalid_id):
    HousingCompanyFactory.create()

    response = api_client.get(reverse("hitas:housing-company-detail", args=[invalid_id]))
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "housing_company_not_found",
        "message": "Housing company not found",
        "reason": "Not Found",
        "status": 404,
    }


# Create tests


def get_housing_company_create_data() -> dict[str, Any]:
    developer: Developer = DeveloperFactory.create()
    building_type: BuildingType = BuildingTypeFactory.create()
    postal_code: HitasPostalCode = HitasPostalCodeFactory.create()
    property_manager: PropertyManager = PropertyManagerFactory.create()

    data = {
        "acquisition_price": 10.00,
        "address": {
            "postal_code": postal_code.value,
            "street_address": "test-street-address-1",
        },
        "building_type": {"id": building_type.uuid.hex},
        "business_id": "1234567-1",
        "developer": {"id": developer.uuid.hex},
        "name": {
            "display": "test-housing-company-1",
            "official": "test-housing-company-1-as-oy",
        },
        "notes": "This is a note.",
        "primary_loan": 10.00,
        "property_manager": {"id": property_manager.uuid.hex},
        "regulation_status": RegulationStatus.REGULATED.value,
        "hitas_type": HitasType.HITAS_I.value,
        "sales_price_catalogue_confirmation_date": "2022-01-01",
        "improvements": {
            "construction_price_index": [
                {
                    "value": 1234,
                    "name": "construction-price-index-improvement-1",
                    "completion_date": "2017-01",
                },
                {
                    "value": 2345,
                    "name": "construction-price-index-improvement-2",
                    "completion_date": "2018-12",
                },
            ],
            "market_price_index": [
                {
                    "value": 3456,
                    "name": "market-price-index-improvement",
                    "completion_date": "2022-05",
                    "no_deductions": False,
                }
            ],
        },
    }
    return data


@pytest.mark.parametrize("minimal_data", [False, True])
@pytest.mark.django_db
def test__api__housing_company__create(api_client: HitasAPIClient, minimal_data: bool):
    data = get_housing_company_create_data()
    if minimal_data:
        data.update(
            {
                "business_id": None,
                "primary_loan": None,
                "property_manager": None,
                "notes": "",
                "sales_price_catalogue_confirmation_date": None,
                "improvements": {
                    "market_price_index": [],
                    "construction_price_index": [],
                },
            }
        )

    response = api_client.post(reverse("hitas:housing-company-list"), data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    hc = HousingCompany.objects.get(uuid=response.json()["id"])
    assert response.json()["address"]["postal_code"] == HitasPostalCode.objects.first().value

    get_response = api_client.get(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]))
    assert response.json() == get_response.json()


@pytest.mark.django_db
def test__api__housing_company__create__duplicate_official_name(api_client: HitasAPIClient):
    existing_hc: HousingCompany = HousingCompanyFactory.create(official_name="test-official-name")
    data = get_housing_company_create_data()
    data["name"]["official"] = existing_hc.official_name

    response = api_client.post(reverse("hitas:housing-company-list"), data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "name.official",
                "message": "Official name provided is already in use. Conflicting official name: 'test-official-name'.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__housing_company__create__duplicate_display_name(api_client: HitasAPIClient):
    existing_hc: HousingCompany = HousingCompanyFactory.create(display_name="test-display-name")
    data = get_housing_company_create_data()
    data["name"]["display"] = existing_hc.display_name

    response = api_client.post(reverse("hitas:housing-company-list"), data=data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "name.display",
                "message": "Display name provided is already in use. Conflicting display name: 'test-display-name'.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__housing_company__create__empty(api_client: HitasAPIClient):
    response = api_client.post(
        reverse("hitas:housing-company-list"), data={}, format="json", openapi_validate_request=False
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {"field": "name", "message": "This field is mandatory and cannot be null."},
            {"field": "hitas_type", "message": "This field is mandatory and cannot be null."},
            {"field": "address", "message": "This field is mandatory and cannot be null."},
            {"field": "building_type", "message": "This field is mandatory and cannot be null."},
            {"field": "developer", "message": "This field is mandatory and cannot be null."},
            {"field": "acquisition_price", "message": "This field is mandatory and cannot be null."},
            {"field": "improvements", "message": "This field is mandatory and cannot be null."},
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.parametrize(
    "invalid_data,fields",
    [
        *parametrize_invalid_foreign_key("building_type"),
        *parametrize_invalid_foreign_key("developer"),
        *parametrize_invalid_foreign_key("property_manager", nullable=True),
        ({"business_id": "#"}, [{"field": "business_id", "message": "'#' is not a valid business id."}]),
        ({"business_id": "123"}, [{"field": "business_id", "message": "'123' is not a valid business id."}]),
        ({"name": None}, [{"field": "name", "message": "This field is mandatory and cannot be null."}]),
        ({"name": 0}, [{"field": "name", "message": "Invalid data. Expected a dictionary, but got int."}]),
        ({"address": None}, [{"field": "address", "message": "This field is mandatory and cannot be null."}]),
        ({"address": 123}, [{"field": "address", "message": "Invalid data. Expected a dictionary, but got int."}]),
        (
            {"acquisition_price": None},
            [{"field": "acquisition_price", "message": "This field is mandatory and cannot be null."}],
        ),
        ({"primary_loan": "foo"}, [{"field": "primary_loan", "message": "A valid number is required."}]),
        ({"improvements": None}, [{"field": "improvements", "message": "This field is mandatory and cannot be null."}]),
        (
            {"improvements": {"market_price_index": None, "construction_price_index": []}},
            [{"field": "improvements.market_price_index", "message": "This field is mandatory and cannot be null."}],
        ),
        (
            {"improvements": {"market_price_index": [], "construction_price_index": None}},
            [
                {
                    "field": "improvements.construction_price_index",
                    "message": "This field is mandatory and cannot be null.",
                }
            ],
        ),
        (
            {
                "improvements": {
                    "market_price_index": [
                        {
                            "name": "foo",
                            "value": 10,
                            "completion_date": "2022-01-01",
                        }
                    ],
                    "construction_price_index": [],
                }
            },
            [
                {
                    "field": "improvements.market_price_index.completion_date",
                    "message": "Date has wrong format. Use one of these formats instead: YYYY-MM.",
                }
            ],
        ),
        (
            {
                "improvements": {
                    "market_price_index": [
                        {
                            "name": "foo",
                            "value": -1,
                            "completion_date": "2022-01",
                        }
                    ],
                    "construction_price_index": [],
                }
            },
            [
                {
                    "field": "improvements.market_price_index.value",
                    "message": "Ensure this value is greater than or equal to 0.",
                }
            ],
        ),
        (
            {
                "improvements": {
                    "market_price_index": [],
                    "construction_price_index": [
                        {
                            "name": "foo",
                            "value": 10,
                            "completion_date": "2022-01-01",
                        }
                    ],
                }
            },
            [
                {
                    "field": "improvements.construction_price_index.completion_date",
                    "message": "Date has wrong format. Use one of these formats instead: YYYY-MM.",
                }
            ],
        ),
        (
            {
                "improvements": {
                    "market_price_index": [],
                    "construction_price_index": [
                        {
                            "name": "foo",
                            "value": -1,
                            "completion_date": "2022-01",
                        }
                    ],
                }
            },
            [
                {
                    "field": "improvements.construction_price_index.value",
                    "message": "Ensure this value is greater than or equal to 0.",
                }
            ],
        ),
        (
            {"notes": None},
            [{"field": "notes", "message": "This field is mandatory and cannot be null."}],
        ),
    ],
)
@pytest.mark.django_db
def test__api__housing_company__create__invalid_data(api_client: HitasAPIClient, invalid_data, fields):
    data = get_housing_company_create_data()
    data.update(invalid_data)

    response = api_client.post(
        reverse("hitas:housing-company-list"), data=data, format="json", openapi_validate_request=False
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__housing_company__create__new_hitas_construction_price_improvement(api_client: HitasAPIClient):
    data = get_housing_company_create_data()
    data["hitas_type"] = HitasType.NEW_HITAS_I.value

    url = reverse("hitas:housing-company-list")
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "construction_price_improvements",
                "message": "Cannot create construction price improvements for a housing company using new hitas rules.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Update tests


@pytest.mark.django_db
def test__api__housing_company__update(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create(hitas_type=HitasType.HITAS_I)
    ApartmentFactory.create(building__real_estate__housing_company=hc)
    postal_code: HitasPostalCode = HitasPostalCodeFactory.create(value="99999")
    property_manager: PropertyManager = PropertyManagerFactory.create()

    data = {
        "acquisition_price": 10.01,
        "address": {
            "street_address": "changed-street-address",
            "postal_code": postal_code.value,
        },
        "building_type": {"id": hc.building_type.uuid.hex},
        "business_id": "",
        "developer": {"id": hc.developer.uuid.hex},
        "name": {
            "display": "changed-name",
            "official": "changed-name-as-oy",
        },
        "notes": "",
        "primary_loan": 10.00,
        "property_manager": {"id": property_manager.uuid.hex},
        "hitas_type": hc.hitas_type.value,
        "sales_price_catalogue_confirmation_date": "2022-01-01",
        "improvements": {
            "construction_price_index": [
                {
                    "value": 1234,
                    "name": "new-name",
                    "completion_date": "2017-01",
                }
            ],
            "market_price_index": [],
        },
    }

    response = api_client.put(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]), data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()

    hc.refresh_from_db()
    assert hc.postal_code == postal_code
    assert hc.property_manager == property_manager
    assert hc.business_id is None
    assert hc.street_address == "changed-street-address"
    assert hc.acquisition_price == Decimal("10.01")
    assert hc.notes == ""
    assert response.json()["completion_date"]

    get_response = api_client.get(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]))
    assert response.json() == get_response.json()


@pytest.mark.django_db
def test__api__housing_company__update__improvements(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create(hitas_type=HitasType.HITAS_I)
    mpi1: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=hc, completion_date=date(2010, 1, 1)
    )
    HousingCompanyMarketPriceImprovementFactory.create(housing_company=hc, completion_date=date(2015, 5, 1))
    mpi3: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=hc, completion_date=date(2020, 10, 1)
    )
    HousingCompanyConstructionPriceImprovementFactory.create(housing_company=hc, completion_date=date(2020, 1, 1))
    cpi2: HousingCompanyConstructionPriceImprovement = HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=hc, completion_date=date(2020, 2, 1)
    )
    cpi3: HousingCompanyConstructionPriceImprovement = HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=hc, completion_date=date(2020, 3, 1)
    )

    cpi2.value = 999999

    def improvement_to_dict(i):
        return {
            "value": i.value,
            "completion_date": i.completion_date.strftime("%Y-%m"),
            "name": i.name,
        }

    data = {
        "acquisition_price": hc.acquisition_price,
        "address": {
            "street_address": hc.street_address,
            "postal_code": hc.postal_code.value,
        },
        "building_type": {"id": hc.building_type.uuid.hex},
        "business_id": hc.business_id,
        "developer": {"id": hc.developer.uuid.hex},
        "name": {
            "display": hc.display_name,
            "official": hc.official_name,
        },
        "notes": hc.notes,
        "primary_loan": hc.primary_loan,
        "property_manager": {"id": hc.property_manager.uuid.hex},
        "hitas_type": hc.hitas_type.value,
        "sales_price_catalogue_confirmation_date": hc.sales_price_catalogue_confirmation_date,
        "improvements": {
            "construction_price_index": list(
                map(improvement_to_dict, [cpi3, cpi2])
            ),  # remove cpi1, modify 2, change order
            "market_price_index": list(map(improvement_to_dict, [mpi1, mpi3])),  # remove mpi2
        },
    }

    response = api_client.put(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]), data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()

    get_response = api_client.get(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]))
    assert get_response.json() == get_response.json()


@pytest.mark.django_db
def test__api__housing_company__update__add_improvement(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create(hitas_type=HitasType.HITAS_I)
    mpi1: HousingCompanyMarketPriceImprovement = HousingCompanyMarketPriceImprovementFactory.create(
        housing_company=hc, completion_date=date(2010, 1, 1)
    )
    cpi1: HousingCompanyConstructionPriceImprovement = HousingCompanyConstructionPriceImprovementFactory.create(
        housing_company=hc, completion_date=date(2020, 1, 1)
    )
    cpi2 = HousingCompanyMarketPriceImprovementFactory(
        housing_company=hc, completion_date=date(2011, 1, 1), value=10, name="new-improvement"
    )

    def improvement_to_dict(i):
        return {
            "value": i.value,
            "completion_date": i.completion_date.strftime("%Y-%m"),
            "name": i.name,
        }

    data = {
        "acquisition_price": hc.acquisition_price,
        "address": {
            "street_address": hc.street_address,
            "postal_code": hc.postal_code.value,
        },
        "building_type": {"id": hc.building_type.uuid.hex},
        "business_id": hc.business_id,
        "developer": {"id": hc.developer.uuid.hex},
        "name": {
            "display": hc.display_name,
            "official": hc.official_name,
        },
        "notes": hc.notes,
        "primary_loan": hc.primary_loan,
        "property_manager": {"id": hc.property_manager.uuid.hex},
        "hitas_type": hc.hitas_type.value,
        "sales_price_catalogue_confirmation_date": hc.sales_price_catalogue_confirmation_date,
        "improvements": {
            "construction_price_index": list(map(improvement_to_dict, [cpi1, cpi2])),
            "market_price_index": list(map(improvement_to_dict, [mpi1])),
        },
    }

    response = api_client.put(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]), data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()

    get_response = api_client.get(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]))
    assert get_response.json() == get_response.json()


@pytest.mark.django_db
def test__api__housing_company__update__new_hitas_construction_price_improvement(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create(hitas_type=HitasType.NEW_HITAS_I)
    improvement: HousingCompanyConstructionPriceImprovement
    improvement = HousingCompanyConstructionPriceImprovementFactory.create(housing_company=housing_company)

    data = {
        "acquisition_price": housing_company.acquisition_price,
        "address": {
            "street_address": housing_company.street_address,
            "postal_code": housing_company.postal_code.value,
        },
        "building_type": {"id": housing_company.building_type.uuid.hex},
        "business_id": housing_company.business_id,
        "developer": {"id": housing_company.developer.uuid.hex},
        "name": {
            "display": housing_company.display_name,
            "official": housing_company.official_name,
        },
        "notes": housing_company.notes,
        "primary_loan": housing_company.primary_loan,
        "property_manager": {"id": housing_company.property_manager.uuid.hex},
        "hitas_type": housing_company.hitas_type.value,
        "sales_price_catalogue_confirmation_date": housing_company.sales_price_catalogue_confirmation_date,
        "improvements": {
            "construction_price_index": [
                {
                    "value": improvement.value,
                    "completion_date": improvement.completion_date.strftime("%Y-%m"),
                    "name": improvement.name,
                }
            ],
            "market_price_index": [],
        },
    }

    url = reverse("hitas:housing-company-detail", kwargs={"uuid": housing_company.uuid.hex})
    response = api_client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "construction_price_improvements",
                "message": "Cannot create construction price improvements for a housing company using new hitas rules.",
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__housing_company__update__improvements_removed_if_empty_list_given(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    HousingCompanyMarketPriceImprovementFactory.create(housing_company=housing_company)
    HousingCompanyConstructionPriceImprovementFactory.create(housing_company=housing_company)

    assert len(housing_company.construction_price_improvements.all()) == 1
    assert len(housing_company.market_price_improvements.all()) == 1

    data = {
        "acquisition_price": housing_company.acquisition_price,
        "address": {
            "street_address": housing_company.street_address,
            "postal_code": housing_company.postal_code.value,
        },
        "building_type": {"id": housing_company.building_type.uuid.hex},
        "business_id": housing_company.business_id,
        "developer": {"id": housing_company.developer.uuid.hex},
        "name": {
            "display": housing_company.display_name,
            "official": housing_company.official_name,
        },
        "notes": housing_company.notes,
        "primary_loan": housing_company.primary_loan,
        "property_manager": {"id": housing_company.property_manager.uuid.hex},
        "hitas_type": housing_company.hitas_type.value,
        "sales_price_catalogue_confirmation_date": housing_company.sales_price_catalogue_confirmation_date,
        "improvements": {
            "construction_price_index": [],
            "market_price_index": [],
        },
    }

    url = reverse("hitas:housing-company-detail", kwargs={"uuid": housing_company.uuid.hex})

    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()

    housing_company.refresh_from_db()
    assert len(housing_company.construction_price_improvements.all()) == 0
    assert len(housing_company.market_price_improvements.all()) == 0


@pytest.mark.django_db
def test__api__housing_company__update__no_changes(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()

    data = {
        "acquisition_price": hc.acquisition_price,
        "address": {
            "street_address": hc.street_address,
            "postal_code": hc.postal_code.value,
        },
        "building_type": {"id": hc.building_type.uuid.hex},
        "business_id": hc.business_id,
        "developer": {"id": hc.developer.uuid.hex},
        "name": {
            "display": hc.display_name,
            "official": hc.official_name,
        },
        "notes": hc.notes,
        "primary_loan": hc.primary_loan,
        "property_manager": {"id": hc.property_manager.uuid.hex},
        "hitas_type": hc.hitas_type.value,
        "improvements": {
            "construction_price_index": [],
            "market_price_index": [],
        },
    }

    response = api_client.put(reverse("hitas:housing-company-detail", args=[hc.uuid.hex]), data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()


@pytest.mark.django_db
def test__api__housing_company__update__fulfill_condition_of_sale(api_client: HitasAPIClient):
    apartment_1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    condition_of_sale: ConditionOfSale = ConditionOfSaleFactory.create(
        new_ownership=apartment_1.first_sale().ownerships.first(),
        old_ownership=apartment_2.first_sale().ownerships.first(),
    )

    assert condition_of_sale.fulfilled is None

    data = {
        "acquisition_price": apartment_1.housing_company.acquisition_price,
        "address": {
            "street_address": apartment_1.housing_company.street_address,
            "postal_code": apartment_1.housing_company.postal_code.value,
        },
        "building_type": {"id": apartment_1.housing_company.building_type.uuid.hex},
        "business_id": apartment_1.housing_company.business_id,
        "developer": {"id": apartment_1.housing_company.developer.uuid.hex},
        "name": {
            "display": apartment_1.housing_company.display_name,
            "official": apartment_1.housing_company.official_name,
        },
        "notes": apartment_1.housing_company.notes,
        "primary_loan": apartment_1.housing_company.primary_loan,
        "property_manager": {"id": apartment_1.housing_company.property_manager.uuid.hex},
        "hitas_type": apartment_1.housing_company.hitas_type.value,
        "improvements": {
            "construction_price_index": [],
            "market_price_index": [],
        },
        "regulation_status": RegulationStatus.RELEASED_BY_HITAS.value,
    }

    url = reverse(
        "hitas:housing-company-detail",
        kwargs={
            "uuid": apartment_1.housing_company.uuid.hex,
        },
    )

    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()

    # Check that the regulation status has been updated
    apartment_1.housing_company.refresh_from_db()
    assert apartment_1.housing_company.regulation_status == RegulationStatus.RELEASED_BY_HITAS

    # Check that the condition of sale has been fulfilled
    condition_of_sale.refresh_from_db()
    assert condition_of_sale.fulfilled is not None


# Partial update


@pytest.mark.django_db
def test__api__housing_company__partial_update__improvements_left_alone_if_not_given(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    HousingCompanyMarketPriceImprovementFactory.create(housing_company=housing_company)
    HousingCompanyConstructionPriceImprovementFactory.create(housing_company=housing_company)

    assert len(housing_company.construction_price_improvements.all()) == 1
    assert len(housing_company.market_price_improvements.all()) == 1

    data = {
        "acquisition_price": housing_company.acquisition_price,
        "address": {
            "street_address": housing_company.street_address,
            "postal_code": housing_company.postal_code.value,
        },
        "building_type": {"id": housing_company.building_type.uuid.hex},
        "business_id": housing_company.business_id,
        "developer": {"id": housing_company.developer.uuid.hex},
        "name": {
            "display": housing_company.display_name,
            "official": housing_company.official_name,
        },
        "notes": housing_company.notes,
        "primary_loan": housing_company.primary_loan,
        "property_manager": {"id": housing_company.property_manager.uuid.hex},
        "hitas_type": housing_company.hitas_type.value,
        "sales_price_catalogue_confirmation_date": housing_company.sales_price_catalogue_confirmation_date,
        # Improvements not given
    }

    url = reverse("hitas:housing-company-detail", kwargs={"uuid": housing_company.uuid.hex})

    response = api_client.patch(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK, response.json()

    housing_company.refresh_from_db()
    assert len(housing_company.construction_price_improvements.all()) == 1
    assert len(housing_company.market_price_improvements.all()) == 1


# Delete tests


@pytest.mark.django_db
def test__api__housing_company__delete(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()

    url = reverse("hitas:housing-company-detail", kwargs={"uuid": hc.uuid.hex})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


@pytest.mark.django_db
def test__api__housing_company__delete__with_references(api_client: HitasAPIClient):
    hc: HousingCompany = HousingCompanyFactory.create()
    re: RealEstate = RealEstateFactory.create(housing_company=hc)
    bu: Building = BuildingFactory.create(real_estate=re)
    ApartmentFactory.create(building=bu)

    url = reverse("hitas:housing-company-detail", kwargs={"uuid": hc.uuid.hex})

    response = api_client.delete(url)
    assert response.status_code == status.HTTP_409_CONFLICT, response.json()

    assert response.json() == {
        "error": "real_estates_on_housing_company",
        "message": "Cannot delete a housing company with real estates.",
        "reason": "Conflict",
        "status": 409,
    }


# Filter tests


@pytest.mark.parametrize(
    "selected_filter",
    [
        {"display_name": "TestDisplayName"},
        {"display_name": "xx"},
        {"street_address": "test-street"},
        {"street_address": "xx"},
        {"property_manager": "TestPropertyManager"},
        {"property_manager": "xx"},
        {"developer": "TestDeveloper"},
        {"developer": "xx"},
        {"postal_code": "99999"},
        {"archive_id": 999},
    ],
)
@pytest.mark.django_db
def test__api__housing_company__filter(api_client: HitasAPIClient, selected_filter):
    hc: HousingCompany = HousingCompanyFactory.create(display_name="TestDisplayName")
    HousingCompanyFactory.create(official_name="TestOfficialName OY")
    HousingCompanyFactory.create(display_name="test-XX-display")
    HousingCompanyFactory.create(regulation_status=RegulationStatus.RELEASED_BY_PLOT_DEPARTMENT)
    HousingCompanyFactory.create(street_address="test-street")
    HousingCompanyFactory.create(street_address="test-XX-street")
    HousingCompanyFactory.create(property_manager__name="TestPropertyManager")
    HousingCompanyFactory.create(property_manager__name="test-XX-property")
    HousingCompanyFactory.create(developer__value="TestDeveloper")
    HousingCompanyFactory.create(developer__value="test-XX-developer")
    HousingCompanyFactory.create(postal_code__value="99999")
    HousingCompanyFactory.create(id=999)
    RealEstateFactory.create(property_identifier="1-1234-321-56", housing_company=hc)
    RealEstateFactory.create(property_identifier="1111-1111-1111-1111", housing_company=hc)

    url = reverse("hitas:housing-company-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()["contents"]) == 1, response.json()


@pytest.mark.django_db
def test__api__housing_company__filter__new_hitas(api_client: HitasAPIClient):
    ApartmentFactory.create(
        completion_date=datetime.date(2012, 1, 1),
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    ApartmentFactory.create(
        completion_date=datetime.date(2020, 1, 1),
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
    )
    ApartmentFactory.create(
        completion_date=datetime.date(2010, 12, 31),
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
    )
    ApartmentFactory.create(
        completion_date=datetime.date(1990, 1, 1),
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
    )

    url = reverse("hitas:housing-company-list") + "?new_hitas=true"
    response_json = api_client.get(url).json()["contents"]
    assert len(response_json) == 1, response_json

    url = reverse("hitas:housing-company-list") + "?new_hitas=false"
    response_json = api_client.get(url).json()["contents"]
    print(response_json)
    assert len(response_json) == 3, response_json


@pytest.mark.django_db
def test__api__housing_company__filter__regulation_status(api_client: HitasAPIClient):
    HousingCompanyFactory.create(regulation_status=RegulationStatus.REGULATED)
    HousingCompanyFactory.create(regulation_status=RegulationStatus.RELEASED_BY_PLOT_DEPARTMENT)
    HousingCompanyFactory.create(regulation_status=RegulationStatus.RELEASED_BY_PLOT_DEPARTMENT)
    HousingCompanyFactory.create(regulation_status=RegulationStatus.RELEASED_BY_HITAS)

    url = reverse("hitas:housing-company-list") + "?is_regulated=true"
    response_json = api_client.get(url).json()["contents"]
    assert len(response_json) == 1, response_json

    url = reverse("hitas:housing-company-list") + "?is_regulated=false"
    response_json = api_client.get(url).json()["contents"]
    print(response_json)
    assert len(response_json) == 3, response_json


@pytest.mark.parametrize(
    "selected_filter,fields",
    [
        (
            {"display_name": "a"},
            [{"field": "display_name", "message": "Ensure this value has at least 2 characters (it has 1)."}],
        ),
        (
            {"street_address": "a"},
            [{"field": "street_address", "message": "Ensure this value has at least 2 characters (it has 1)."}],
        ),
        (
            {"property_manager": "a"},
            [{"field": "property_manager", "message": "Ensure this value has at least 2 characters (it has 1)."}],
        ),
        (
            {"developer": "a"},
            [{"field": "developer", "message": "Ensure this value has at least 2 characters (it has 1)."}],
        ),
        (
            {"postal_code": "abcde"},
            [{"field": "postal_code", "message": "Enter a valid value."}],
        ),
        (
            {"postal_code": "1234"},
            [{"field": "postal_code", "message": "Enter a valid value."}],
        ),
        (
            {"postal_code": "123456"},
            [{"field": "postal_code", "message": "Enter a valid value."}],
        ),
        (
            {"archive_id": "-1"},
            [{"field": "archive_id", "message": "Ensure this value is greater than or equal to 1."}],
        ),
        (
            {"archive_id": "0"},
            [{"field": "archive_id", "message": "Ensure this value is greater than or equal to 1."}],
        ),
    ],
)
@pytest.mark.django_db
def test__api__housing_company__filter__invalid_data(api_client: HitasAPIClient, selected_filter, fields):
    url = reverse("hitas:housing-company-list") + "?" + urlencode(selected_filter)
    response = api_client.get(url, openapi_validate_request=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Hitas type tests


@pytest.mark.django_db
def test__api__hitas_type(api_client: HitasAPIClient):
    url = reverse("hitas:hitas-type-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == [
        {
            "label": "Ei Hitas",
            "value": "non_hitas",
            "no_interest": False,
            "old_ruleset": True,
            "skip_from_statistics": True,
        },
        {
            "label": "Hitas I",
            "value": "hitas_1",
            "no_interest": False,
            "old_ruleset": True,
            "skip_from_statistics": False,
        },
        {
            "label": "Hitas II",
            "value": "hitas_2",
            "no_interest": False,
            "old_ruleset": True,
            "skip_from_statistics": False,
        },
        {
            "label": "Hitas I, Ei korkoja",
            "value": "hitas_1_no_interest",
            "no_interest": True,
            "old_ruleset": True,
            "skip_from_statistics": False,
        },
        {
            "label": "Hitas II, Ei korkoja",
            "value": "hitas_2_no_interest",
            "no_interest": True,
            "old_ruleset": True,
            "skip_from_statistics": False,
        },
        {
            "label": "Uusi Hitas I",
            "value": "new_hitas_1",
            "no_interest": False,
            "old_ruleset": False,
            "skip_from_statistics": False,
        },
        {
            "label": "Uusi Hitas II",
            "value": "new_hitas_2",
            "no_interest": False,
            "old_ruleset": False,
            "skip_from_statistics": False,
        },
        {
            "label": "Puolihitas",
            "value": "half_hitas",
            "no_interest": False,
            "old_ruleset": True,
            "skip_from_statistics": True,
        },
        {
            "label": "Vuokratalo Hitas I",
            "value": "rental_hitas_1",
            "no_interest": True,
            "old_ruleset": True,
            "skip_from_statistics": True,
        },
        {
            "label": "Vuokratalo Hitas II",
            "value": "rental_hitas_2",
            "no_interest": True,
            "old_ruleset": True,
            "skip_from_statistics": True,
        },
    ]


# Regulation status tests


@pytest.mark.django_db
def test__api__regulation_status(api_client: HitasAPIClient):
    url = reverse("hitas:regulation-status-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == [
        {"label": "Regulated", "value": "regulated"},
        {"label": "Released by Hitas", "value": "released_by_hitas"},
        {"label": "Released by Plot Department", "value": "released_by_plot_department"},
    ]


# Batch complete apartments tests


@pytest.mark.django_db
def test__api__batch_complete_apartments__improper_range(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 2,
        "apartment_number_end": 1,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "non_field_errors",
                "message": "Starting apartment number must be less than or equal to the ending apartment number.",
            },
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__batch_complete_apartments__no_apartments(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 1,
        "apartment_number_end": 100,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 0,
    }


@pytest.mark.django_db
def test__api__batch_complete_apartments__single__in_range(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number=1,
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 1,
        "apartment_number_end": 1,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 1,
    }

    apartment.refresh_from_db()
    assert apartment.completion_date == date(2020, 1, 1)


@pytest.mark.django_db
def test__api__batch_complete_apartments__single__not_in_range(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number=1,
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 2,
        "apartment_number_end": 100,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 0,
    }

    apartment.refresh_from_db()
    assert apartment.completion_date is None


@pytest.mark.django_db
def test__api__batch_complete_apartments__single__all(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number=1,
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": None,
        "apartment_number_end": None,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 1,
    }

    apartment.refresh_from_db()
    assert apartment.completion_date == date(2020, 1, 1)


@pytest.mark.django_db
def test__api__batch_complete_apartments__single__set_not_completed(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number=1,
        completion_date=datetime.date(2020, 1, 1),
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": None,
        "apartment_number_start": 1,
        "apartment_number_end": 1,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 1,
    }

    apartment.refresh_from_db()
    assert apartment.completion_date is None


@pytest.mark.django_db
def test__api__batch_complete_apartments__multiple__in_range(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment_1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number=1,
        completion_date=None,
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number=2,
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 1,
        "apartment_number_end": 2,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 2,
    }

    apartment_1.refresh_from_db()
    assert apartment_1.completion_date == date(2020, 1, 1)

    apartment_2.refresh_from_db()
    assert apartment_2.completion_date == date(2020, 1, 1)


@pytest.mark.django_db
def test__api__batch_complete_apartments__multiple__some_in_range(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment_1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number=1,
        completion_date=None,
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number=2,
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 1,
        "apartment_number_end": 1,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 1,
    }

    apartment_1.refresh_from_db()
    assert apartment_1.completion_date == date(2020, 1, 1)

    apartment_2.refresh_from_db()
    assert apartment_2.completion_date is None


@pytest.mark.django_db
def test__api__batch_complete_apartments__multiple__different_stair(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment_1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number=1,
        completion_date=None,
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="B",
        apartment_number=1,
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 1,
        "apartment_number_end": 1,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()

    # Both apartments are completed, even though they are in different stairs
    # This was agreed as the current accepted behaviour, as the most common use cases
    # for this feature are covered by just selecting an apartment number range.
    assert response.json() == {
        "completed_apartment_count": 2,
    }

    apartment_1.refresh_from_db()
    assert apartment_1.completion_date == date(2020, 1, 1)

    apartment_2.refresh_from_db()
    assert apartment_2.completion_date == date(2020, 1, 1)


@pytest.mark.django_db
def test__api__batch_complete_apartments__multiple__all(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment_1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number=1,
        completion_date=None,
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number=2,
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": None,
        "apartment_number_end": None,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 2,
    }

    apartment_1.refresh_from_db()
    assert apartment_1.completion_date == date(2020, 1, 1)

    apartment_2.refresh_from_db()
    assert apartment_2.completion_date == date(2020, 1, 1)


@pytest.mark.django_db
def test__api__batch_complete_apartments__multiple__one_already_completed(api_client: HitasAPIClient):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment_1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number=1,
        completion_date=None,
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number=2,
        completion_date=date(2022, 1, 1),
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": 1,
        "apartment_number_end": 2,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 2,
    }

    apartment_1.refresh_from_db()
    assert apartment_1.completion_date == date(2020, 1, 1)

    # Completion date is changed even if set
    apartment_2.refresh_from_db()
    assert apartment_2.completion_date == date(2020, 1, 1)


@pytest.mark.parametrize(
    ["apartment_number_start", "apartment_number_end"],
    [
        (1, None),
        (None, 2),
    ],
)
@pytest.mark.django_db
def test__api__batch_complete_apartments__multiple__open_range(
    api_client: HitasAPIClient,
    apartment_number_start: Optional[int],
    apartment_number_end: Optional[int],
):
    housing_company: HousingCompany = HousingCompanyFactory.create()
    apartment_1: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number=1,
        completion_date=None,
    )
    apartment_2: Apartment = ApartmentFactory.create(
        building__real_estate__housing_company=housing_company,
        stair="A",
        apartment_number=2,
        completion_date=None,
    )

    url = reverse(
        "hitas:housing-company-batch-complete-apartments",
        kwargs={
            "uuid": housing_company.uuid.hex,
        },
    )

    data = {
        "completion_date": "2020-01-01",
        "apartment_number_start": apartment_number_start,
        "apartment_number_end": apartment_number_end,
    }

    response = api_client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "completed_apartment_count": 2,
    }

    apartment_1.refresh_from_db()
    assert apartment_1.completion_date == date(2020, 1, 1)

    apartment_2.refresh_from_db()
    assert apartment_2.completion_date == date(2020, 1, 1)
