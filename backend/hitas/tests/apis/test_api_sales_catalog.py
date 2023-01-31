from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from django.urls import reverse
from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from rest_framework import status

from hitas.models import ApartmentType, RealEstate
from hitas.tests.apis.helpers import HitasAPIClient, InvalidInput, parametrize_helper
from hitas.tests.factories import ApartmentTypeFactory, RealEstateFactory


@pytest.mark.django_db
def test__api__sales_catalog(api_client: HitasAPIClient):
    real_estate: RealEstate = RealEstateFactory.create()

    # Create necessary apartment types
    apartment_type_1: ApartmentType = ApartmentTypeFactory.create(value="h+k+s")
    apartment_type_2: ApartmentType = ApartmentTypeFactory.create(value="h+kt")

    url = reverse(
        "hitas:sales-catalog-list",
        kwargs={
            "housing_company_uuid": real_estate.housing_company.uuid.hex,
            "real_estate_uuid": real_estate.uuid.hex,
        },
    )
    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    path = Path(__file__).parent.parent / "static" / "mallihinnasto.xlsx"
    data = path.read_bytes()

    response = api_client.post(
        url,
        data=data,
        content_type=content_type,
        openapi_validate_request=False,  # cannot validate requests with bytes
    )

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response.json() == {
        "apartments": [
            {
                "acquisition_price": 275000.0,
                "apartment_number": 1,
                "apartment_type": {
                    "id": apartment_type_1.uuid.hex,
                    "value": "h+k+s",
                },
                "debt_free_purchase_price": 200000.0,
                "floor": "1",
                "primary_loan_amount": 75000.0,
                "rooms": 3,
                "row": 5,
                "share_number_end": 75,
                "share_number_start": 1,
                "stair": "A",
                "surface_area": 75.0,
            },
            {
                "acquisition_price": 175000.0,
                "apartment_number": 2,
                "apartment_type": {
                    "id": apartment_type_1.uuid.hex,
                    "value": "h+k+s",
                },
                "debt_free_purchase_price": 100000.0,
                "floor": "2",
                "primary_loan_amount": 75000.0,
                "rooms": 1,
                "row": 6,
                "share_number_end": 115,
                "share_number_start": 76,
                "stair": "A",
                "surface_area": 40.0,
            },
            {
                "acquisition_price": 225000.0,
                "apartment_number": 3,
                "apartment_type": {
                    "id": apartment_type_2.uuid.hex,
                    "value": "h+kt",
                },
                "debt_free_purchase_price": 150000.0,
                "floor": "3",
                "primary_loan_amount": 75000.0,
                "rooms": 2,
                "row": 7,
                "share_number_end": 180,
                "share_number_start": 116,
                "stair": "A",
                "surface_area": 65.0,
            },
            {
                "acquisition_price": 350000.0,
                "apartment_number": 4,
                "apartment_type": {
                    "id": apartment_type_1.uuid.hex,
                    "value": "h+k+s",
                },
                "debt_free_purchase_price": 250000.0,
                "floor": "4",
                "primary_loan_amount": 100000.0,
                "rooms": 5,
                "row": 8,
                "share_number_end": 280,
                "share_number_start": 181,
                "stair": "A",
                "surface_area": 100.0,
            },
            {
                "acquisition_price": 170000.0,
                "apartment_number": 1,
                "apartment_type": {
                    "id": apartment_type_1.uuid.hex,
                    "value": "h+k+s",
                },
                "debt_free_purchase_price": 95000.0,
                "floor": "5",
                "primary_loan_amount": 75000.0,
                "rooms": 1,
                "row": 9,
                "share_number_end": 320,
                "share_number_start": 281,
                "stair": "B",
                "surface_area": 40.0,
            },
            {
                "acquisition_price": 350000.0,
                "apartment_number": 2,
                "apartment_type": {
                    "id": apartment_type_1.uuid.hex,
                    "value": "h+k+s",
                },
                "debt_free_purchase_price": 250000.0,
                "floor": "6",
                "primary_loan_amount": 100000.0,
                "rooms": 5,
                "row": 10,
                "share_number_end": 420,
                "share_number_start": 321,
                "stair": "B",
                "surface_area": 100.0,
            },
            {
                "acquisition_price": 275000.0,
                "apartment_number": 3,
                "apartment_type": {
                    "id": apartment_type_1.uuid.hex,
                    "value": "h+k+s",
                },
                "debt_free_purchase_price": 200000.0,
                "floor": "7",
                "primary_loan_amount": 75000.0,
                "rooms": 3,
                "row": 11,
                "share_number_end": 495,
                "share_number_start": 421,
                "stair": "B",
                "surface_area": 75.0,
            },
            {
                "acquisition_price": 235000.0,
                "apartment_number": 4,
                "apartment_type": {
                    "id": apartment_type_2.uuid.hex,
                    "value": "h+kt",
                },
                "debt_free_purchase_price": 160000.0,
                "floor": "8",
                "primary_loan_amount": 75000.0,
                "rooms": 2,
                "row": 12,
                "share_number_end": 560,
                "share_number_start": 496,
                "stair": "B",
                "surface_area": 65.0,
            },
        ],
        "confirmation_date": "2021-08-06T00:00:00",
        "realised_acquisition_price": 2060000,
        "total_acquisition_price": 2055000,
        "total_surface_area": 560,
    }


@pytest.mark.django_db
def test__api__sales_catalog__missing_apartment_types(api_client: HitasAPIClient):
    real_estate: RealEstate = RealEstateFactory.create()

    url = reverse(
        "hitas:sales-catalog-list",
        kwargs={
            "housing_company_uuid": real_estate.housing_company.uuid.hex,
            "real_estate_uuid": real_estate.uuid.hex,
        },
    )
    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    path = Path(__file__).parent.parent / "static" / "mallihinnasto.xlsx"
    data = path.read_bytes()

    response = api_client.post(
        url,
        data=data,
        content_type=content_type,
        openapi_validate_request=False,  # cannot validate requests with bytes
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {"field": "E5.apartment_type", "message": "Apartment type h+k+s not found"},
            {"field": "E6.apartment_type", "message": "Apartment type h+k+s not found"},
            {"field": "E7.apartment_type", "message": "Apartment type h+kt not found"},
            {"field": "E8.apartment_type", "message": "Apartment type h+k+s not found"},
            {"field": "E9.apartment_type", "message": "Apartment type h+k+s not found"},
            {"field": "E10.apartment_type", "message": "Apartment type h+k+s not found"},
            {"field": "E11.apartment_type", "message": "Apartment type h+k+s not found"},
            {"field": "E12.apartment_type", "message": "Apartment type h+kt not found"},
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "Missing stair": InvalidInput(
                invalid_data={
                    "A5": None,
                },
                fields=[
                    {
                        "field": "A5.stair",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Missing floor": InvalidInput(
                invalid_data={
                    "B5": None,
                },
                fields=[
                    {
                        "field": "B5.floor",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Missing apartment_number": InvalidInput(
                invalid_data={
                    "C5": None,
                },
                fields=[
                    {
                        "field": "C5.apartment_number",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Missing rooms": InvalidInput(
                invalid_data={
                    "D5": None,
                },
                fields=[
                    {
                        "field": "D5.rooms",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Missing apartment_type": InvalidInput(
                invalid_data={
                    "E5": None,
                },
                fields=[
                    {
                        "field": "E5.apartment_type",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Missing surface_area": InvalidInput(
                invalid_data={
                    "F5": None,
                },
                fields=[
                    {
                        "field": "F5.surface_area",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Missing share_number_start": InvalidInput(
                invalid_data={
                    "G5": None,
                },
                fields=[
                    {
                        "field": "G5.share_number_start",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Missing share_number_end": InvalidInput(
                invalid_data={
                    "H5": None,
                },
                fields=[
                    {
                        "field": "H5.share_number_end",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Missing debt_free_purchase_price": InvalidInput(
                invalid_data={
                    "I5": None,
                },
                fields=[
                    {
                        "field": "I5.debt_free_purchase_price",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Missing primary_loan_amount": InvalidInput(
                invalid_data={
                    "J5": None,
                },
                fields=[
                    {
                        "field": "J5.primary_loan_amount",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Missing acquisition_price": InvalidInput(
                invalid_data={
                    "K5": None,
                },
                fields=[
                    {
                        "field": "K5.acquisition_price",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Missing confirmation_date": InvalidInput(
                invalid_data={
                    "F2": None,
                },
                fields=[
                    {
                        "field": "F2.confirmation_date",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Missing realised_acquisition_price": InvalidInput(
                invalid_data={
                    "E3": None,
                },
                fields=[
                    {
                        "field": "E3.realised_acquisition_price",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Missing total_surface_area": InvalidInput(
                invalid_data={
                    "F13": None,
                },
                fields=[
                    {
                        "field": "F13.total_surface_area",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Missing total_acquisition_price": InvalidInput(
                invalid_data={
                    "K13": None,
                },
                fields=[
                    {
                        "field": "K13.total_acquisition_price",
                        "message": "This field is mandatory and cannot be null.",
                    },
                ],
            ),
            "Share overlap single start": InvalidInput(
                invalid_data={
                    "G6": 75,
                },
                fields=[
                    {
                        "field": "H5.share_number_end",
                        "message": "Overlapping shares with apartment on row 6: 75",
                    },
                    {
                        "field": "G6.share_number_start",
                        "message": "Overlapping shares with apartment on row 5: 75",
                    },
                ],
            ),
            "Share overlap single end": InvalidInput(
                invalid_data={
                    "H5": 76,
                },
                fields=[
                    {
                        "field": "H5.share_number_end",
                        "message": "Overlapping shares with apartment on row 6: 76",
                    },
                    {
                        "field": "G6.share_number_start",
                        "message": "Overlapping shares with apartment on row 5: 76",
                    },
                ],
            ),
            "Share overlap multiple": InvalidInput(
                invalid_data={
                    "G6": 70,
                },
                fields=[
                    {
                        "field": "G5.share_number_start",
                        "message": "Overlapping shares with apartment on row 6: 70-75",
                    },
                    {
                        "field": "G6.share_number_start",
                        "message": "Overlapping shares with apartment on row 5: 70-75",
                    },
                    {
                        "field": "H5.share_number_end",
                        "message": "Overlapping shares with apartment on row 6: 70-75",
                    },
                    {
                        "field": "H6.share_number_end",
                        "message": "Overlapping shares with apartment on row 5: 70-75",
                    },
                ],
            ),
        },
    )
)
@pytest.mark.django_db
def test__api__sales_catalog__invalid_data(api_client: HitasAPIClient, invalid_data, fields):
    real_estate: RealEstate = RealEstateFactory.create()

    # Create necessary apartment types
    ApartmentTypeFactory.create(value="h+k+s")
    ApartmentTypeFactory.create(value="h+kt")

    url = reverse(
        "hitas:sales-catalog-list",
        kwargs={
            "housing_company_uuid": real_estate.housing_company.uuid.hex,
            "real_estate_uuid": real_estate.uuid.hex,
        },
    )
    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    path = Path(__file__).parent.parent / "static" / "mallihinnasto.xlsx"
    wb: Workbook = load_workbook(path, data_only=True)
    ws: Worksheet = wb.worksheets[0]

    for key, value in invalid_data.items():
        ws[key] = value

    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        data: bytes = tmp.read()

    response = api_client.post(
        url,
        data=data,
        content_type=content_type,
        openapi_validate_request=False,  # cannot validate requests with bytes
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": fields,
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }
