import datetime
from decimal import Decimal

import pytest

from hitas.calculations.construction_time_interest import Payment, interest_days, total_construction_time_interest


@pytest.mark.parametrize(
    "payment_date, completion_date, expected",
    [
        (datetime.date(2022, 1, 1), datetime.date(2022, 1, 1), 0),
        (datetime.date(2022, 1, 1), datetime.date(2022, 1, 2), 0),
        (datetime.date(2022, 1, 1), datetime.date(2022, 1, 3), 2),
        (datetime.date(2022, 1, 1), datetime.date(2022, 2, 1), 30),  # One month is always 30
        (datetime.date(2022, 1, 1), datetime.date(2022, 3, 1), 60),  # Two months is always 60
        (datetime.date(2022, 1, 1), datetime.date(2023, 1, 1), 360),  # One year is 12 * 30 = 360
        (datetime.date(2022, 1, 1), datetime.date(2023, 5, 15), 494),  # One year + 4 months + 14 days = 360 + 120 + 14
        (datetime.date(2022, 3, 31), datetime.date(2022, 4, 1), 0),
        (datetime.date(2022, 3, 31), datetime.date(2022, 5, 1), 31),
        (datetime.date(2022, 3, 31), datetime.date(2022, 5, 31), 60),
        (datetime.date(2022, 3, 31), datetime.date(2022, 6, 1), 61),
    ],
)
def test_interest_days(payment_date: datetime.date, completion_date: datetime.date, expected: int):
    assert (
        interest_days(payment_date, completion_date) == expected
    ), f"days({payment_date}, {completion_date}) != {expected}"


def test_total_interest():
    assert (
        total_construction_time_interest(
            # loan_rate = 6 as given 10 is higher than that
            housing_company_construction_loan_rate=Decimal(10),
            apartment_completion_date=datetime.date(2022, 1, 1),
            apartment_transfer_price=Decimal(100000),
            apartment_loans_during_construction=Decimal(20000),
            payments=[
                # interest_days = 2021-12-01 -> 2022-01-01 = 30
                Payment(date=datetime.date(2021, 12, 1), percentage=Decimal(100)),
            ],
        )
        # 30 * 100 / 100 * (100_000 - 20_000) * 6 / 100 / 360
        == Decimal("400.00")
    )

    assert (
        total_construction_time_interest(
            # loan_rate = 6 as given 14 is higher than that
            housing_company_construction_loan_rate=Decimal(14),
            apartment_completion_date=datetime.date(1995, 2, 24),
            apartment_transfer_price=Decimal(48211.0),
            apartment_loans_during_construction=Decimal(0.0),
            payments=[
                # interest_days = 1994-03-15 -> 1995-02-24 = 11 months, 9 days = 339
                Payment(date=datetime.date(1994, 3, 15), percentage=Decimal(15)),
                # interest_days = 1994-04-29 -> 1995-02-24 = 10 months, -5 days = 295
                Payment(date=datetime.date(1994, 4, 29), percentage=Decimal(20)),
                # interest_days = 1994-06-15 -> 1995-02-24 = 8 months, 9 days = 249
                Payment(date=datetime.date(1994, 6, 15), percentage=Decimal(20)),
                # interest_days = 1994-08-15 -> 1995-02-24 = 6 months, 9 days = 189
                Payment(date=datetime.date(1994, 8, 15), percentage=Decimal(20)),
                # interest_days = 1994-10-14 -> 1995-02-24 = 4 months, 10 days = 130
                Payment(date=datetime.date(1994, 10, 14), percentage=Decimal(20)),
                # interest_days = 1995-02-10 -> 1995-02-24 = 14
                Payment(date=datetime.date(1995, 2, 10), percentage=Decimal(5)),
            ],
        )
        #   (339 * 0.15 * 48211 * 0.06 / 360 = 408.59 = 409)
        # + (295 * 0.20 * 48211 * 0.06 / 360 = 474.07 = 474)
        # + (249 * 0.20 * 48211 * 0.06 / 360 = 400.15 = 400)
        # + (189 * 0.20 * 48211 * 0.06 / 360 = 303.73 = 304)
        # + (130 * 0.20 * 48211 * 0.06 / 360 = 208.91 = 209)
        # + ( 14 * 0.05 * 48211 * 0.06 / 360 =   5.62 = 6)
        # = 1802
        == Decimal("1802")
    )
