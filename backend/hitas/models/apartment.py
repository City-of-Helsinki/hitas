from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumField

from hitas.models._base import ExternalHitasModel, HitasModelDecimalField


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
    apartment_type = models.ForeignKey("ApartmentType", on_delete=models.PROTECT)
    surface_area = HitasModelDecimalField(help_text=_("Measured in m^2"))

    share_number_start = models.PositiveIntegerField(null=True)
    share_number_end = models.PositiveIntegerField(null=True)

    street_address = models.CharField(max_length=128)
    postal_code = models.ForeignKey("PostalCode", on_delete=models.PROTECT)
    # 'Huoneistonumero'
    apartment_number = models.PositiveSmallIntegerField()
    floor = models.PositiveSmallIntegerField(default=1)
    # 'Porras'
    stair = models.CharField(max_length=16)

    # 'Luovutushinta'
    debt_free_purchase_price = HitasModelDecimalField(blank=True, null=True)
    # 'Kauppakirjahinta'
    purchase_price = HitasModelDecimalField(blank=True, null=True)
    # 'Hankinta-arvo'
    acquisition_price = HitasModelDecimalField(blank=True, null=True)
    # 'Ensisijaislaina'
    primary_loan_amount = HitasModelDecimalField(blank=True, null=True)
    # 'Rakennusaikaiset loans'
    loans_during_construction = HitasModelDecimalField(blank=True, null=True)
    # 'Rakennusaikaiset korot'
    interest_during_construction = HitasModelDecimalField(blank=True, null=True)

    notes = models.TextField(blank=True)

    @property
    def shares_count(self) -> int:
        return self.share_number_end - self.share_number_start + 1

    @property
    def share_numbers(self) -> str:
        return f"{self.share_number_start} - {self.share_number_end}"

    def validate_share_numbers(self) -> None:
        # TODO Validate overlap in share numbers across other HousingCompany shares
        if self.share_number_start is None and self.share_number_end is None:
            return
        if self.share_number_start is None or self.share_number_end is None:
            raise ValidationError(
                _("You must enter both: %(start)s and %(end)s or neither."),
                params={"start": "share_number_start", "end": "share_number_end"},
            )
        if self.share_number_start > self.share_number_end:
            raise ValidationError(
                _("%(start)s must not be greater than %(end)s"),
                params={"start": "share_number_start", "end": "share_number_end"},
            )

    class Meta:
        verbose_name = _("Apartment")
        verbose_name_plural = _("Apartments")
        ordering = ["id"]

    def __str__(self):
        return f"{self.street_address} {self.apartment_number}"
