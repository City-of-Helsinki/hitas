import datetime
import uuid
from datetime import date
from decimal import Decimal
from itertools import chain
from typing import Any, Collection, Optional

from dateutil.relativedelta import relativedelta
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import OuterRef, Prefetch, Subquery
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumField
from safedelete import SOFT_DELETE_CASCADE

from hitas.models._base import ExternalHitasModel, HitasImprovement, HitasModelDecimalField
from hitas.models.apartment_sale import ApartmentSale
from hitas.models.condition_of_sale import GracePeriod
from hitas.models.housing_company import HousingCompany
from hitas.models.ownership import Ownership, OwnershipLike
from hitas.models.postal_code import HitasPostalCode
from hitas.types import HitasEncoder


class ApartmentState(Enum):
    FREE = "free"
    RESERVED = "reserved"
    SOLD = "sold"

    class Labels:
        FREE = _("Free")
        RESERVED = _("Reserved")
        SOLD = _("Sold")


# Huoneisto / Asunto
class Apartment(ExternalHitasModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    building = models.ForeignKey("Building", on_delete=models.PROTECT, related_name="apartments")

    state = EnumField(ApartmentState, default=ApartmentState.FREE, null=True)
    apartment_type = models.ForeignKey("ApartmentType", on_delete=models.PROTECT, related_name="apartments", null=True)
    surface_area = HitasModelDecimalField(null=True, help_text=_("Measured in m^2"))
    # 'Huoneiden määrä'
    rooms = models.IntegerField(null=True, validators=[MinValueValidator(1)])

    # 'Pienin ja suurin osakenumero'
    share_number_start = models.IntegerField(null=True, validators=[MinValueValidator(1)])
    share_number_end = models.IntegerField(null=True, validators=[MinValueValidator(1)])

    completion_date = models.DateField(null=True)

    street_address = models.CharField(max_length=128)
    # 'Huoneistonumero'
    apartment_number = models.PositiveSmallIntegerField()
    # 'Kerros'
    floor = models.CharField(max_length=50, blank=True, null=True)
    # 'Porras'
    stair = models.CharField(max_length=16)

    # 'Kauppakirjahinta'
    purchase_price = HitasModelDecimalField(null=True, blank=True)
    # 'Rakennusaikaiset lisätyöt'
    additional_work_during_construction = HitasModelDecimalField(null=True)
    # 'Rakennusaikaiset lainat'
    loans_during_construction = HitasModelDecimalField(null=True)
    # 'Rakennusaikaiset korot 6%'
    interest_during_construction_6 = HitasModelDecimalField(null=True)
    # 'Rakennusaikaiset korot 14%'
    interest_during_construction_14 = HitasModelDecimalField(null=True)
    # 'Luovutushinta (RA)'
    debt_free_purchase_price_during_construction = HitasModelDecimalField(null=True)

    notes = models.TextField(blank=True, null=True)

    # 'Hankinta-arvo'
    @property
    def acquisition_price(self) -> Optional[Decimal]:
        if self.debt_free_purchase_price is None or self.primary_loan_amount is None:
            return None

        return self.debt_free_purchase_price + self.primary_loan_amount

    # 'Luovutushinta'
    @property
    def debt_free_purchase_price(self) -> Optional[Decimal]:
        first_sale = self.sales.order_by("purchase_date").first()
        return first_sale.purchase_price if first_sale is not None else None

    # 'Ensisijaislaina'
    @property
    def primary_loan_amount(self) -> Optional[Decimal]:
        first_sale = self.sales.order_by("purchase_date").first()
        return first_sale.primary_loan_amount if first_sale is not None else None

    # 'Ensimmäinen kauppakirjapvm'
    @property
    def first_purchase_date(self) -> Optional[date]:
        first_sale = self.sales.order_by("purchase_date").first()
        return first_sale.purchase_date if first_sale is not None else None

    # 'Viimeisin kauppakirjapvm'
    @property
    def latest_purchase_date(self) -> Optional[date]:
        last_sale = self.sales.order_by("purchase_date").last()
        return last_sale.purchase_date if last_sale is not None else None

    @property
    def housing_company(self) -> HousingCompany:
        return self.building.real_estate.housing_company

    @property
    def postal_code(self) -> HitasPostalCode:
        return self.building.postal_code

    @property
    def city(self) -> str:
        return self.postal_code.city

    @property
    def shares_count(self) -> int:
        if not self.share_number_start:
            return 0

        return self.share_number_end - self.share_number_start + 1

    @property
    def old_hitas_ruleset(self) -> bool:
        return self.housing_company.financing_method.old_hitas_ruleset

    @property
    def address(self) -> str:
        return f"{self.street_address} {self.stair} {self.apartment_number}"

    @property
    def is_new(self) -> bool:
        today = timezone.now().date()
        if self.completion_date is None or self.completion_date > today:
            return True

        # Fetch all sales to take advantage of prefetch cache.
        sales = list(self.sales.all())
        no_sales = len(sales) < 1

        no_first_purchase_or_in_the_future = self.first_purchase_date is None or self.first_purchase_date > today
        no_first_sale_or_in_the_future = (
            no_sales
            # Sort the sales to be sure we select the first sale in case prefetch cache has some other sorting
            or sorted(sales, key=lambda sale: sale.purchase_date)[0].purchase_date > today
        )

        return no_first_purchase_or_in_the_future and no_first_sale_or_in_the_future

    @property
    def sell_by_date(self):
        sell_by_dates: set[datetime.date] = set()

        for ownership in self.ownerships.all():
            for cos in chain(ownership.conditions_of_sale_new.all(), ownership.conditions_of_sale_old.all()):
                if cos.fulfilled:
                    continue

                completion_date = cos.new_ownership.apartment.completion_date
                if completion_date is None:
                    continue

                if cos.grace_period == GracePeriod.NOT_GIVEN:
                    sell_by_dates.add(completion_date)
                elif cos.grace_period == GracePeriod.THREE_MONTHS:
                    sell_by_dates.add(completion_date + relativedelta(months=3))
                elif cos.grace_period == GracePeriod.SIX_MONTHS:
                    sell_by_dates.add(completion_date + relativedelta(months=6))

        if not sell_by_dates:
            return None

        return min(sell_by_dates)

    @property
    def has_grace_period(self) -> bool:
        for ownership in self.ownerships.all():
            for cos in chain(ownership.conditions_of_sale_new.all(), ownership.conditions_of_sale_old.all()):
                if cos.fulfilled:
                    continue
                if cos.grace_period != GracePeriod.NOT_GIVEN:
                    return True
        return False

    def change_ownerships(self, ownership_data: list[OwnershipLike], **kwargs: Any) -> list[Ownership]:
        # Mark current ownerships for the apartment as "past"
        Ownership.objects.filter(apartment=self).delete()

        # Replace with the new ownerships
        return Ownership.objects.bulk_create([Ownership(apartment=self, **kwargs, **entry) for entry in ownership_data])

    class Meta:
        verbose_name = _("Apartment")
        verbose_name_plural = _("Apartments")
        ordering = ["id"]

        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_share_number_start_gte_1",
                check=models.Q(share_number_start__gte=1),
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_share_number_end_gte_1",
                check=models.Q(share_number_end__gte=1),
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_share_number_both_set",
                # Don't know if there's a better way to say (share_number_start IS NULL) == (share_number_end IS NULL)
                # at least Q(share_number_start__isnull=Q(share_number_end__isnull=True)) seems not to work
                check=(
                    models.Q(share_number_start__isnull=False, share_number_end__isnull=False)
                    | models.Q(share_number_start__isnull=True, share_number_end__isnull=True)
                ),
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_share_number_start_lte_share_number_end",
                check=models.Q(share_number_end__gte=models.F("share_number_start")),
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_surface_area_gte_0",
                check=models.Q(surface_area__gte=0),
            ),
        ]

    def __str__(self):
        return f"{self.street_address} {self.stair} {self.apartment_number}"

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:{self.pk} ({str(self)})>"


class ApartmentMarketPriceImprovement(HitasImprovement):
    apartment = models.ForeignKey("Apartment", on_delete=models.CASCADE, related_name="market_price_improvements")


class DepreciationPercentage(Enum):
    ZERO = Decimal(0)
    TWO_AND_HALF = Decimal("2.5")
    TEN = Decimal("10.0")

    class Labels:
        ZERO = "0.0"
        TWO_AND_HALF = "2.5"
        TEN = "10.0"


class ApartmentConstructionPriceImprovement(HitasImprovement):
    apartment = models.ForeignKey("Apartment", on_delete=models.CASCADE, related_name="construction_price_improvements")

    depreciation_percentage = EnumField(DepreciationPercentage, default=DepreciationPercentage.TEN)


class ApartmentMaximumPriceCalculation(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    apartment = models.ForeignKey("Apartment", on_delete=models.CASCADE, related_name="max_price_calculations")
    created_at = models.DateTimeField(auto_created=True)
    confirmed_at = models.DateTimeField(null=True)

    calculation_date = models.DateField()
    valid_until = models.DateField()

    maximum_price = HitasModelDecimalField(validators=[MinValueValidator(0)])

    json = models.JSONField(encoder=HitasEncoder, null=True)

    # `CURRENT_JSON_VERSION` can be used to determinate changes in JSON structure in `json` field. This is useful now
    # when we're constantly changing the json version during the development. When JSON format changes during the
    # development, we don't want to be supporting the old versions. Updating this field will hide all old calculations
    # and thus hiding the old formats. When we are ready to go to production, we should change this back to 1. After
    # this can be useful for doing database migrations.
    CURRENT_JSON_VERSION = 5
    json_version = models.SmallIntegerField(default=CURRENT_JSON_VERSION, validators=[MinValueValidator(1)], null=True)

    class Meta:
        verbose_name = _("Apartment maximum price calculation")
        verbose_name_plural = _("Apartment maximum price calculations")


def prefetch_first_sale(lookup_prefix: str = "", ignore: Collection[int] = ()) -> Prefetch:
    """Prefetch only the first sale of an apartment.

    :param lookup_prefix: Add prefix to lookup, e.g. 'ownerships__apartment__'
                          depending on the prefix context. Should end with '__'.
    :param ignore: These sale ID's should be ignored.
    """
    return Prefetch(
        f"{lookup_prefix}sales",
        ApartmentSale.objects.filter(
            id__in=Subquery(
                ApartmentSale.objects.filter(apartment_id=OuterRef("apartment_id"))
                .exclude(id__in=ignore)
                .order_by("purchase_date")
                .values_list("id", flat=True)[:1]
            )
        ),
    )
