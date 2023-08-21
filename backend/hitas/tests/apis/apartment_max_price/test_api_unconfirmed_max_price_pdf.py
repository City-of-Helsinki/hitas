# ruff: noqa: E501
import datetime
from inspect import cleandoc
from io import BytesIO
from typing import Literal, NamedTuple

import pytest
from django.urls import reverse
from django.utils import timezone
from pypdf import PdfReader
from rest_framework import status

from hitas.models import Apartment, Ownership
from hitas.models.housing_company import HitasType
from hitas.models.pdf_body import PDFBodyName
from hitas.tests.apis.helpers import HitasAPIClient, parametrize_helper
from hitas.tests.factories import ApartmentFactory, PDFBodyFactory
from hitas.tests.factories.indices import (
    ConstructionPriceIndex2005Equal100Factory,
    ConstructionPriceIndexFactory,
    MarketPriceIndex2005Equal100Factory,
    MarketPriceIndexFactory,
    SurfaceAreaPriceCeilingFactory,
)
from users.models import User


@pytest.mark.django_db
def test__api__unconfirmed_max_price_pdf(api_client: HitasAPIClient, freezer):
    freezer.move_to("2022-01-01")
    api_user: User = api_client.handler._force_user

    apartment: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2021, 1, 1),
        additional_work_during_construction=5000,
        interest_during_construction_mpi=1000,
        interest_during_construction_cpi=2000,
        surface_area=50,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        sales__purchase_price=80000,
        sales__apartment_share_of_housing_company_loans=15000,
    )

    ownership: Ownership = apartment.latest_sale(include_first_sale=True).ownerships.first()

    body = PDFBodyFactory.create(
        name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION,
        texts=["||foo||", "||bar||", "||baz||"],
    )

    this_month = datetime.date.today().replace(day=1)
    completion_month = apartment.completion_date.replace(day=1)

    # Completion month indices
    ConstructionPriceIndex2005Equal100Factory.create(month=completion_month, value=100)
    MarketPriceIndex2005Equal100Factory.create(month=completion_month, value=200)
    # Current month indices
    ConstructionPriceIndex2005Equal100Factory.create(month=this_month, value=150)
    MarketPriceIndex2005Equal100Factory.create(month=this_month, value=250)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=3000)

    url = reverse(
        "hitas:apartment-download-latest-unconfirmed-prices",
        kwargs={"housing_company_uuid": apartment.housing_company.uuid.hex, "uuid": apartment.uuid.hex},
    )

    data = {
        "request_date": "2022-01-01",
        "additional_info": "This is additional information",
    }

    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response["content-type"] == "application/pdf"

    letter = PdfReader(BytesIO(response.content))
    assert len(letter.pages) == 1

    page_1 = letter.pages[0].extract_text()
    page_1 = cleandoc("\n".join(item.strip() for item in page_1.split("\n")))

    assert page_1 == cleandoc(
        f"""
        01.01.2022
        Postiosoite
        Käyntiosoite
        Puh. (09) 310 13033
        Asuntopalvelut
        Työpajankatu 8
        Email hitas@hel.fi
        PL 58231
        00580 Helsinki
        Url http://www.hel.fi/hitas
        00099 HELSINGIN KAUPUNKI
        {apartment.address}
        {apartment.postal_code.value} HELSINKI
        HITAS-HUONEISTON ENIMMÄISHINTA
        \x7f ilman yhtiökohtaisia parannuksia ja mahdollista yhtiölainaosuutta
        Omistaja ja omistusosuus (%)
        {ownership.owner.name}
        {float(ownership.percentage):.2f}

        Asunto-osakeyhtiö
        {apartment.housing_company.display_name}, Helsinki
        Huoneiston osoite
        {apartment.address}, {apartment.postal_code.value} HELSINKI
        Huoneiston valmistumisajankohta
        {apartment.completion_date.strftime("%d.%m.%Y")}
        Huoneiston ensimmäinen kaupantekoajankohta
        {apartment.first_sale().purchase_date.strftime("%d.%m.%Y")}
        Alkuperäinen velaton hankintahinta, euroa
        95 000,00
        Rakennuttajalta tilatut lisä- ja muutostyöt
        5 000,00
        Hitas-huoneiston hinta rakennuskustannusindeksillä
        laskettuna, euroa
        150 000,00
        This is additional information
        Hitas-huoneistonne velaton enimmäishinta on 150 000 euroa rakennuskustannusindeksillä laskettuna.
        {body.texts[0]}
        {body.texts[1]}
        {body.texts[2]}
        {api_user.first_name} {api_user.last_name}
        {api_user.title}
        """
    )


@pytest.mark.django_db
def test__api__unconfirmed_max_price_pdf__old_hitas_ruleset(api_client: HitasAPIClient, freezer):
    freezer.move_to("2022-01-01")
    api_user: User = api_client.handler._force_user

    apartment: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2010, 1, 1),
        additional_work_during_construction=5000,
        interest_during_construction_mpi=1000,
        interest_during_construction_cpi=2000,
        surface_area=50,
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        sales__purchase_price=80000,
        sales__apartment_share_of_housing_company_loans=15000,
    )

    # Create another apartment with a later completion date.
    # As Old-Hitas rules use the apartment completion date for the maximum price calculation,
    # this apartment should not affect the calculation.
    ApartmentFactory.create(
        completion_date=datetime.date(2011, 1, 1),
        building__real_estate__housing_company=apartment.housing_company,
    )

    ownership: Ownership = apartment.latest_sale(include_first_sale=True).ownerships.first()

    body = PDFBodyFactory.create(
        name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION,
        texts=["||foo||", "||bar||", "||baz||"],
    )

    this_month = timezone.now().date().replace(day=1)
    completion_month = apartment.completion_date.replace(day=1)

    # Completion month indices
    ConstructionPriceIndexFactory.create(month=completion_month, value=100)
    MarketPriceIndexFactory.create(month=completion_month, value=200)
    # Current month indices
    ConstructionPriceIndexFactory.create(month=this_month, value=150)
    MarketPriceIndexFactory.create(month=this_month, value=250)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=3000)

    url = reverse(
        "hitas:apartment-download-latest-unconfirmed-prices",
        kwargs={"housing_company_uuid": apartment.housing_company.uuid.hex, "uuid": apartment.uuid.hex},
    )

    data = {
        "request_date": "2022-01-01",
        "additional_info": "This is additional information",
    }

    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response["content-type"] == "application/pdf"

    letter = PdfReader(BytesIO(response.content))
    assert len(letter.pages) == 1

    page_1 = letter.pages[0].extract_text()
    page_1 = cleandoc("\n".join(item.strip() for item in page_1.split("\n")))

    assert page_1 == cleandoc(
        f"""
        01.01.2022
        Postiosoite
        Käyntiosoite
        Puh. (09) 310 13033
        Asuntopalvelut
        Työpajankatu 8
        Email hitas@hel.fi
        PL 58231
        00580 Helsinki
        Url http://www.hel.fi/hitas
        00099 HELSINGIN KAUPUNKI
        {apartment.address}
        {apartment.postal_code.value} HELSINKI
        HITAS-HUONEISTON ENIMMÄISHINTA
        \x7f ilman yhtiökohtaisia parannuksia ja mahdollista yhtiölainaosuutta
        Omistaja ja omistusosuus (%)
        {ownership.owner.name}
        {float(ownership.percentage):.2f}

        Asunto-osakeyhtiö
        {apartment.housing_company.display_name}, Helsinki
        Huoneiston osoite
        {apartment.address}, {apartment.postal_code.value} HELSINKI
        Huoneiston valmistumisajankohta
        {apartment.completion_date.strftime("%d.%m.%Y")}
        Huoneiston ensimmäinen kaupantekoajankohta
        {apartment.first_sale().purchase_date.strftime("%d.%m.%Y")}
        Alkuperäinen velaton hankintahinta, euroa
        95 000,00
        Rakennuttajalta tilatut lisä- ja muutostyöt
        5 000,00
        Rakennusaikainen korko, euroa
        1 000,00
        Hitas-huoneiston hinta rakennuskustannusindeksillä
        laskettuna, euroa
        148 863,90
        This is additional information
        Hitas-huoneistonne velaton enimmäishinta on 150 000 euroa. Velaton enimmäishinta on laskettu
        voimassaolevan rajahinnan perusteella (50.00 m² * 3000.00 euroa).
        {body.texts[0]}
        {body.texts[1]}
        {body.texts[2]}
        {api_user.first_name} {api_user.last_name}
        {api_user.title}
        """
    )


class MissingIndexParameters(NamedTuple):
    missing_index: Literal[
        "completion_date_construction_price_index_missing",
        "completion_date_market_price_index_missing",
        "current_date_construction_price_index_missing",
        "current_date_market_price_index_missing",
        "surface_area_price_ceiling_missing",
    ]
    error: str
    message: str


@pytest.mark.django_db
@pytest.mark.parametrize(
    **parametrize_helper(
        {
            "completion_date_construction_price_index_missing": MissingIndexParameters(
                missing_index="completion_date_construction_price_index_missing",
                error="cpi2005eq100.2022-01",
                message="One or more indices required for max price calculation is missing.",
            ),
            "completion_date_market_price_index_missing": MissingIndexParameters(
                missing_index="completion_date_market_price_index_missing",
                error="mpi2005eq100.2022-01",
                message="One or more indices required for max price calculation is missing.",
            ),
            "current_date_construction_price_index_missing": MissingIndexParameters(
                missing_index="current_date_construction_price_index_missing",
                error="cpi2005eq100.2022-01",
                message="One or more indices required for max price calculation is missing.",
            ),
            "current_date_market_price_index_missing": MissingIndexParameters(
                missing_index="current_date_market_price_index_missing",
                error="mpi2005eq100.2022-01",
                message="One or more indices required for max price calculation is missing.",
            ),
            "surface_area_price_ceiling_missing": MissingIndexParameters(
                missing_index="surface_area_price_ceiling_missing",
                error="sapc.2022-01",
                message="One or more indices required for max price calculation is missing.",
            ),
        }
    )
)
def test__api__unconfirmed_max_price_pdf__indices_missing(
    api_client: HitasAPIClient,
    freezer,
    missing_index: str,
    error: str,
    message: str,
):
    freezer.move_to("2022-01-01")

    apartment: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2021, 1, 1),
        additional_work_during_construction=5000,
        interest_during_construction_mpi=1000,
        interest_during_construction_cpi=2000,
        surface_area=50,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        sales__purchase_price=80000,
        sales__apartment_share_of_housing_company_loans=15000,
    )

    PDFBodyFactory.create(
        name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION,
        texts=["||foo||", "||bar||", "||baz||"],
    )

    this_month = timezone.now().date().replace(day=1)
    completion_month = apartment.completion_date.replace(day=1)

    # Completion month indices
    if missing_index != "completion_date_construction_price_index_missing":
        ConstructionPriceIndex2005Equal100Factory.create(month=completion_month, value=100)
    if missing_index != "completion_date_market_price_index_missing":
        MarketPriceIndex2005Equal100Factory.create(month=completion_month, value=200)

    # Current month indices
    if missing_index != "current_date_construction_price_index_missing":
        ConstructionPriceIndex2005Equal100Factory.create(month=this_month, value=150)
    if missing_index != "current_date_market_price_index_missing":
        MarketPriceIndex2005Equal100Factory.create(month=this_month, value=250)
    if missing_index != "surface_area_price_ceiling_missing":
        SurfaceAreaPriceCeilingFactory.create(month=this_month, value=3000)

    url = reverse(
        "hitas:apartment-download-latest-unconfirmed-prices",
        kwargs={"housing_company_uuid": apartment.housing_company.uuid.hex, "uuid": apartment.uuid.hex},
    )

    data = {
        "request_date": "2022-01-01",
        "additional_info": "This is additional information",
    }

    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": error,
        "message": message,
        "reason": "Conflict",
        "status": 409,
    }


@pytest.mark.django_db
def test__api__unconfirmed_max_price_pdf__past_date(api_client: HitasAPIClient, freezer):
    freezer.move_to("2022-01-01")
    api_user: User = api_client.handler._force_user

    apartment: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2021, 1, 1),
        additional_work_during_construction=5000,
        interest_during_construction_mpi=1000,
        interest_during_construction_cpi=2000,
        surface_area=50,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        sales__purchase_price=80000,
        sales__apartment_share_of_housing_company_loans=15000,
    )

    ownership: Ownership = apartment.latest_sale(include_first_sale=True).ownerships.first()

    body = PDFBodyFactory.create(
        name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION,
        texts=["||foo||", "||bar||", "||baz||"],
    )

    this_month = timezone.now().date().replace(day=1)
    past_month = datetime.date(2021, 5, 1)
    completion_month = apartment.completion_date.replace(day=1)

    # Completion month indices
    ConstructionPriceIndex2005Equal100Factory.create(month=completion_month, value=100)
    MarketPriceIndex2005Equal100Factory.create(month=completion_month, value=200)
    # Past month indices
    ConstructionPriceIndex2005Equal100Factory.create(month=past_month, value=150)
    MarketPriceIndex2005Equal100Factory.create(month=past_month, value=250)
    SurfaceAreaPriceCeilingFactory.create(month=past_month, value=3000)
    # Current month indices (should not be used in calculation)
    ConstructionPriceIndex2005Equal100Factory.create(month=this_month, value=200)
    MarketPriceIndex2005Equal100Factory.create(month=this_month, value=300)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=4000)

    url = reverse(
        "hitas:apartment-download-latest-unconfirmed-prices",
        kwargs={"housing_company_uuid": apartment.housing_company.uuid.hex, "uuid": apartment.uuid.hex},
    )

    data = {
        "request_date": "2022-01-01",
        "calculation_date": past_month.isoformat(),
        "additional_info": "This is additional information",
    }

    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert response["content-type"] == "application/pdf"

    letter = PdfReader(BytesIO(response.content))
    assert len(letter.pages) == 1

    page_1 = letter.pages[0].extract_text()
    page_1 = cleandoc("\n".join(item.strip() for item in page_1.split("\n")))

    assert page_1 == cleandoc(
        f"""
        01.01.2022
        Postiosoite
        Käyntiosoite
        Puh. (09) 310 13033
        Asuntopalvelut
        Työpajankatu 8
        Email hitas@hel.fi
        PL 58231
        00580 Helsinki
        Url http://www.hel.fi/hitas
        00099 HELSINGIN KAUPUNKI
        {apartment.address}
        {apartment.postal_code.value} HELSINKI
        HITAS-HUONEISTON ENIMMÄISHINTA
        \x7f ilman yhtiökohtaisia parannuksia ja mahdollista yhtiölainaosuutta
        Omistaja ja omistusosuus (%)
        {ownership.owner.name}
        {float(ownership.percentage):.2f}

        Asunto-osakeyhtiö
        {apartment.housing_company.display_name}, Helsinki
        Huoneiston osoite
        {apartment.address}, {apartment.postal_code.value} HELSINKI
        Huoneiston valmistumisajankohta
        {apartment.completion_date.strftime("%d.%m.%Y")}
        Huoneiston ensimmäinen kaupantekoajankohta
        {apartment.first_sale().purchase_date.strftime("%d.%m.%Y")}
        Alkuperäinen velaton hankintahinta, euroa
        95 000,00
        Rakennuttajalta tilatut lisä- ja muutostyöt
        5 000,00
        Hitas-huoneiston hinta rakennuskustannusindeksillä
        laskettuna, euroa
        150 000,00
        This is additional information
        Hitas-huoneistonne velaton enimmäishinta on 150 000 euroa rakennuskustannusindeksillä laskettuna.
        {body.texts[0]}
        {body.texts[1]}
        {body.texts[2]}
        {api_user.first_name} {api_user.last_name}
        {api_user.title}
        """
    )


@pytest.mark.django_db
def test__api__unconfirmed_max_price_pdf__request_date_in_the_future(api_client: HitasAPIClient, freezer):
    freezer.move_to("2022-01-01")

    apartment: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2021, 1, 1),
        additional_work_during_construction=5000,
        interest_during_construction_mpi=1000,
        interest_during_construction_cpi=2000,
        surface_area=50,
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        sales__purchase_price=80000,
        sales__apartment_share_of_housing_company_loans=15000,
    )

    past_month = datetime.date(2021, 5, 1)
    future_month = datetime.date(2022, 5, 1)

    url = reverse(
        "hitas:apartment-download-latest-unconfirmed-prices",
        kwargs={"housing_company_uuid": apartment.housing_company.uuid.hex, "uuid": apartment.uuid.hex},
    )

    data = {
        "request_date": future_month.isoformat(),
        "calculation_date": past_month.isoformat(),
        "additional_info": "This is additional information",
    }

    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "request_date",
                "message": "Date cannot be in the future.",
            },
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__unconfirmed_max_price_pdf__calculation_date_in_the_future(api_client: HitasAPIClient, freezer):
    freezer.move_to("2022-01-01")

    apartment: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2021, 1, 1),
        additional_work_during_construction=5000,
        interest_during_construction_mpi=1000,
        interest_during_construction_cpi=2000,
        surface_area=50,
        building__real_estate__housing_company__hitas_type=HitasType.HITAS_I,
        sales__purchase_price=80000,
        sales__apartment_share_of_housing_company_loans=15000,
    )

    future_month = datetime.date(2022, 5, 1)

    url = reverse(
        "hitas:apartment-download-latest-unconfirmed-prices",
        kwargs={"housing_company_uuid": apartment.housing_company.uuid.hex, "uuid": apartment.uuid.hex},
    )

    data = {
        "request_date": "2022-01-01",
        "calculation_date": future_month.isoformat(),
        "additional_info": "This is additional information",
    }

    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {
                "field": "calculation_date",
                "message": "Date cannot be in the future.",
            },
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__unconfirmed_max_price_pdf__missing_template(api_client: HitasAPIClient, freezer):
    freezer.move_to("2022-01-01")

    apartment: Apartment = ApartmentFactory.create(
        completion_date=datetime.date(2021, 1, 1),
        additional_work_during_construction=5000,
        interest_during_construction_mpi=1000,
        interest_during_construction_cpi=2000,
        surface_area=50,
        building__real_estate__housing_company__hitas_type=HitasType.NEW_HITAS_I,
        sales__purchase_price=80000,
        sales__apartment_share_of_housing_company_loans=15000,
    )

    this_month = timezone.now().date().replace(day=1)
    completion_month = apartment.completion_date.replace(day=1)

    # Completion month indices
    ConstructionPriceIndex2005Equal100Factory.create(month=completion_month, value=100)
    MarketPriceIndex2005Equal100Factory.create(month=completion_month, value=200)
    # Current month indices
    ConstructionPriceIndex2005Equal100Factory.create(month=this_month, value=150)
    MarketPriceIndex2005Equal100Factory.create(month=this_month, value=250)
    SurfaceAreaPriceCeilingFactory.create(month=this_month, value=3000)

    url = reverse(
        "hitas:apartment-download-latest-unconfirmed-prices",
        kwargs={"housing_company_uuid": apartment.housing_company.uuid.hex, "uuid": apartment.uuid.hex},
    )

    data = {
        "request_date": "2022-01-01",
        "additional_info": "This is additional information",
    }

    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_409_CONFLICT, response.json()
    assert response.json() == {
        "error": "missing",
        "message": "Missing body template",
        "reason": "Conflict",
        "status": 409,
    }
