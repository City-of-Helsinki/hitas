import uuid
from decimal import Decimal
from typing import Optional

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumField
from safedelete import SOFT_DELETE_CASCADE

from hitas.models._base import ExternalHitasModel, HitasImprovement, HitasModelDecimalField
from hitas.models.housing_company import HousingCompany
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

    # 'Luovutushinta'
    debt_free_purchase_price = HitasModelDecimalField(null=True)
    # 'Ensisijaislaina'
    primary_loan_amount = HitasModelDecimalField(default=0, null=True)
    # 'Kauppakirjahinta'
    purchase_price = HitasModelDecimalField(null=True, blank=True)
    # 'Ensimmäinen kauppakirjapvm'
    first_purchase_date = models.DateField(null=True, blank=True)
    # 'Viimeisin kauppakirjapvm'
    latest_purchase_date = models.DateField(null=True, blank=True)
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
    def address(self) -> str:
        return f"{self.street_address} {self.stair} {self.apartment_number}"

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
        return f"{self.street_address} {self.apartment_number}"


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
