import datetime

from hitas.exceptions import ModelConflict


class IndexMissingException(ModelConflict):
    def __init__(self, *, error_code: str, date: datetime.date):
        super().__init__(
            error_code=f"{error_code}.{date.strftime('%Y-%m')}",
            message="One or more indices required for max price calculation is missing.",
        )


class InvalidCalculationResultException(ModelConflict):
    def __init__(self, *, error_code: str, message: str = ""):
        super().__init__(
            error_code=error_code,
            message=" ".join(("Maximum price calculation could not be completed.", message)),
        )
