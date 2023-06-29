import datetime
from typing import Literal, Optional
from uuid import UUID

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage
from django.db.models import Prefetch
from django.db.models.functions import TruncMonth
from django.utils import timezone

from hitas.exceptions import HitasModelNotFound, get_hitas_object_or_404
from hitas.models import (
    Apartment,
    ApartmentMaximumPriceCalculation,
    ConstructionPriceIndex,
    ConstructionPriceIndex2005Equal100,
    EmailTemplate,
    JobPerformance,
    MarketPriceIndex,
    MarketPriceIndex2005Equal100,
    Ownership,
    PDFBody,
    SurfaceAreaPriceCeiling,
)
from hitas.models.apartment import ApartmentWithAnnotations
from hitas.models.email_template import EmailTemplateType
from hitas.models.job_performance import JobPerformanceSource
from hitas.models.pdf_body import PDFBodyName
from hitas.models.thirty_year_regulation import RegulationResult, ThirtyYearRegulationResultsRowWithAnnotations
from hitas.services.apartment import (
    get_first_sale_loan_amount,
    get_first_sale_purchase_date,
    get_first_sale_purchase_price,
    get_latest_sale_purchase_date,
    get_latest_sale_purchase_price,
    prefetch_latest_sale,
)
from hitas.services.condition_of_sale import condition_of_sale_queryset
from hitas.services.indices import (
    subquery_apartment_current_surface_area_price,
    subquery_apartment_first_sale_acquisition_price_index_adjusted,
)
from hitas.services.thirty_year_regulation import get_thirty_year_regulation_results_for_housing_company
from hitas.utils import monthify
from hitas.views.apartment import ApartmentDetailSerializer
from hitas.views.utils.pdf import render_to_pdf
from users.models import User


def send_confirmed_max_price_calculation_email(
    calculation_id: UUID,
    request_date: datetime.date,
    template_name: str,
    recipients: list[str],
    user: User,
) -> None:
    confirmed_max_price_calculation = get_hitas_object_or_404(ApartmentMaximumPriceCalculation, uuid=calculation_id)
    filename, pdf = render_confirmed_max_price_calculation_pdf(confirmed_max_price_calculation, user)

    template = get_hitas_object_or_404(
        EmailTemplate,
        name=template_name,
        type=EmailTemplateType.CONFIRMED_MAX_PRICE_CALCULATION,
    )
    send_pdf_via_email(body=template.text, recipients=recipients, filename=filename, pdf=pdf)

    JobPerformance.objects.get_or_create(
        user=user,
        request_date=request_date,
        delivery_date=timezone.now().date(),
        source=JobPerformanceSource.CONFIRMED_MAX_PRICE,
        object_type=ContentType.objects.get_for_model(confirmed_max_price_calculation),
        object_id=confirmed_max_price_calculation.id,
    )


def render_confirmed_max_price_calculation_pdf(
    confirmed_max_price_calculation: ApartmentMaximumPriceCalculation,
    user: User,
) -> tuple[str, bytes]:
    pdf_body = get_hitas_object_or_404(PDFBody, name=PDFBodyName.CONFIRMED_MAX_PRICE_CALCULATION)
    filename = f"Enimmäishintalaskelma {confirmed_max_price_calculation.apartment.address}.pdf"
    context = {
        "maximum_price_calculation": confirmed_max_price_calculation,
        "user": user,
        "body_parts": pdf_body.texts,
        "title": filename,
        "date_today": datetime.date.strftime(timezone.now().today(), "%d.%m.%Y"),
    }
    pdf = render_to_pdf(template="confirmed_maximum_price.jinja", context=context)
    return filename, pdf


def get_apartment_for_unconfirmed_max_price_calculation(
    apartment_id: UUID,
    calculation_date: datetime.date,
) -> ApartmentWithAnnotations:
    completion_date: Optional[datetime.date] = (
        Apartment.objects.filter(uuid=apartment_id).values_list("completion_date", flat=True).first()
    )

    apartment: Optional[ApartmentWithAnnotations] = (
        Apartment.objects.filter(uuid=apartment_id)
        .prefetch_related(
            prefetch_latest_sale(include_first_sale=True),
            Prefetch(
                "sales__ownerships",
                Ownership.objects.select_related("owner"),
            ),
            Prefetch(
                "sales__ownerships__conditions_of_sale_new",
                condition_of_sale_queryset(),
            ),
            Prefetch(
                "sales__ownerships__conditions_of_sale_old",
                condition_of_sale_queryset(),
            ),
        )
        .select_related(
            "building",
            "apartment_type",
            "building__real_estate",
            "building__real_estate__housing_company",
            "building__real_estate__housing_company__postal_code",
        )
        .annotate(
            _first_purchase_date=get_first_sale_purchase_date("id"),
            _first_sale_purchase_price=get_first_sale_purchase_price("id"),
            _first_sale_share_of_housing_company_loans=get_first_sale_loan_amount("id"),
            _latest_sale_purchase_price=get_latest_sale_purchase_price("id"),
            _latest_purchase_date=get_latest_sale_purchase_date("id"),
            completion_month=TruncMonth("completion_date"),  # Used for calculating indexes
            cpi=subquery_apartment_first_sale_acquisition_price_index_adjusted(
                ConstructionPriceIndex,
                completion_date=completion_date,
                calculation_date=calculation_date,
            ),
            mpi=subquery_apartment_first_sale_acquisition_price_index_adjusted(
                MarketPriceIndex,
                completion_date=completion_date,
                calculation_date=calculation_date,
            ),
            cpi_2005_100=subquery_apartment_first_sale_acquisition_price_index_adjusted(
                ConstructionPriceIndex2005Equal100,
                completion_date=completion_date,
                calculation_date=calculation_date,
            ),
            mpi_2005_100=subquery_apartment_first_sale_acquisition_price_index_adjusted(
                MarketPriceIndex2005Equal100,
                completion_date=completion_date,
                calculation_date=calculation_date,
            ),
            sapc=subquery_apartment_current_surface_area_price(
                calculation_date=calculation_date,
            ),
        )
        .first()
    )
    if not apartment:
        raise HitasModelNotFound(Apartment)

    if apartment.housing_company.hitas_type.old_hitas_ruleset:
        if apartment.cpi is None:
            raise HitasModelNotFound(ConstructionPriceIndex)
        if apartment.mpi is None:
            raise HitasModelNotFound(MarketPriceIndex)
    else:
        if apartment.cpi_2005_100 is None:
            raise HitasModelNotFound(ConstructionPriceIndex2005Equal100)
        if apartment.mpi_2005_100 is None:
            raise HitasModelNotFound(MarketPriceIndex2005Equal100)

    return apartment


def send_unconfirmed_max_price_calculation_email(
    apartment_id: UUID,
    calculation_date: datetime.date,
    request_date: datetime.date,
    additional_info: str,
    template_name: str,
    recipients: list[str],
    user: User,
) -> None:
    calculation_month = monthify(calculation_date)
    apartment = get_apartment_for_unconfirmed_max_price_calculation(apartment_id, calculation_month)

    filename, pdf = render_unconfirmed_max_price_calculation_pdf(
        apartment=apartment,
        calculation_month=calculation_month,
        additional_info=additional_info,
        user=user,
    )

    template = get_hitas_object_or_404(
        EmailTemplate,
        name=template_name,
        type=EmailTemplateType.UNCONFIRMED_MAX_PRICE_CALCULATION,
    )
    send_pdf_via_email(body=template.text, recipients=recipients, filename=filename, pdf=pdf)

    JobPerformance.objects.get_or_create(
        user=user,
        request_date=request_date,
        delivery_date=timezone.now().date(),
        source=JobPerformanceSource.UNCONFIRMED_MAX_PRICE,
        object_type=ContentType.objects.get_for_model(apartment),
        object_id=apartment.id,
    )


def render_unconfirmed_max_price_calculation_pdf(
    apartment: ApartmentWithAnnotations,
    calculation_month: datetime.date,
    additional_info: str,
    user: User,
) -> tuple[str, bytes]:
    apartment_data = ApartmentDetailSerializer(apartment).data
    pdf_body = get_hitas_object_or_404(PDFBody, name=PDFBodyName.UNCONFIRMED_MAX_PRICE_CALCULATION)
    surface_area_price_ceiling = get_hitas_object_or_404(SurfaceAreaPriceCeiling, month=calculation_month)

    filename = f"Hinta-arvio {apartment.address}.pdf"
    context = {
        "apartment": apartment_data,
        "additional_info": additional_info,
        "surface_area_price_ceiling": surface_area_price_ceiling.value,
        "old_hitas_ruleset": apartment.old_hitas_ruleset,
        "user": user,
        "body_parts": pdf_body.texts,
        "date_today": datetime.date.strftime(timezone.now().today(), "%d.%m.%Y"),
    }

    pdf = render_to_pdf(template="unconfirmed_maximum_price.jinja", context=context)
    return filename, pdf


def send_regulation_letter_email(
    housing_company_id: UUID,
    calculation_date: datetime.date,
    template_name: str,
    recipients: list[str],
    user: User,
) -> None:
    results = get_thirty_year_regulation_results_for_housing_company(housing_company_id, calculation_date)
    filename, pdf = render_regulation_letter_pdf(results, user)

    template = get_hitas_object_or_404(
        EmailTemplate,
        name=template_name,
        type=(
            EmailTemplateType.STAYS_REGULATED
            if results.regulation_result == RegulationResult.STAYS_REGULATED
            else EmailTemplateType.RELEASED_FROM_REGULATION
        ),
    )

    send_pdf_via_email(body=template.text, recipients=recipients, filename=filename, pdf=pdf)


def render_regulation_letter_pdf(
    results: ThirtyYearRegulationResultsRowWithAnnotations,
    user: User,
) -> tuple[str, bytes]:
    pdf_body = get_hitas_object_or_404(
        PDFBody,
        name=(
            PDFBodyName.STAYS_REGULATED
            if results.regulation_result == RegulationResult.STAYS_REGULATED
            else PDFBodyName.RELEASED_FROM_REGULATION
        ),
    )
    choice = "jatkumisesta" if results.regulation_result == RegulationResult.STAYS_REGULATED else "pättymisestä"
    filename = f"Tiedote sääntelyn {choice} - {results.housing_company.display_name}.pdf"
    context = {
        "results": results,
        "user": user,
        "title": filename,
        "body_parts": pdf_body.texts,
        "date_today": datetime.date.strftime(timezone.now().today(), "%d.%m.%Y"),
    }
    pdf = render_to_pdf(template="regulation_letter.jinja", context=context)
    return filename, pdf


def send_pdf_via_email(body: str, recipients: list[str], filename: str, pdf: bytes) -> None:
    message = EmailMessage(
        subject=filename.removesuffix(".pdf"),
        body=body,
        to=recipients,
        bcc=[settings.DEFAULT_FROM_EMAIL],
        attachments=[(filename, pdf, "application/pdf")],
    )
    retries = 2
    while retries > 0:
        sent: Literal[0, 1] = message.send(fail_silently=True)
        if sent == 1:
            break
        retries -= 1
