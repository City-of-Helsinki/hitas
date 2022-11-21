import datetime
import operator
from typing import Any, Optional

from rest_framework.authentication import TokenAuthentication


def safe_attrgetter(obj: Any, dotted_path: str, default: Optional[Any]) -> Any:
    """
    Examples:
        >>> safe_attrgetter(object, "__class__.__name__.__class__.__name__")
        'str'
        >>> safe_attrgetter(object, "foo.bar.baz") is None
        True
        >>> safe_attrgetter(object, "foo.bar.baz", default="")
        ''
    """
    try:
        return operator.attrgetter(dotted_path)(obj)
    except AttributeError:
        return default


class BearerAuthentication(TokenAuthentication):
    keyword = "Bearer"


def this_month() -> datetime.date:
    return monthify(datetime.date.today())


def monthify(date: datetime.date) -> datetime.date:
    return date.replace(day=1)
