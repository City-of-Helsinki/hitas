import datetime
from io import BytesIO
from urllib.parse import urlencode

import pytest
from django.http import HttpResponse
from django.urls import reverse
from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from rest_framework import status

from hitas.models import ApartmentSale
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import ApartmentSaleFactory


@pytest.mark.django_db
def test__api__sales_report__single_sale(api_client: HitasAPIClient):
    # Create sales in the report interval
    sale: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=datetime.date(2020, 1, 1),
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=100,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__postal_code__cost_area=1,
    )

    data = {
        "start_date": "2020-01-01",
        "end_date": "2020-01-31",
    }
    url = reverse("hitas:sales-report-list") + "?" + urlencode(data)
    response: HttpResponse = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    workbook: Workbook = load_workbook(BytesIO(response.content), data_only=False)
    worksheet: Worksheet = workbook.worksheets[0]

    assert list(worksheet.values) == [
        (
            "Kalleusalue",
            "Postinumero",
            "Osoite",
            "Ilmoituspäivä",
            "Kauppapäivä",
            "Kaupan neliöhinta",
            "Velaton neliöhinta",
        ),
        (
            sale.apartment.postal_code.cost_area,
            sale.apartment.postal_code.value,
            sale.apartment.address,
            datetime.datetime.fromisoformat(sale.notification_date.isoformat()),
            datetime.datetime.fromisoformat(sale.purchase_date.isoformat()),
            500,  # 50_000 / 100
            600,  # (50_000 + 10_000) / 100
        ),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kaikki kaupat", "Lukumäärä", 1, 1),
        (None, None, None, None, "Summa", 500, 600),
        (None, None, None, None, "Keskiarvo", 500, 600),
        (None, None, None, None, "Maksimi", 500, 600),
        (None, None, None, None, "Minimi", 500, 600),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 1", "Lukumäärä", 1, 1),
        (None, None, None, None, "Summa", 500, 600),
        (None, None, None, None, "Keskiarvo", 500, 600),
        (None, None, None, None, "Maksimi", 500, 600),
        (None, None, None, None, "Minimi", 500, 600),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 2", "Lukumäärä", 0, 0),
        (None, None, None, None, "Summa", 0, 0),
        (None, None, None, None, "Keskiarvo", 0, 0),
        (None, None, None, None, "Maksimi", 0, 0),
        (None, None, None, None, "Minimi", 0, 0),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 3", "Lukumäärä", 0, 0),
        (None, None, None, None, "Summa", 0, 0),
        (None, None, None, None, "Keskiarvo", 0, 0),
        (None, None, None, None, "Maksimi", 0, 0),
        (None, None, None, None, "Minimi", 0, 0),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 4", "Lukumäärä", 0, 0),
        (None, None, None, None, "Summa", 0, 0),
        (None, None, None, None, "Keskiarvo", 0, 0),
        (None, None, None, None, "Maksimi", 0, 0),
        (None, None, None, None, "Minimi", 0, 0),
    ]


@pytest.mark.django_db
def test__api__sales_report__multiple_sales(api_client: HitasAPIClient):
    # Create sales in the report interval
    sale_1: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=datetime.date(2020, 1, 1),
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=100,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__postal_code__cost_area=1,
    )
    sale_2: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=datetime.date(2020, 1, 15),
        purchase_price=130_000,
        apartment_share_of_housing_company_loans=100,
        apartment__surface_area=100,
        apartment__building__real_estate__housing_company__postal_code__value="00002",
        apartment__building__real_estate__housing_company__postal_code__cost_area=1,
    )

    data = {
        "start_date": "2020-01-01",
        "end_date": "2020-01-31",
    }
    url = reverse("hitas:sales-report-list") + "?" + urlencode(data)
    response: HttpResponse = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    workbook: Workbook = load_workbook(BytesIO(response.content), data_only=False)
    worksheet: Worksheet = workbook.worksheets[0]

    assert list(worksheet.values) == [
        (
            "Kalleusalue",
            "Postinumero",
            "Osoite",
            "Ilmoituspäivä",
            "Kauppapäivä",
            "Kaupan neliöhinta",
            "Velaton neliöhinta",
        ),
        (
            sale_1.apartment.postal_code.cost_area,
            sale_1.apartment.postal_code.value,
            sale_1.apartment.address,
            datetime.datetime.fromisoformat(sale_1.notification_date.isoformat()),
            datetime.datetime.fromisoformat(sale_1.purchase_date.isoformat()),
            500,  # 50_000 / 100
            600,  # (50_000 + 10_000) / 100
        ),
        (
            sale_2.apartment.postal_code.cost_area,
            sale_2.apartment.postal_code.value,
            sale_2.apartment.address,
            datetime.datetime.fromisoformat(sale_2.notification_date.isoformat()),
            datetime.datetime.fromisoformat(sale_2.purchase_date.isoformat()),
            1300,  # 130_000 / 100
            1301,  # (130_000 + 100) / 100
        ),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kaikki kaupat", "Lukumäärä", 2, 2),
        (None, None, None, None, "Summa", 1800, 1901),
        (None, None, None, None, "Keskiarvo", 900, 950.5),
        (None, None, None, None, "Maksimi", 1300, 1301),
        (None, None, None, None, "Minimi", 500, 600),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 1", "Lukumäärä", 2, 2),
        (None, None, None, None, "Summa", 1800, 1901),
        (None, None, None, None, "Keskiarvo", 900, 950.5),
        (None, None, None, None, "Maksimi", 1300, 1301),
        (None, None, None, None, "Minimi", 500, 600),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 2", "Lukumäärä", 0, 0),
        (None, None, None, None, "Summa", 0, 0),
        (None, None, None, None, "Keskiarvo", 0, 0),
        (None, None, None, None, "Maksimi", 0, 0),
        (None, None, None, None, "Minimi", 0, 0),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 3", "Lukumäärä", 0, 0),
        (None, None, None, None, "Summa", 0, 0),
        (None, None, None, None, "Keskiarvo", 0, 0),
        (None, None, None, None, "Maksimi", 0, 0),
        (None, None, None, None, "Minimi", 0, 0),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 4", "Lukumäärä", 0, 0),
        (None, None, None, None, "Summa", 0, 0),
        (None, None, None, None, "Keskiarvo", 0, 0),
        (None, None, None, None, "Maksimi", 0, 0),
        (None, None, None, None, "Minimi", 0, 0),
    ]


@pytest.mark.django_db
def test__api__sales_report__multiple_sales__one_excluded_from_sales(api_client: HitasAPIClient):
    # Create sales in the report interval
    sale_1: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=datetime.date(2020, 1, 1),
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=100,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__postal_code__cost_area=1,
    )
    # Sale not included even though in the report interval because of exclude_from_statistics
    ApartmentSaleFactory.create(
        purchase_date=datetime.date(2020, 1, 15),
        purchase_price=130_000,
        exclude_from_statistics=True,
        apartment_share_of_housing_company_loans=100,
        apartment__surface_area=100,
        apartment__building__real_estate__housing_company__postal_code__value="00002",
        apartment__building__real_estate__housing_company__postal_code__cost_area=1,
    )

    data = {
        "start_date": "2020-01-01",
        "end_date": "2020-01-31",
    }
    url = reverse("hitas:sales-report-list") + "?" + urlencode(data)
    response: HttpResponse = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    workbook: Workbook = load_workbook(BytesIO(response.content), data_only=False)
    worksheet: Worksheet = workbook.worksheets[0]

    assert list(worksheet.values) == [
        (
            "Kalleusalue",
            "Postinumero",
            "Osoite",
            "Ilmoituspäivä",
            "Kauppapäivä",
            "Kaupan neliöhinta",
            "Velaton neliöhinta",
        ),
        (
            sale_1.apartment.postal_code.cost_area,
            sale_1.apartment.postal_code.value,
            sale_1.apartment.address,
            datetime.datetime.fromisoformat(sale_1.notification_date.isoformat()),
            datetime.datetime.fromisoformat(sale_1.purchase_date.isoformat()),
            500,  # 50_000 / 100
            600,  # (50_000 + 10_000) / 100
        ),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kaikki kaupat", "Lukumäärä", 1, 1),
        (None, None, None, None, "Summa", 500, 600),
        (None, None, None, None, "Keskiarvo", 500, 600),
        (None, None, None, None, "Maksimi", 500, 600),
        (None, None, None, None, "Minimi", 500, 600),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 1", "Lukumäärä", 1, 1),
        (None, None, None, None, "Summa", 500, 600),
        (None, None, None, None, "Keskiarvo", 500, 600),
        (None, None, None, None, "Maksimi", 500, 600),
        (None, None, None, None, "Minimi", 500, 600),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 2", "Lukumäärä", 0, 0),
        (None, None, None, None, "Summa", 0, 0),
        (None, None, None, None, "Keskiarvo", 0, 0),
        (None, None, None, None, "Maksimi", 0, 0),
        (None, None, None, None, "Minimi", 0, 0),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 3", "Lukumäärä", 0, 0),
        (None, None, None, None, "Summa", 0, 0),
        (None, None, None, None, "Keskiarvo", 0, 0),
        (None, None, None, None, "Maksimi", 0, 0),
        (None, None, None, None, "Minimi", 0, 0),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 4", "Lukumäärä", 0, 0),
        (None, None, None, None, "Summa", 0, 0),
        (None, None, None, None, "Keskiarvo", 0, 0),
        (None, None, None, None, "Maksimi", 0, 0),
        (None, None, None, None, "Minimi", 0, 0),
    ]


@pytest.mark.django_db
def test__api__sales_report__multiple_sales__one_out_of_interval(api_client: HitasAPIClient):
    # Create sales in the report interval
    sale: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=datetime.date(2020, 1, 1),
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=100,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__postal_code__cost_area=1,
    )
    ApartmentSaleFactory.create(
        purchase_date=datetime.date(2020, 2, 1),
        purchase_price=130_000,
        apartment_share_of_housing_company_loans=100,
        apartment__surface_area=100,
        apartment__building__real_estate__housing_company__postal_code__value="00002",
        apartment__building__real_estate__housing_company__postal_code__cost_area=1,
    )

    data = {
        "start_date": "2020-01-01",
        "end_date": "2020-01-31",
    }
    url = reverse("hitas:sales-report-list") + "?" + urlencode(data)
    response: HttpResponse = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    workbook: Workbook = load_workbook(BytesIO(response.content), data_only=False)
    worksheet: Worksheet = workbook.worksheets[0]

    assert list(worksheet.values) == [
        (
            "Kalleusalue",
            "Postinumero",
            "Osoite",
            "Ilmoituspäivä",
            "Kauppapäivä",
            "Kaupan neliöhinta",
            "Velaton neliöhinta",
        ),
        (
            sale.apartment.postal_code.cost_area,
            sale.apartment.postal_code.value,
            sale.apartment.address,
            datetime.datetime.fromisoformat(sale.notification_date.isoformat()),
            datetime.datetime.fromisoformat(sale.purchase_date.isoformat()),
            500,  # 50_000 / 100
            600,  # (50_000 + 10_000) / 100
        ),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kaikki kaupat", "Lukumäärä", 1, 1),
        (None, None, None, None, "Summa", 500, 600),
        (None, None, None, None, "Keskiarvo", 500, 600),
        (None, None, None, None, "Maksimi", 500, 600),
        (None, None, None, None, "Minimi", 500, 600),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 1", "Lukumäärä", 1, 1),
        (None, None, None, None, "Summa", 500, 600),
        (None, None, None, None, "Keskiarvo", 500, 600),
        (None, None, None, None, "Maksimi", 500, 600),
        (None, None, None, None, "Minimi", 500, 600),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 2", "Lukumäärä", 0, 0),
        (None, None, None, None, "Summa", 0, 0),
        (None, None, None, None, "Keskiarvo", 0, 0),
        (None, None, None, None, "Maksimi", 0, 0),
        (None, None, None, None, "Minimi", 0, 0),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 3", "Lukumäärä", 0, 0),
        (None, None, None, None, "Summa", 0, 0),
        (None, None, None, None, "Keskiarvo", 0, 0),
        (None, None, None, None, "Maksimi", 0, 0),
        (None, None, None, None, "Minimi", 0, 0),
        (None, None, None, None, None, None, None),
        (None, None, None, "Kalleusalue 4", "Lukumäärä", 0, 0),
        (None, None, None, None, "Summa", 0, 0),
        (None, None, None, None, "Keskiarvo", 0, 0),
        (None, None, None, None, "Maksimi", 0, 0),
        (None, None, None, None, "Minimi", 0, 0),
    ]


@pytest.mark.django_db
def test__api__sales_report__start_date_after_end_date(api_client: HitasAPIClient):
    # Create sales in the report interval
    ApartmentSaleFactory.create(
        purchase_date=datetime.date(2020, 1, 1),
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=100,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__postal_code__cost_area=1,
    )

    data = {
        "start_date": "2020-01-31",
        "end_date": "2020-01-01",
    }
    url = reverse("hitas:sales-report-list") + "?" + urlencode(data)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "non_field_errors",
                "message": "Start date must be before end date",
            },
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__sales_report__surface_area_missing(api_client: HitasAPIClient):
    # Create sales in the report interval
    sale: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=datetime.date(2020, 1, 1),
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=None,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__postal_code__cost_area=1,
    )

    data = {
        "start_date": "2020-01-01",
        "end_date": "2020-01-31",
    }
    url = reverse("hitas:sales-report-list") + "?" + urlencode(data)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "non_field_errors",
                "message": (
                    f"Surface are zero or missing for apartment {sale.apartment.address!r}. "
                    f"Cannot calculate price per square meter."
                ),
            }
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }
