from datetime import datetime
from io import BytesIO
from typing import Any

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from rest_framework import exceptions
from xhtml2pdf import pisa


def render_to_pdf(template: str, context: dict[str, Any]) -> bytes:
    """Render given template to a pdf"""
    result = BytesIO()
    template = get_template(template).render(
        {
            **context,
            # Due to the limitations of the xhtml2pdf library a file system path
            # is required instead of a Django static files url.
            "logo_path": settings.BASE_DIR / "hitas/static/helsinki_kehystunnus_musta.png",
        },
    )
    pdf = pisa.pisaDocument(BytesIO(template.encode("UTF-8")), dest=result)
    if pdf.err:
        raise exceptions.APIException(pdf.err)
    return result.getvalue()


def get_pdf_response(filename: str, template: str, context: dict[str, Any]) -> HttpResponse:
    context.setdefault("title", filename)
    pdf = render_to_pdf(
        template,
        {
            **context,
            "date_today": datetime.strftime(timezone.now().date(), "%d.%m.%Y"),
        },
    )
    response = HttpResponse(pdf, content_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response
