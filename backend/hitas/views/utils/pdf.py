from io import BytesIO
from typing import Any

from django.template.loader import get_template
from rest_framework import exceptions
from xhtml2pdf import pisa


def render_to_pdf(template: str, context: dict[str, Any]) -> bytes:
    """Render given template to a pdf"""
    result = BytesIO()
    template = get_template(template).render(context)
    pdf = pisa.pisaDocument(BytesIO(template.encode("UTF-8")), dest=result)
    if pdf.err:
        raise exceptions.APIException(pdf.err)
    return result.getvalue()
