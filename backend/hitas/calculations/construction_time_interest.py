import datetime
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import List


@dataclass
class Payment:
    date: datetime.date
    percentage: Decimal


def total_construction_time_interest(
    loan_rate: Decimal,
    apartment_completion_date: datetime.date,
    apartment_transfer_price: Decimal,
    apartment_loans_during_construction: Decimal,
    payments: List[Payment],
) -> int:
    # Calculate the total interest for each payment
    return sum(
        map(
            lambda payment: int(
                # NOTE: each interest is rounded to the nearest integer as this is what the old system did
                payment_interest(
                    interest_days=interest_days(payment.date, apartment_completion_date),
                    instalment=payment.percentage,
                    transfer_price=apartment_transfer_price,
                    construction_time_loan=apartment_loans_during_construction,
                    loan_rate=loan_rate,
                ).quantize(Decimal("1"), ROUND_HALF_UP)
            ),
            payments,
        )
    )


def payment_interest(
    interest_days: int,
    instalment: Decimal,
    transfer_price: Decimal,
    construction_time_loan: Decimal,
    loan_rate: Decimal,
) -> Decimal:
    # Calculate the interest for a single payment
    return interest_days * (instalment / 100) * (transfer_price - construction_time_loan) * (loan_rate / 100) / 360


def interest_days(payment_date: datetime.date, completion_date: datetime.date) -> int:
    # interest days are not included when the payment date is >= (completion date - 1)
    if payment_date >= (completion_date - datetime.timedelta(days=1)):
        return 0

    # Calculate the number of days
    # NOTE: interest days are calculated as year = 12 months, month = 30 days
    retval = ((completion_date.year - payment_date.year) * 12 + (completion_date.month - payment_date.month)) * 30 + (
        completion_date.day - payment_date.day
    )

    # Add extra day when payment day is 31 and completion day is not, add an extra day (from the calculation rules)
    if payment_date.day == 31 and completion_date.day != 31:
        retval += 1

    return retval
