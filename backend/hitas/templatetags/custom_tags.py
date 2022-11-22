from datetime import datetime
from typing import Union

import django_jinja.library
from django.contrib.humanize.templatetags.humanize import intcomma as humanize_intcomma
from num2words import num2words


@django_jinja.library.filter
def format_date(value: Union[str, datetime.date]) -> str:
    if type(value) == str:
        value = datetime.strptime(value, "%Y-%m-%d")

    if value:
        return datetime.strftime(value, "%d.%m.%Y")
    return "-"


@django_jinja.library.filter
def intcomma(value) -> str:
    return humanize_intcomma(value)


@django_jinja.library.filter
def wordify(value: int) -> str:
    return num2words(value, lang="fi")
