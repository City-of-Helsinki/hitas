import datetime
from decimal import Decimal
from inspect import cleandoc
from io import BytesIO

import pytest
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from pypdf import PdfReader
from rest_framework import status
from rest_framework.reverse import reverse

from hitas.models import Apartment
from hitas.models.pdf_body import PDFBodyName
from hitas.models.thirty_year_regulation import (
    RegulationResult,
    ThirtyYearRegulationResults,
    ThirtyYearRegulationResultsRow,
)
from hitas.tests.apis.helpers import HitasAPIClient
from hitas.tests.apis.thirty_year_regulation.utils import create_thirty_year_old_housing_company, get_relevant_dates
from hitas.tests.factories import PDFBodyFactory
from users.models import User

# Regulation letters


@pytest.mark.django_db
def test__api__regulation_letter__continuation_letter(api_client: HitasAPIClient, freezer):
    api_user: User = api_client.handler._force_user
    this_month, _, regulation_month = get_relevant_dates(freezer)

    old_housing_company = create_thirty_year_old_housing_company()
    apartment = Apartment.objects.first()

    result = ThirtyYearRegulationResults.objects.create(
        regulation_month=datetime.datetime(1993, 2, 1),
        calculation_month=datetime.date(2023, 2, 1),
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
        housing_company=old_housing_company,
        completion_date=datetime.date(1993, 2, 1),
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

    body = PDFBodyFactory.create(name=PDFBodyName.STAYS_REGULATED, texts=["||foo||", "||bar||", "||baz||"])

    url = reverse("hitas:thirty-year-regulation-letter") + f"?housing_company_id={old_housing_company.uuid.hex}"

    response: HttpResponse = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    # Fetch has been saved
    row.refresh_from_db()
    assert row.letter_fetched is True

    letter = PdfReader(BytesIO(response.content))
    assert len(letter.pages) == 2

    page_1 = letter.pages[0].extract_text()
    page_1 = cleandoc("\n".join(item.strip() for item in page_1.split("\n")))

    address = (
        f"{old_housing_company.street_address}, " f"{row.postal_code} {old_housing_company.postal_code.city.upper()}"
    )

    assert page_1 == cleandoc(
        f"""
        01.02.2023
        Postiosoite
        Käyntiosoite
        Puh. (09) 310 13033
        Hitas
        Työpajankatu 8
        Email hitas@hel.fi
        PL 58237
        00580 Helsinki
        Url http://www.hel.fi/hitas
        00099 HELSINGIN KAUPUNKI
        {old_housing_company.display_name}
        HITAS-YHTIÖN HINTOJEN VERTAILU JA HINTASÄÄNTELYN VAIKUTUS
        Asunto-osakeyhtiö
        {old_housing_company.display_name}
        Yhtiön osoite
        {address}
        Osakenumerot
        {apartment.share_number_start} - {apartment.share_number_end}
        Kiinteistötunnukset
        {apartment.building.real_estate.property_identifier}
        Yhtiön ikä
        Yhtiönne valmistumisesta on kulunut 30 vuotta 01.02.2023
        Yhtiön keskineliöhinta
        Yhtiönne laskettu keskimääräinen neliöhinta on kaksitoistatuhatta (12 000) euroa
        markkinahintaindeksillä laskettuna.
        Rajahinta
        Kaikkien Hitas-yhtiöiden keskimääräinen neliöhinta on viisituhatta (5 000) euroa. Jos yhtiön
        keskineliöhinta on alempi kuin rajahinta, niin vertailussa yhtiön neliöhintana käytetään
        rajahintaa.
        Postinumeroalueen
        keskineliöhinta
        Tilastokeskuksen viimeisimmän 12 kuukauden hintatilaston (täydennettynä Hitas-asuntojen
        hintatiedoilla) mukaan postinumeroalueen 00001 asuntojen keskimääräinen neliöhinta on
        neljäkymmentäyhdeksäntuhatta (49 000) euroa.
        Neliöhintojen vertailu
        {old_housing_company.display_name} jää enimmäishintojen vertailun perusteella hintasääntelyn
        vaikutuksen piiriin, koska yhtiön keskineliöhinta alittaa postinumeroalueen kaikkien asuntojen
        keskineliöhinnan.
        Hintasääntelystä
        vapautuminen
        {body.texts[0]}
        Tontin maanvuokra
        {body.texts[1]}
        Hintasääntelyn
        jatkuminen
        {body.texts[2]}
        Hintasääntelyilmoitus on tulostettu Hitas-rekisteristä.
        Lisätiedot: {api_user.first_name} {api_user.last_name}, {api_user.title}, puhelin {api_user.phone}
        LIITE
        Laskelma yhtiön keskineliöhinnoista
        TIEDOKSI
        Kaupunkiympäristön tontit-yksikölle
        """
    )

    page_2 = letter.pages[1].extract_text()
    page_2 = cleandoc("\n".join(item.strip() for item in page_2.split("\n")))

    assert page_2 == cleandoc(
        f"""
        Liite 1
        01.02.2023
        Postiosoite
        Käyntiosoite
        Puh. (09) 310 13033
        Hitas
        Työpajankatu 8
        Email hitas@hel.fi
        PL 58237
        00580 Helsinki
        Url http://www.hel.fi/hitas
        00099 HELSINGIN KAUPUNKI
        LASKELMA YHTIÖN KESKINELIÖHINNASTA
        RAKENNUSKUSTANNUS- JA MARKKINAHINTAINDEKSILLÄ
        Asunto-osakeyhtiö:
        {old_housing_company.display_name}
        Yhtiön osoite:
        {address}
        Yhtiön osakenumerot:
        {apartment.share_number_start} - {apartment.share_number_end}
        Osakkeiden lkm:
        {apartment.share_number_end - apartment.share_number_start + 1}
        Asuntojen lkm:
        1

        Hankinta-arvo:
        60 000
        Pinta-ala m²:
        10
        Viimeisen vaiheen valmistumispäivä:
        01.02.1993
         rakennuskustannushintaindeksi
        0
         markkinahintaindeksi
        100,00
        Laskentapäivä:
        01.02.2023
         rakennuskustannushintaindeksi
        0
         markkinahintaindeksi
        200,00

        Keskimääräinen neliöhinta
        rakennuskustannushintaindeksillä euroa/m²
        0
        laskentakaava:
        (0 / 0) * (60 000 / 10)
        Keskimääräinen neliöhinta
        markkinahintaindeksillä euroa/m²
        12 000
        laskentakaava:
        (200,00 / 100,00) * (60 000 / 10)

        NELIÖHINTOJEN VERTAILU
        Yhtiön keskineliöhinta euroa/m²
        12 000
        Rajahinta euroa/m²
        5 000
        Postinumeroalueen keskihinta euroa/m²
        49 000
        Hintaero postinumeroalueen neliöhintaan
        (= ero yhtiön keskineliöhintaan tai rajahintaan)
        -37 000
        """
    )


@pytest.mark.django_db
def test__api__regulation_letter__release_letter(api_client: HitasAPIClient, freezer):
    api_user: User = api_client.handler._force_user
    this_month, _, regulation_month = get_relevant_dates(freezer)

    old_housing_company = create_thirty_year_old_housing_company()
    apartment = Apartment.objects.first()

    result = ThirtyYearRegulationResults.objects.create(
        regulation_month=datetime.datetime(1993, 2, 1),
        calculation_month=datetime.date(2023, 2, 1),
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
        housing_company=old_housing_company,
        completion_date=datetime.date(1993, 2, 1),
        surface_area=Decimal("10.00"),
        postal_code="00001",
        realized_acquisition_price=Decimal("60000.00"),
        unadjusted_average_price_per_square_meter=Decimal("6000.00"),
        adjusted_average_price_per_square_meter=Decimal("12000.00"),
        completion_month_index=Decimal("100.00"),
        calculation_month_index=Decimal("200.00"),
        regulation_result=RegulationResult.RELEASED_FROM_REGULATION,
    )

    body = PDFBodyFactory.create(name=PDFBodyName.RELEASED_FROM_REGULATION, texts=["||foo||"])

    url = reverse("hitas:thirty-year-regulation-letter") + f"?housing_company_id={old_housing_company.uuid.hex}"

    response: HttpResponse = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    # Fetch has been saved
    row.refresh_from_db()
    assert row.letter_fetched is True

    letter = PdfReader(BytesIO(response.content))
    assert len(letter.pages) == 2

    page_1 = letter.pages[0].extract_text()
    page_1 = cleandoc("\n".join(item.strip() for item in page_1.split("\n")))

    address = (
        f"{old_housing_company.street_address}, " f"{row.postal_code} {old_housing_company.postal_code.city.upper()}"
    )

    assert page_1 == cleandoc(
        f"""
        01.02.2023
        Postiosoite
        Käyntiosoite
        Puh. (09) 310 13033
        Hitas
        Työpajankatu 8
        Email hitas@hel.fi
        PL 58237
        00580 Helsinki
        Url http://www.hel.fi/hitas
        00099 HELSINGIN KAUPUNKI
        {old_housing_company.display_name}
        HITAS-YHTIÖN HINTOJEN VERTAILU JA HINTASÄÄNTELYSTÄ VAPAUTUMINEN
        Asunto-osakeyhtiö
        {old_housing_company.display_name}
        Yhtiön osoite
        {address}
        Osakenumerot
        {apartment.share_number_start} - {apartment.share_number_end}
        Kiinteistötunnukset
        {apartment.building.real_estate.property_identifier}
        Yhtiön ikä
        Yhtiönne valmistumisesta on kulunut 30 vuotta 01.02.2023
        Yhtiön keskineliöhinta
        Yhtiönne laskettu keskimääräinen neliöhinta on kaksitoistatuhatta (12 000) euroa
        markkinahintaindeksillä laskettuna.
        Rajahinta
        Kaikkien Hitas-yhtiöiden keskimääräinen neliöhinta on viisituhatta (5 000) euroa. Jos yhtiön
        keskineliöhinta on alempi kuin rajahinta, niin vertailussa yhtiön neliöhintana käytetään
        rajahintaa.
        Postinumeroalueen
        keskineliöhinta
        Tilastokeskuksen viimeisimmän 12 kuukauden hintatilaston (täydennettynä Hitas-asuntojen
        hintatiedoilla) mukaan postinumeroalueen 00001 asuntojen keskimääräinen neliöhinta on
        neljätuhatta yhdeksänsataa (4 900) euroa.
        Neliöhintojen vertailu
        {old_housing_company.display_name} vapautuu enimmäishintojen vertailun perusteella
        hintasääntelystä, koska yhtiön keskineliöhinta ylittää postinumeroalueen kaikkien asuntojen
        keskineliöhinnan.
        Hintasääntelystä
        vapautuminen
        {body.texts[0]}
        Hintasääntelyilmoitus on tulostettu Hitas-rekisteristä.
        Lisätiedot: {api_user.first_name} {api_user.last_name}, {api_user.title}, puhelin {api_user.phone}
        LIITE
        Laskelma yhtiön keskineliöhinnoista
        TIEDOKSI
        Kaupunkiympäristön tontit-yksikölle
        """
    )

    page_2 = letter.pages[1].extract_text()
    page_2 = cleandoc("\n".join(item.strip() for item in page_2.split("\n")))

    assert page_2 == cleandoc(
        f"""
        Liite 1
        01.02.2023
        Postiosoite
        Käyntiosoite
        Puh. (09) 310 13033
        Hitas
        Työpajankatu 8
        Email hitas@hel.fi
        PL 58237
        00580 Helsinki
        Url http://www.hel.fi/hitas
        00099 HELSINGIN KAUPUNKI
        LASKELMA YHTIÖN KESKINELIÖHINNASTA
        RAKENNUSKUSTANNUS- JA MARKKINAHINTAINDEKSILLÄ
        Asunto-osakeyhtiö:
        {old_housing_company.display_name}
        Yhtiön osoite:
        {address}
        Yhtiön osakenumerot:
        {apartment.share_number_start} - {apartment.share_number_end}
        Osakkeiden lkm:
        {apartment.share_number_end - apartment.share_number_start + 1}
        Asuntojen lkm:
        1

        Hankinta-arvo:
        60 000
        Pinta-ala m²:
        10
        Viimeisen vaiheen valmistumispäivä:
        01.02.1993
         rakennuskustannushintaindeksi
        0
         markkinahintaindeksi
        100,00
        Laskentapäivä:
        01.02.2023
         rakennuskustannushintaindeksi
        0
         markkinahintaindeksi
        200,00

        Keskimääräinen neliöhinta
        rakennuskustannushintaindeksillä euroa/m²
        0
        laskentakaava:
        (0 / 0) * (60 000 / 10)
        Keskimääräinen neliöhinta
        markkinahintaindeksillä euroa/m²
        12 000
        laskentakaava:
        (200,00 / 100,00) * (60 000 / 10)

        NELIÖHINTOJEN VERTAILU
        Yhtiön keskineliöhinta euroa/m²
        12 000
        Rajahinta euroa/m²
        5 000
        Postinumeroalueen keskihinta euroa/m²
        4 900
        Hintaero postinumeroalueen neliöhintaan
        (= ero yhtiön keskineliöhintaan tai rajahintaan)
        7 100
        """
    )


@pytest.mark.django_db
def test__api__regulation_letter__previous_letter(api_client: HitasAPIClient, freezer):
    api_user: User = api_client.handler._force_user
    day = datetime.datetime(2023, 3, 1)
    freezer.move_to(day)

    this_month = day.date()
    last_month = this_month - relativedelta(months=1)

    old_housing_company = create_thirty_year_old_housing_company()
    apartment = Apartment.objects.first()

    # Previous thirty-year regulation results
    result_1 = ThirtyYearRegulationResults.objects.create(
        regulation_month=datetime.datetime(1993, 2, 1),
        calculation_month=datetime.date(2023, 2, 1),
        surface_area_price_ceiling=Decimal("5000.00"),
        sales_data={
            "external": {},
            "internal": {"00001": {"2022Q4": {"price": 49000.0, "sale_count": 1}}},
            "price_by_area": {"00001": 49000.0},
        },
        replacement_postal_codes=[],
    )
    ThirtyYearRegulationResultsRow.objects.create(
        parent=result_1,
        housing_company=old_housing_company,
        completion_date=datetime.date(1993, 2, 1),
        surface_area=Decimal("10.00"),
        postal_code="00001",
        realized_acquisition_price=Decimal("60000.00"),
        unadjusted_average_price_per_square_meter=Decimal("6000.00"),
        adjusted_average_price_per_square_meter=Decimal("12000.00"),
        completion_month_index=Decimal("100.00"),
        calculation_month_index=Decimal("200.00"),
        regulation_result=RegulationResult.STAYS_REGULATED,
    )

    # Latest thirty-year regulation results
    result = ThirtyYearRegulationResults.objects.create(
        regulation_month=datetime.datetime(1993, 2, 1),
        calculation_month=datetime.date(2023, 3, 1),
        surface_area_price_ceiling=Decimal("6000.00"),
        sales_data={
            "external": {},
            "internal": {"00001": {"2022Q4": {"price": 51000.0, "sale_count": 1}}},
            "price_by_area": {"00001": 51000.0},
        },
        replacement_postal_codes=[],
    )
    row = ThirtyYearRegulationResultsRow.objects.create(
        parent=result,
        housing_company=old_housing_company,
        completion_date=datetime.date(1993, 2, 1),
        surface_area=Decimal("10.00"),
        postal_code="00001",
        realized_acquisition_price=Decimal("60000.00"),
        unadjusted_average_price_per_square_meter=Decimal("6000.00"),
        adjusted_average_price_per_square_meter=Decimal("12000.00"),
        completion_month_index=Decimal("100.00"),
        calculation_month_index=Decimal("200.00"),
        regulation_result=RegulationResult.STAYS_REGULATED,
    )

    body = PDFBodyFactory.create(name=PDFBodyName.STAYS_REGULATED, texts=["||foo||", "||bar||", "||baz||"])

    url = (
        reverse("hitas:thirty-year-regulation-letter")
        + f"?housing_company_id={old_housing_company.uuid.hex}"
        + f"&calculation_date={last_month.isoformat()}"
    )

    response: HttpResponse = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    letter = PdfReader(BytesIO(response.content))
    assert len(letter.pages) == 2

    page_1 = letter.pages[0].extract_text()
    page_1 = cleandoc("\n".join(item.strip() for item in page_1.split("\n")))

    address = (
        f"{old_housing_company.street_address}, " f"{row.postal_code} {old_housing_company.postal_code.city.upper()}"
    )

    assert page_1 == cleandoc(
        f"""
        01.03.2023
        Postiosoite
        Käyntiosoite
        Puh. (09) 310 13033
        Hitas
        Työpajankatu 8
        Email hitas@hel.fi
        PL 58237
        00580 Helsinki
        Url http://www.hel.fi/hitas
        00099 HELSINGIN KAUPUNKI
        {old_housing_company.display_name}
        HITAS-YHTIÖN HINTOJEN VERTAILU JA HINTASÄÄNTELYN VAIKUTUS
        Asunto-osakeyhtiö
        {old_housing_company.display_name}
        Yhtiön osoite
        {address}
        Osakenumerot
        {apartment.share_number_start} - {apartment.share_number_end}
        Kiinteistötunnukset
        {apartment.building.real_estate.property_identifier}
        Yhtiön ikä
        Yhtiönne valmistumisesta on kulunut 30 vuotta 01.02.2023
        Yhtiön keskineliöhinta
        Yhtiönne laskettu keskimääräinen neliöhinta on kaksitoistatuhatta (12 000) euroa
        markkinahintaindeksillä laskettuna.
        Rajahinta
        Kaikkien Hitas-yhtiöiden keskimääräinen neliöhinta on viisituhatta (5 000) euroa. Jos yhtiön
        keskineliöhinta on alempi kuin rajahinta, niin vertailussa yhtiön neliöhintana käytetään
        rajahintaa.
        Postinumeroalueen
        keskineliöhinta
        Tilastokeskuksen viimeisimmän 12 kuukauden hintatilaston (täydennettynä Hitas-asuntojen
        hintatiedoilla) mukaan postinumeroalueen 00001 asuntojen keskimääräinen neliöhinta on
        neljäkymmentäyhdeksäntuhatta (49 000) euroa.
        Neliöhintojen vertailu
        {old_housing_company.display_name} jää enimmäishintojen vertailun perusteella hintasääntelyn
        vaikutuksen piiriin, koska yhtiön keskineliöhinta alittaa postinumeroalueen kaikkien asuntojen
        keskineliöhinnan.
        Hintasääntelystä
        vapautuminen
        {body.texts[0]}
        Tontin maanvuokra
        {body.texts[1]}
        Hintasääntelyn
        jatkuminen
        {body.texts[2]}
        Hintasääntelyilmoitus on tulostettu Hitas-rekisteristä.
        Lisätiedot: {api_user.first_name} {api_user.last_name}, {api_user.title}, puhelin {api_user.phone}
        LIITE
        Laskelma yhtiön keskineliöhinnoista
        TIEDOKSI
        Kaupunkiympäristön tontit-yksikölle
        """
    )

    page_2 = letter.pages[1].extract_text()
    page_2 = cleandoc("\n".join(item.strip() for item in page_2.split("\n")))

    assert page_2 == cleandoc(
        f"""
        Liite 1
        01.03.2023
        Postiosoite
        Käyntiosoite
        Puh. (09) 310 13033
        Hitas
        Työpajankatu 8
        Email hitas@hel.fi
        PL 58237
        00580 Helsinki
        Url http://www.hel.fi/hitas
        00099 HELSINGIN KAUPUNKI
        LASKELMA YHTIÖN KESKINELIÖHINNASTA
        RAKENNUSKUSTANNUS- JA MARKKINAHINTAINDEKSILLÄ
        Asunto-osakeyhtiö:
        {old_housing_company.display_name}
        Yhtiön osoite:
        {address}
        Yhtiön osakenumerot:
        {apartment.share_number_start} - {apartment.share_number_end}
        Osakkeiden lkm:
        {apartment.share_number_end - apartment.share_number_start + 1}
        Asuntojen lkm:
        1

        Hankinta-arvo:
        60 000
        Pinta-ala m²:
        10
        Viimeisen vaiheen valmistumispäivä:
        01.02.1993
         rakennuskustannushintaindeksi
        0
         markkinahintaindeksi
        100,00
        Laskentapäivä:
        01.02.2023
         rakennuskustannushintaindeksi
        0
         markkinahintaindeksi
        200,00

        Keskimääräinen neliöhinta
        rakennuskustannushintaindeksillä euroa/m²
        0
        laskentakaava:
        (0 / 0) * (60 000 / 10)
        Keskimääräinen neliöhinta
        markkinahintaindeksillä euroa/m²
        12 000
        laskentakaava:
        (200,00 / 100,00) * (60 000 / 10)

        NELIÖHINTOJEN VERTAILU
        Yhtiön keskineliöhinta euroa/m²
        12 000
        Rajahinta euroa/m²
        5 000
        Postinumeroalueen keskihinta euroa/m²
        49 000
        Hintaero postinumeroalueen neliöhintaan
        (= ero yhtiön keskineliöhintaan tai rajahintaan)
        -37 000
        """
    )


@pytest.mark.django_db
def test__api__regulation_letter__no_regulation_data(api_client: HitasAPIClient, freezer):
    this_month, _, regulation_month = get_relevant_dates(freezer)

    old_housing_company = create_thirty_year_old_housing_company()

    url = reverse("hitas:thirty-year-regulation-letter") + f"?housing_company_id={old_housing_company.uuid.hex}"

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "thirty_year_regulation_results_row_not_found",
        "message": "Thirty Year Regulation Results Row not found",
        "reason": "Not Found",
        "status": 404,
    }


@pytest.mark.django_db
def test__api__regulation_letter__invalid_id(api_client: HitasAPIClient, freezer):
    url = reverse("hitas:thirty-year-regulation-letter") + "?housing_company_id=foo"

    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {"field": "housing_company_id", "message": "Not a valid UUID."},
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


@pytest.mark.django_db
def test__api__regulation_letter__id_missing(api_client: HitasAPIClient, freezer):
    url = reverse("hitas:thirty-year-regulation-letter")

    response = api_client.get(url, openapi_validate_request=False)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {
        "error": "bad_request",
        "fields": [
            {"field": "housing_company_id", "message": "This field is mandatory and cannot be null."},
        ],
        "message": "Bad request",
        "reason": "Bad Request",
        "status": 400,
    }


# Regulation Excel report


@pytest.mark.django_db
def test__api__regulation_results__report(api_client: HitasAPIClient, freezer):
    this_month, _, regulation_month = get_relevant_dates(freezer)

    old_housing_company = create_thirty_year_old_housing_company()

    result = ThirtyYearRegulationResults.objects.create(
        regulation_month=datetime.datetime(1993, 2, 1),
        calculation_month=datetime.date(2023, 2, 1),
        surface_area_price_ceiling=Decimal("5000.00"),
        sales_data={
            "external": {},
            "internal": {"00001": {"2022Q4": {"price": 49000.0, "sale_count": 1}}},
            "price_by_area": {"00001": 49000.0},
        },
        replacement_postal_codes=[],
    )

    ThirtyYearRegulationResultsRow.objects.create(
        parent=result,
        housing_company=old_housing_company,
        completion_date=datetime.date(1993, 2, 1),
        surface_area=Decimal("10.00"),
        postal_code="00001",
        realized_acquisition_price=Decimal("60000.00"),
        unadjusted_average_price_per_square_meter=Decimal("6000.00"),
        adjusted_average_price_per_square_meter=Decimal("12000.00"),
        completion_month_index=Decimal("100.00"),
        calculation_month_index=Decimal("200.00"),
        regulation_result=RegulationResult.STAYS_REGULATED,
    )

    url = reverse("hitas:thirty-year-regulation-results") + f"?calculation_date={this_month.isoformat()}"

    response: HttpResponse = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    workbook: Workbook = load_workbook(BytesIO(response.content), data_only=False)
    worksheet: Worksheet = workbook.worksheets[0]

    assert list(worksheet.values) == [
        (
            "Yhtiö",
            "Hankinta-arvo",
            "Huoneistoja",
            "Indeksit",
            "Muutos",
            "Takistettu hinta",
            "Pinta-ala",
            "E-hinta/m²",
            "Postinumerohinta",
            "Tila",
            "Valmistumispäivä",
            "Yhtiön ikä",
        ),
        (
            old_housing_company.display_name,
            60000,
            1,
            "100.00/200.00",
            60000,
            120000,
            10,
            12000,
            49000,
            "Ei vapaudu",
            datetime.datetime(1993, 2, 1, 0, 0),
            "30 v 0 kk",
        ),
        (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ),
        (
            "Summa",
            "=SUM(B2:B2)",
            "=SUM(C2:C2)",
            None,
            "=SUM(E2:E2)",
            "=SUM(F2:F2)",
            "=SUM(G2:G2)",
            "=SUM(H2:H2)",
            "=SUM(I2:I2)",
            None,
            None,
            None,
        ),
        (
            "Keskiarvo",
            "=AVERAGE(B2:B2)",
            "=AVERAGE(C2:C2)",
            None,
            "=AVERAGE(E2:E2)",
            "=AVERAGE(F2:F2)",
            "=AVERAGE(G2:G2)",
            "=AVERAGE(H2:H2)",
            "=AVERAGE(I2:I2)",
            None,
            None,
            None,
        ),
    ]


@pytest.mark.django_db
def test__api__regulation_results__no_regulation_data(api_client: HitasAPIClient):
    url = reverse("hitas:thirty-year-regulation-results")

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
    assert response.json() == {
        "error": "thirty_year_regulation_results_not_found",
        "message": "Thirty Year Regulation Results not found",
        "reason": "Not Found",
        "status": 404,
    }
