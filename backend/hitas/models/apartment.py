import uuid
from datetime import date
from decimal import Decimal
from itertools import chain
from typing import Any, Optional

from dateutil.relativedelta import relativedelta
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumField
from safedelete import SOFT_DELETE_CASCADE

from hitas.models._base import ExternalHitasModel, HitasImprovement, HitasMarketPriceImprovement, HitasModelDecimalField
from hitas.models.apartment_sale import ApartmentSale, ApartmentSaleWithAnnotations
from hitas.models.condition_of_sale import ConditionOfSaleAnnotated, GracePeriod
from hitas.models.housing_company import HousingCompany
from hitas.models.ownership import Ownership, OwnershipLike
from hitas.models.postal_code import HitasPostalCode
from hitas.types import HitasEncoder
from hitas.utils import subquery_count


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

    # 'Myyntihintaluettelon luovutushinta'
    catalog_purchase_price: Optional[Decimal] = HitasModelDecimalField(null=True)
    # 'Myyntihintaluettelon ensisijaislaina'
    catalog_primary_loan_amount: Optional[Decimal] = HitasModelDecimalField(null=True)

    # 'Rakennusaikaiset lisätyöt'
    additional_work_during_construction: Optional[Decimal] = HitasModelDecimalField(null=True)
    # 'Rakennusaikaiset lainat'
    loans_during_construction: Optional[Decimal] = HitasModelDecimalField(null=True)
    # 'Rakennusaikaiset korot 6%'
    interest_during_construction_6: Optional[Decimal] = HitasModelDecimalField(null=True)
    # 'Rakennusaikaiset korot 14%'
    interest_during_construction_14: Optional[Decimal] = HitasModelDecimalField(null=True)
    # 'Luovutushinta (RA)'
    debt_free_purchase_price_during_construction: Optional[Decimal] = HitasModelDecimalField(null=True)

    notes = models.TextField(blank=True, null=True)

    # 'Myyntihintaluettelon Hankinta-arvo' = Myyntihintaluettelon kauppakirjahinta + yhtiölainaosuus
    @property
    def catalog_acquisition_price(self) -> Optional[Decimal]:
        if self.catalog_purchase_price is not None and self.catalog_primary_loan_amount is not None:
            return self.catalog_purchase_price + self.catalog_primary_loan_amount

        return None

    # 'Hankinta-arvo' = Ensimmäisen kaupan kauppakirjahinta + yhtiölainaosuus
    @property
    def first_sale_acquisition_price(self) -> Optional[Decimal]:
        if self.first_sale_purchase_price is not None and self.first_sale_share_of_housing_company_loans is not None:
            return self.first_sale_purchase_price + self.first_sale_share_of_housing_company_loans

        return None

    # 'Luovutushinta' = Ensimmäisen kaupan kauppakirjahinta
    @property
    def first_sale_purchase_price(self) -> Optional[Decimal]:
        # Allow caches for the instance
        if hasattr(self, "_first_sale_purchase_price"):
            return self._first_sale_purchase_price

        first_sale = self.first_sale
        self._first_sale_purchase_price = first_sale.purchase_price if first_sale is not None else None
        return self._first_sale_purchase_price

    # 'Ensisijaislaina' = Ensimmäisen kaupan yhtiölainaosuus
    @property
    def first_sale_share_of_housing_company_loans(self) -> Optional[Decimal]:
        # Allow caches for the instance
        if hasattr(self, "_first_sale_share_of_housing_company_loans"):
            return self._first_sale_share_of_housing_company_loans

        first_sale = self.first_sale
        self._first_sale_share_of_housing_company_loans = (
            first_sale.apartment_share_of_housing_company_loans if first_sale is not None else None
        )
        return self._first_sale_share_of_housing_company_loans

    # 'Viimeisin Kauppakirjahinta'
    @property
    def latest_sale_purchase_price(self) -> Optional[Decimal]:
        # Allow caches for the instance
        if hasattr(self, "_latest_sale_purchase_price"):
            return self._latest_sale_purchase_price

        latest_sale = self.latest_sale_with_sale_count
        self._latest_sale_purchase_price = None
        if latest_sale is None:
            return None
        if latest_sale.sale_count < 2:
            return None
        self._latest_sale_purchase_price = latest_sale.purchase_price
        return self._latest_sale_purchase_price

    # 'Viimeisin yhtiölainaosuus'
    @property
    def latest_sale_share_of_housing_company_loans(self) -> Optional[Decimal]:
        # Allow caches for the instance
        if hasattr(self, "_latest_sale_share_of_housing_company_loans"):
            return self._latest_sale_share_of_housing_company_loans

        latest_sale = self.latest_sale_with_sale_count
        self._latest_sale_share_of_housing_company_loans = None
        if latest_sale is None:
            return None
        if latest_sale.sale_count < 2:
            return None
        self._latest_sale_share_of_housing_company_loans = latest_sale.apartment_share_of_housing_company_loans
        return self._latest_sale_share_of_housing_company_loans

    # 'Ensimmäinen kauppakirjapvm'
    @property
    def first_purchase_date(self) -> Optional[date]:
        # Allow caches for the instance
        if hasattr(self, "_first_purchase_date"):
            return self._first_purchase_date

        first_sale = self.first_sale
        self._first_purchase_date = first_sale.purchase_date if first_sale is not None else None
        return self._first_purchase_date

    # 'Viimeisin kauppakirjapvm'
    @property
    def latest_purchase_date(self) -> Optional[date]:
        # Allow caches for the instance
        if hasattr(self, "_latest_purchase_date"):
            return self._latest_purchase_date

        latest_sale = self.latest_sale_with_sale_count
        self._latest_purchase_date = None
        if latest_sale is None:
            return None
        if latest_sale.sale_count < 2:
            return None
        self._latest_purchase_date = latest_sale.purchase_date
        return self._latest_purchase_date

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
        """Is this apartment considered new for the purposes of creating conditions of sale?"""
        today = timezone.now().date()
        if self.completion_date is None or self.completion_date > today:
            return True

        # Fetch all sales to take advantage of prefetch cache.
        # Sort the sales to be sure we select the first sale in case prefetch cache has some other sorting.
        sales = sorted(self.sales.all(), key=lambda sale: sale.purchase_date)
        if not sales:
            return True

        return sales[0].purchase_date > today

    @property
    def sell_by_date(self):
        """
        Calculate the sell by date for an apartment based on its conditions of sale.

        Apartment should have its ownerships with their conditions of sales prefetched,
        and each condition of sale should have its apartment's completion date joined,
        and the apartment's first sale date annotated as 'first_purchase_date'.
        """
        sell_by_dates: set[date] = set()

        for ownership in self.ownerships.all():
            cos: ConditionOfSaleAnnotated
            for cos in chain(ownership.conditions_of_sale_new.all(), ownership.conditions_of_sale_old.all()):
                if cos.fulfilled:
                    continue

                # If the apartment has not been completed, there is no sell by date yet.
                sell_by_date = cos.new_ownership.apartment.completion_date
                if sell_by_date is None:
                    continue

                # If apartment was first sold after it was completed,
                # the sell by date is calculated based on first sale date.
                if cos.first_purchase_date is not None and cos.first_purchase_date > sell_by_date:
                    sell_by_date = cos.first_purchase_date

                # If grace period has been given, it should be included
                if cos.grace_period == GracePeriod.THREE_MONTHS:
                    sell_by_date += relativedelta(months=3)
                elif cos.grace_period == GracePeriod.SIX_MONTHS:
                    sell_by_date += relativedelta(months=6)

                sell_by_dates.add(sell_by_date)

        if not sell_by_dates:
            return None

        # If apartment has multiple conditions of sale, the earliest sell by date is counted.
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

    @cached_property
    def first_sale(self) -> Optional[ApartmentSale]:
        return self.sales.order_by("purchase_date").first()

    @cached_property
    def latest_sale_with_sale_count(self) -> Optional[ApartmentSaleWithAnnotations]:
        """Get the latest sale for this apartment, with the total number of sales annotated."""
        return (
            self.sales.annotate(
                sale_count=subquery_count(ApartmentSale, "apartment_id"),
            )
            .order_by("purchase_date")
            .last()
        )

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


# This is for typing only
class ApartmentWithAnnotations(Apartment):
    completion_month: Optional[date]
    cpi: Optional[Decimal]
    cpi_2005_100: Optional[Decimal]
    mpi: Optional[Decimal]
    mpi_2005_100: Optional[Decimal]
    sapc: Optional[Decimal]
    _first_sale_purchase_price: Optional[Decimal]
    _first_sale_share_of_housing_company_loans: Optional[Decimal]
    _latest_sale_purchase_price: Optional[Decimal]
    _first_purchase_date: Optional[date]
    _latest_purchase_date: Optional[date]
    has_conditions_of_sale: Optional[bool]

    class Meta:
        abstract = True


# This is for typing only
class ApartmentWithAnnotationsMaxPrice(Apartment):
    _first_sale_purchase_price: Optional[Decimal]
    _first_sale_share_of_housing_company_loans: Optional[Decimal]
    completion_month: Optional[date]
    calculation_date_cpi: Optional[Decimal]
    calculation_date_cpi_2005eq100: Optional[Decimal]
    completion_date_cpi: Optional[Decimal]
    completion_date_cpi_2005eq100: Optional[Decimal]
    calculation_date_mpi: Optional[Decimal]
    calculation_date_mpi_2005eq100: Optional[Decimal]
    completion_date_mpi: Optional[Decimal]
    completion_date_mpi_2005eq100: Optional[Decimal]
    surface_area_price_ceiling_m2: Optional[Decimal]
    surface_area_price_ceiling: Optional[Decimal]
    realized_housing_company_acquisition_price: Optional[Decimal]
    completion_date_realized_housing_company_acquisition_price: Optional[Decimal]

    class Meta:
        abstract = True


class ApartmentMarketPriceImprovement(HitasMarketPriceImprovement):
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
