import datetime
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional


@dataclass
class ImprovementData:
    # Name of the improvement
    name: str
    # Original value of the improvement
    value: Decimal
    # Completion date of the improvement
    completion_date: datetime.date
    # Completion date index for this improvement. Not needed for all the calculations.
    completion_date_index: Optional[Decimal] = None
    # Depreciation percentage for this improvement. Not needed for all the calculations.
    depreciation_percentage: Optional[Decimal] = None
    # When this improvement is apartment improvement constructed before 2011 then it's
    # possible to mark the improvement as "additional work before construction" which
    # is treated with its own rules.
    treat_as_additional_work: bool = False


class Excess(Enum):
    AFTER_2010_HOUSING_COMPANY = Decimal("30.0")
    BEFORE_2010_HOUSING_COMPANY = Decimal("150.0")
    BEFORE_2010_APARTMENT = Decimal("100.0")
