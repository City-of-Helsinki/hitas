from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumField

from hitas.models._base import ExternalHitasModel, HitasModelDecimalField
from hitas.models.utils import validate_share_numbers


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
    building = models.ForeignKey("Building", on_delete=models.PROTECT, related_name="apartments")

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

    notes = models.TextField(blank=True)

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

    def validate_share_numbers(self) -> None:
        validate_share_numbers(start=self.share_number_start, end=self.share_number_end)

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
