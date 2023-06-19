import datetime
from decimal import Decimal
from unittest.mock import ANY, patch

import pytest
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from rest_framework import status

from hitas.models import (
    Apartment,
    ApartmentMaximumPriceCalculation,
    ApartmentSale,
    ConstructionPriceIndex2005Equal100,
    JobPerformance,
    MarketPriceIndex2005Equal100,
    SurfaceAreaPriceCeiling,
    ThirtyYearRegulationResults,
    ThirtyYearRegulationResultsRow,
)
from hitas.models.email_template import EmailTemplate, EmailTemplateType
from hitas.models.housing_company import HitasType, RegulationStatus
from hitas.models.pdf_body import PDFBodyName
from hitas.models.thirty_year_regulation import RegulationResult
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.factories import ApartmentSaleFactory, EmailTemplateFactory, PDFBodyFactory
from hitas.tests.factories.apartment import ApartmentFactory, create_apartment_max_price_calculation
from hitas.tests.factories.indices import (
    ConstructionPriceIndex2005Equal100Factory,
    MarketPriceIndex2005Equal100Factory,
    SurfaceAreaPriceCeilingFactory,
)


@pytest.mark.django_db
def test__api__send_confirmed_max_price_email(api_client: HitasAPIClient):
    max_price_calculation: ApartmentMaximumPriceCalculation = create_apartment_max_price_calculation()
    PDFBodyFactory.create(
        name=PDFBodyName.CONFIRMED_MAX_PRICE_CALCULATION,
        texts=["||foo||"],
    )
    template: EmailTemplate = EmailTemplateFactory.create(
        name="foo",
        type=EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION,
    )

    url = reverse("hitas:confirmed-max-price-calculation-email-list")
    data = {
        "calculation_id": max_price_calculation.uuid.hex,
        "request_date": datetime.date.today().isoformat(),
        "template_name": template.name,
        "recipients": ["test@email.com"],
    }

    with patch("hitas.services.email.send_pdf_via_email", return_value=None) as mock:
        response = api_client.post(url, data=data, format="json")

    mock.assert_called_once_with(
        body=template.text,
        recipients=["test@email.com"],
        filename=f"Enimmäishintalaskelma {max_price_calculation.apartment.address}.pdf",
        pdf=ANY,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    assert JobPerformance.objects.count() == 1


@pytest.mark.django_db
def test__api__send_confirmed_max_price_email__pdf_body_not_found(api_client: HitasAPIClient):
    max_price_calculation: ApartmentMaximumPriceCalculation = create_apartment_max_price_calculation()
    template: EmailTemplate = EmailTemplateFactory.create(
        name="foo",
        type=EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION,
    )

    url = reverse("hitas:confirmed-max-price-calculation-email-list")
    data = {
        "calculation_id": max_price_calculation.uuid.hex,
        "request_date": datetime.date.today().isoformat(),
        "template_name": template.name,
        "recipients": ["test@email.com"],
    }

    with patch("hitas.services.email.send_pdf_via_email", return_value=None):
        response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "pdf_body_not_found",
        "message": "PDF body not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__send_confirmed_max_price_email__email_template_not_found(api_client: HitasAPIClient):
    max_price_calculation: ApartmentMaximumPriceCalculation = create_apartment_max_price_calculation()
    PDFBodyFactory.create(
        name=PDFBodyName.CONFIRMED_MAX_PRICE_CALCULATION,
        texts=["||foo||"],
    )

    url = reverse("hitas:confirmed-max-price-calculation-email-list")
    data = {
        "calculation_id": max_price_calculation.uuid.hex,
        "request_date": datetime.date.today().isoformat(),
        "template_name": "foo",
        "recipients": ["test@email.com"],
    }

    with patch("hitas.services.email.send_pdf_via_email", return_value=None):
        response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "email_template_not_found",
        "message": "Email template not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__send_unconfirmed_max_price_email(api_client: HitasAPIClient, freezer):
    freezer.move_to("2022-01-01")

    apartment: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2021, 1, 1),
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    PDFBodyFactory.create(
        name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION,
        texts=["||foo||", "||bar||", "||baz||"],
    )
    template: EmailTemplate = EmailTemplateFactory.create(
        name="foo",
        type=EmailTemplateType.UNCONFIRMED_MAX_PRICE_CALCULATION,
    )

    this_month = datetime.date.today().replace(day=1)
    completion_month = apartment.completion_date.replace(day=1)

    ConstructionPriceIndex2005Equal100Factory.create(month=completion_month, value=100)
    MarketPriceIndex2005Equal100Factory.create(month=completion_month, value=200)
    ConstructionPriceIndex2005Equal100Factory.create(month=this_month, value=150)
    MarketPriceIndex2005Equal100Factory.create(month=this_month, value=250)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=3000)

    url = reverse("hitas:unconfirmed-max-price-calculation-email-list")
    data = {
        "apartment_id": apartment.uuid.hex,
        "calculation_date": this_month.isoformat(),
        "request_date": datetime.date.today().isoformat(),
        "additional_info": "foo",
        "template_name": template.name,
        "recipients": ["test@email.com"],
    }

    with patch("hitas.services.email.send_pdf_via_email", return_value=None) as mock:
        response = api_client.post(url, data=data, format="json")

    mock.assert_called_once_with(
        body=template.text,
        recipients=["test@email.com"],
        filename=f"Hinta-arvio {apartment.address}.pdf",
        pdf=ANY,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    assert JobPerformance.objects.count() == 1


@pytest.mark.django_db
def test__api__send_unconfirmed_max_price_email__pdf_body_not_found(api_client: HitasAPIClient, freezer):
    freezer.move_to("2022-01-01")

    apartment: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2021, 1, 1),
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    template: EmailTemplate = EmailTemplateFactory.create(
        name="foo",
        type=EmailTemplateType.UNCONFIRMED_MAX_PRICE_CALCULATION,
    )

    this_month = datetime.date.today().replace(day=1)
    completion_month = apartment.completion_date.replace(day=1)

    ConstructionPriceIndex2005Equal100Factory.create(month=completion_month, value=100)
    MarketPriceIndex2005Equal100Factory.create(month=completion_month, value=200)
    ConstructionPriceIndex2005Equal100Factory.create(month=this_month, value=150)
    MarketPriceIndex2005Equal100Factory.create(month=this_month, value=250)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=3000)

    url = reverse("hitas:unconfirmed-max-price-calculation-email-list")
    data = {
        "apartment_id": apartment.uuid.hex,
        "calculation_date": this_month.isoformat(),
        "request_date": datetime.date.today().isoformat(),
        "additional_info": "foo",
        "template_name": template.name,
        "recipients": ["test@email.com"],
    }

    with patch("hitas.services.email.send_pdf_via_email", return_value=None):
        response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "pdf_body_not_found",
        "message": "PDF body not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__send_unconfirmed_max_price_email__email_template_not_found(api_client: HitasAPIClient, freezer):
    freezer.move_to("2022-01-01")

    apartment: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2021, 1, 1),
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    PDFBodyFactory.create(
        name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION,
        texts=["||foo||", "||bar||", "||baz||"],
    )

    this_month = datetime.date.today().replace(day=1)
    completion_month = apartment.completion_date.replace(day=1)

    ConstructionPriceIndex2005Equal100Factory.create(month=completion_month, value=100)
    MarketPriceIndex2005Equal100Factory.create(month=completion_month, value=200)
    ConstructionPriceIndex2005Equal100Factory.create(month=this_month, value=150)
    MarketPriceIndex2005Equal100Factory.create(month=this_month, value=250)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=3000)

    url = reverse("hitas:unconfirmed-max-price-calculation-email-list")
    data = {
        "apartment_id": apartment.uuid.hex,
        "calculation_date": this_month.isoformat(),
        "request_date": datetime.date.today().isoformat(),
        "additional_info": "foo",
        "template_name": "foo",
        "recipients": ["test@email.com"],
    }

    with patch("hitas.services.email.send_pdf_via_email", return_value=None):
        response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "email_template_not_found",
        "message": "Email template not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.parametrize(
    ["index", "error"],
    [
        [
            ConstructionPriceIndex2005Equal100,
            {
                "error": "construction_price_index_year_for_apartments_constructed_in_january_2005_onwards_not_found",
                "message": "Construction price index year for apartments constructed in January 2005 onwards not found",
                "reason": "Not Found",
                "status": 404,
            },
        ],
        [
            MarketPriceIndex2005Equal100,
            {
                "error": "market_price_index_for_apartments_constructed_in_january_2011_onwards_not_found",
                "message": "Market price index for apartments constructed in January 2011 onwards not found",
                "reason": "Not Found",
                "status": 404,
            },
        ],
        [
            SurfaceAreaPriceCeiling,
            {
                "error": "surface_area_price_ceiling_not_found",
                "message": "Surface area price ceiling not found",
                "reason": "Not Found",
                "status": 404,
            },
        ],
    ],
)
@pytest.mark.django_db
def test__api__send_unconfirmed_max_price_email__indices_missing(api_client: HitasAPIClient, freezer, index, error):
    freezer.move_to("2022-01-01")

    apartment: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2021, 1, 1),
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
    )
    PDFBodyFactory.create(
        name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION,
        texts=["||foo||", "||bar||", "||baz||"],
    )
    template: EmailTemplate = EmailTemplateFactory.create(
        name="foo",
        type=EmailTemplateType.UNCONFIRMED_MAX_PRICE_CALCULATION,
    )

    this_month = datetime.date.today().replace(day=1)
    completion_month = apartment.completion_date.replace(day=1)

    if index != ConstructionPriceIndex2005Equal100:
        ConstructionPriceIndex2005Equal100Factory.create(month=completion_month, value=100)
        ConstructionPriceIndex2005Equal100Factory.create(month=this_month, value=150)
    if index != MarketPriceIndex2005Equal100:
        MarketPriceIndex2005Equal100Factory.create(month=this_month, value=250)
        MarketPriceIndex2005Equal100Factory.create(month=completion_month, value=200)
    if index != SurfaceAreaPriceCeiling:
        SurfaceAreaPriceCeilingFactory.create(month=this_month, value=3000)

    url = reverse("hitas:unconfirmed-max-price-calculation-email-list")
    data = {
        "apartment_id": apartment.uuid.hex,
        "calculation_date": this_month.isoformat(),
        "request_date": datetime.date.today().isoformat(),
        "additional_info": "foo",
        "template_name": template.name,
        "recipients": ["test@email.com"],
    }

    with patch("hitas.services.email.send_pdf_via_email", return_value=None):
        response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == error


@pytest.mark.django_db
def test__api__send_regulation_letter__stays_regulated(api_client: HitasAPIClient, freezer):
    freezer.move_to("2022-02-01")

    this_month = datetime.date.today().replace(day=1)
    regulation_month = this_month - relativedelta(years=30)

    sale: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    result = ThirtyYearRegulationResults.objects.create(
        regulation_month=regulation_month,
        calculation_month=this_month,
        surface_area_price_ceiling=Decimal("5000.00"),
        sales_data={
            "external": {},
            "internal": {"00001": {"2022Q4": {"price": 49000.0, "sale_count": 1}}},
            "price_by_area": {"00001": 49000.0},
        },
        replacement_postal_codes=[],
    )

    row = ThirtyYearRegulationResultsRow.objects.create(
        parent=result,
        housing_company=sale.apartment.housing_company,
        completion_date=regulation_month,
        surface_area=Decimal("10.00"),
        postal_code="00001",
        realized_acquisition_price=Decimal("60000.00"),
        unadjusted_average_price_per_square_meter=Decimal("6000.00"),
        adjusted_average_price_per_square_meter=Decimal("12000.00"),
        completion_month_index=Decimal("100.00"),
        calculation_month_index=Decimal("200.00"),
        regulation_result=RegulationResult.STAYS_REGULATED,
        letter_fetched=False,
    )

    template: EmailTemplate = EmailTemplateFactory.create(
        name="foo",
        type=EmailTemplateType.STAYS_REGULATED,
    )

    PDFBodyFactory.create(name=PDFBodyName.STAYS_REGULATED)

    url = reverse("hitas:regulation-letter-email-list")
    data = {
        "housing_company_id": row.housing_company.uuid.hex,
        "calculation_date": this_month.isoformat(),
        "template_name": template.name,
        "recipients": ["test@email.com"],
    }

    with patch("hitas.services.email.send_pdf_via_email", return_value=None) as mock:
        response = api_client.post(url, data=data, format="json")

    mock.assert_called_once_with(
        body=template.text,
        recipients=["test@email.com"],
        filename=f"Tiedote sääntelyn jatkumisesta - {row.housing_company.display_name}.pdf",
        pdf=ANY,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()


@pytest.mark.django_db
def test__api__send_regulation_letter__stays_regulated__email_template_missing(api_client: HitasAPIClient, freezer):
    freezer.move_to("2022-02-01")

    this_month = datetime.date.today().replace(day=1)
    regulation_month = this_month - relativedelta(years=30)

    sale: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    result = ThirtyYearRegulationResults.objects.create(
        regulation_month=regulation_month,
        calculation_month=this_month,
        surface_area_price_ceiling=Decimal("5000.00"),
        sales_data={
            "external": {},
            "internal": {"00001": {"2022Q4": {"price": 49000.0, "sale_count": 1}}},
            "price_by_area": {"00001": 49000.0},
        },
        replacement_postal_codes=[],
    )

    row = ThirtyYearRegulationResultsRow.objects.create(
        parent=result,
        housing_company=sale.apartment.housing_company,
        completion_date=regulation_month,
        surface_area=Decimal("10.00"),
        postal_code="00001",
        realized_acquisition_price=Decimal("60000.00"),
        unadjusted_average_price_per_square_meter=Decimal("6000.00"),
        adjusted_average_price_per_square_meter=Decimal("12000.00"),
        completion_month_index=Decimal("100.00"),
        calculation_month_index=Decimal("200.00"),
        regulation_result=RegulationResult.STAYS_REGULATED,
        letter_fetched=False,
    )

    PDFBodyFactory.create(name=PDFBodyName.STAYS_REGULATED)

    url = reverse("hitas:regulation-letter-email-list")
    data = {
        "housing_company_id": row.housing_company.uuid.hex,
        "calculation_date": this_month.isoformat(),
        "template_name": "foo",
        "recipients": ["test@email.com"],
    }

    with patch("hitas.services.email.send_pdf_via_email", return_value=None):
        response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "email_template_not_found",
        "message": "Email template not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__send_regulation_letter__released_from_regulation(api_client: HitasAPIClient, freezer):
    freezer.move_to("2022-02-01")

    this_month = datetime.date.today().replace(day=1)
    regulation_month = this_month - relativedelta(years=30)

    sale: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    result = ThirtyYearRegulationResults.objects.create(
        regulation_month=regulation_month,
        calculation_month=this_month,
        surface_area_price_ceiling=Decimal("5000.00"),
        sales_data={
            "external": {},
            "internal": {"00001": {"2022Q4": {"price": 4900.0, "sale_count": 1}}},
            "price_by_area": {"00001": 4900.0},
        },
        replacement_postal_codes=[],
    )

    row = ThirtyYearRegulationResultsRow.objects.create(
        parent=result,
        housing_company=sale.apartment.housing_company,
        completion_date=regulation_month,
        surface_area=Decimal("10.00"),
        postal_code="00001",
        realized_acquisition_price=Decimal("60000.00"),
        unadjusted_average_price_per_square_meter=Decimal("6000.00"),
        adjusted_average_price_per_square_meter=Decimal("12000.00"),
        completion_month_index=Decimal("100.00"),
        calculation_month_index=Decimal("200.00"),
        regulation_result=RegulationResult.RELEASED_FROM_REGULATION,
    )

    template: EmailTemplate = EmailTemplateFactory.create(
        name="foo",
        type=EmailTemplateType.RELEASED_FROM_REGULATION,
    )

    PDFBodyFactory.create(name=PDFBodyName.RELEASED_FROM_REGULATION)

    url = reverse("hitas:regulation-letter-email-list")
    data = {
        "housing_company_id": row.housing_company.uuid.hex,
        "calculation_date": this_month.isoformat(),
        "template_name": template.name,
        "recipients": ["test@email.com"],
    }

    with patch("hitas.services.email.send_pdf_via_email", return_value=None) as mock:
        response = api_client.post(url, data=data, format="json")

    mock.assert_called_once_with(
        body=template.text,
        recipients=["test@email.com"],
        filename=f"Tiedote sääntelyn pättymisestä - {row.housing_company.display_name}.pdf",
        pdf=ANY,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()


@pytest.mark.django_db
def test__api__send_regulation_letter__released_from_regulation__email_template_missing(
    api_client: HitasAPIClient, freezer
):
    freezer.move_to("2022-02-01")

    this_month = datetime.date.today().replace(day=1)
    regulation_month = this_month - relativedelta(years=30)

    sale: ApartmentSale = ApartmentSaleFactory.create(
        purchase_date=regulation_month,
        purchase_price=50_000,
        apartment_share_of_housing_company_loans=10_000,
        apartment__surface_area=10,
        apartment__completion_date=regulation_month,
        apartment__building__real_estate__housing_company__postal_code__value="00001",
        apartment__building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED,
    )

    result = ThirtyYearRegulationResults.objects.create(
        regulation_month=regulation_month,
        calculation_month=this_month,
        surface_area_price_ceiling=Decimal("5000.00"),
        sales_data={
            "external": {},
            "internal": {"00001": {"2022Q4": {"price": 4900.0, "sale_count": 1}}},
            "price_by_area": {"00001": 4900.0},
        },
        replacement_postal_codes=[],
    )

    row = ThirtyYearRegulationResultsRow.objects.create(
        parent=result,
        housing_company=sale.apartment.housing_company,
        completion_date=regulation_month,
        surface_area=Decimal("10.00"),
        postal_code="00001",
        realized_acquisition_price=Decimal("60000.00"),
        unadjusted_average_price_per_square_meter=Decimal("6000.00"),
        adjusted_average_price_per_square_meter=Decimal("12000.00"),
        completion_month_index=Decimal("100.00"),
        calculation_month_index=Decimal("200.00"),
        regulation_result=RegulationResult.RELEASED_FROM_REGULATION,
    )

    PDFBodyFactory.create(name=PDFBodyName.RELEASED_FROM_REGULATION)

    url = reverse("hitas:regulation-letter-email-list")
    data = {
        "housing_company_id": row.housing_company.uuid.hex,
        "calculation_date": this_month.isoformat(),
        "template_name": "foo",
        "recipients": ["test@email.com"],
    }

    with patch("hitas.services.email.send_pdf_via_email", return_value=None):
        response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "email_template_not_found",
        "message": "Email template not found",
        "reason": "Not Found",
        "status": 404,
    }
