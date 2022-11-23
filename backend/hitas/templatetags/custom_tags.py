from datetime import date, datetime
from decimal import Decimal
from typing import Union

import django_jinja.library
from django.contrib.humanize.templatetags.humanize import intcomma as humanize_intcomma
from num2words import num2words


@django_jinja.library.filter
def format_date(value: Union[str, datetime]) -> str:
    if type(value) == str:
        value = datetime.strptime(value, "%Y-%m-%d")

    if value:
        return datetime.strftime(value, "%d.%m.%Y")
    return "-"


@django_jinja.library.filter
def intcomma(value) -> str:
    if not value:
        return "0"
    return humanize_intcomma(Decimal(str(value)).normalize())


@django_jinja.library.filter
def wordify(value: int) -> str:
    return num2words(value, lang="fi")


@django_jinja.library.filter
def is_date_pre_2011(value: Union[str, datetime.date]) -> bool:
    if type(value) == str:
        value = datetime.strptime(value, "%Y-%m-%d")
    return value < date(2011, 1, 1)
