import datetime

import pytest

from hitas.calculations.max_prices.rules import surface_area_price_ceiling_validity


@pytest.mark.parametrize(
    "date, expected",
    [
        # January
        (datetime.date(2022, 1, 1), datetime.date(2022, 2, 28)),
        (datetime.date(2022, 1, 15), datetime.date(2022, 2, 28)),
        (datetime.date(2022, 1, 31), datetime.date(2022, 2, 28)),
        # February
        (datetime.date(2022, 2, 1), datetime.date(2022, 5, 31)),
        (datetime.date(2022, 2, 15), datetime.date(2022, 5, 31)),
        (datetime.date(2022, 2, 28), datetime.date(2022, 5, 31)),
        # March
        (datetime.date(2022, 3, 1), datetime.date(2022, 5, 31)),
        (datetime.date(2022, 3, 15), datetime.date(2022, 5, 31)),
        (datetime.date(2022, 3, 31), datetime.date(2022, 5, 31)),
        # April
        (datetime.date(2022, 4, 1), datetime.date(2022, 5, 31)),
        (datetime.date(2022, 4, 15), datetime.date(2022, 5, 31)),
        (datetime.date(2022, 4, 30), datetime.date(2022, 5, 31)),
        # May
        (datetime.date(2022, 5, 1), datetime.date(2022, 8, 31)),
        (datetime.date(2022, 5, 15), datetime.date(2022, 8, 31)),
        (datetime.date(2022, 5, 31), datetime.date(2022, 8, 31)),
        # June
        (datetime.date(2022, 6, 1), datetime.date(2022, 8, 31)),
        (datetime.date(2022, 6, 15), datetime.date(2022, 8, 31)),
        (datetime.date(2022, 6, 30), datetime.date(2022, 8, 31)),
        # July
        (datetime.date(2022, 7, 1), datetime.date(2022, 8, 31)),
        (datetime.date(2022, 7, 15), datetime.date(2022, 8, 31)),
        (datetime.date(2022, 7, 31), datetime.date(2022, 8, 31)),
        # August
        (datetime.date(2022, 8, 1), datetime.date(2022, 11, 30)),
        (datetime.date(2022, 8, 15), datetime.date(2022, 11, 30)),
        (datetime.date(2022, 8, 31), datetime.date(2022, 11, 30)),
        # September
        (datetime.date(2022, 9, 1), datetime.date(2022, 11, 30)),
        (datetime.date(2022, 9, 15), datetime.date(2022, 11, 30)),
        (datetime.date(2022, 9, 30), datetime.date(2022, 11, 30)),
        # October
        (datetime.date(2022, 10, 1), datetime.date(2022, 11, 30)),
        (datetime.date(2022, 10, 15), datetime.date(2022, 11, 30)),
        (datetime.date(2022, 10, 31), datetime.date(2022, 11, 30)),
        # November
        (datetime.date(2022, 11, 1), datetime.date(2023, 2, 28)),
        (datetime.date(2022, 11, 15), datetime.date(2023, 2, 28)),
        (datetime.date(2022, 11, 30), datetime.date(2023, 2, 28)),
        # December
        (datetime.date(2022, 12, 1), datetime.date(2023, 2, 28)),
        (datetime.date(2022, 12, 15), datetime.date(2023, 2, 28)),
        (datetime.date(2022, 12, 31), datetime.date(2023, 2, 28)),
        # Leap year
        (datetime.date(2023, 11, 1), datetime.date(2024, 2, 29)),
        (datetime.date(2023, 12, 31), datetime.date(2024, 2, 29)),
        (datetime.date(2024, 1, 1), datetime.date(2024, 2, 29)),
        (datetime.date(2024, 1, 31), datetime.date(2024, 2, 29)),
    ],
)
def test__surface_area_price_ceiling_validity(date: datetime.date, expected: datetime.date):
    assert surface_area_price_ceiling_validity(date) == expected
