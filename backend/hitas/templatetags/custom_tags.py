from datetime import datetime

import django_jinja.library
from django.contrib.humanize.templatetags.humanize import intcomma as humanize_intcomma


@django_jinja.library.filter
def format_date(value: str) -> str:
    if value:
        return datetime.strftime(datetime.strptime(value, "%Y-%m-%d"), "%d.%m.%Y")
    return "-"


@django_jinja.library.filter
def intcomma(value) -> str:
    return humanize_intcomma(value)
