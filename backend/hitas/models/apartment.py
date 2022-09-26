from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumField
from safedelete import SOFT_DELETE_CASCADE

from hitas.models._base import ExternalHitasModel, HitasImprovement, HitasModelDecimalField


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

    building = models.ForeignKey("Building", on_delete=models.CASCADE, related_name="apartments")

    state = EnumField(ApartmentState, default=ApartmentState.FREE)
    apartment_type = models.ForeignKey("ApartmentType", on_delete=models.PROTECT, related_name="apartments")
    surface_area = HitasModelDecimalField(help_text=_("Measured in m^2"))

    share_number_start = models.IntegerField(null=True, validators=[MinValueValidator(1)])
    share_number_end = models.IntegerField(null=True, validators=[MinValueValidator(1)])

    completion_date = models.DateField(null=True)

    street_address = models.CharField(max_length=128)
    # 'Huoneistonumero'
    apartment_number = models.PositiveSmallIntegerField()
    floor = models.CharField(max_length=50, blank=True, null=True)
    # 'Porras'
    stair = models.CharField(max_length=16)

    # 'Luovutushinta'
    debt_free_purchase_price = models.PositiveIntegerField(default=0)
    # 'Ensisijaislaina'
    primary_loan_amount = models.PositiveIntegerField(default=0)
    # 'Kauppakirjahinta'
    purchase_price = HitasModelDecimalField(blank=True, null=True)
    # '1. kauppakirjapvm'
    first_purchase_date = models.DateField(null=True, blank=True)
    # '2. kauppakirjapvm'
    second_purchase_date = models.DateField(null=True, blank=True)
    # 'Rakennusaikaiset lisätyöt'
    additional_work_during_construction = models.PositiveIntegerField(default=0)
    # 'Rakennusaikaiset lainat'
    loans_during_construction = models.PositiveIntegerField(default=0)
    # 'Rakennusaikaiset korot'
    interest_during_construction = models.PositiveIntegerField(default=0)
    # 'Luovutushinta (RA)'
    debt_free_purchase_price_during_construction = models.PositiveIntegerField(default=0)

    notes = models.TextField(blank=True, null=True)

    # 'Hankinta-arvo'
    @property
    def acquisition_price(self):
        return self.debt_free_purchase_price + self.primary_loan_amount

    @property
    def postal_code(self):
        return self.building.postal_code

    @property
    def city(self):
        return self.postal_code().city

    @property
    def shares_count(self) -> int:
        if not self.share_number_start:
            return 0

        return self.share_number_end - self.share_number_start + 1

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
    ZERO = 0.0
    TWO_AND_HALF = 2.5
    TEN = 10.0

    class Labels:
        ZERO = "0.0"
        TWO_AND_HALF = "2.5"
        TEN = "10.0"


class ApartmentConstructionPriceImprovement(HitasImprovement):
    apartment = models.ForeignKey("Apartment", on_delete=models.CASCADE, related_name="construction_price_improvements")

    depreciation_percentage = EnumField(DepreciationPercentage, default=DepreciationPercentage.TEN)
