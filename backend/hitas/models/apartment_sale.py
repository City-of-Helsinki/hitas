import datetime
from decimal import Decimal

from auditlog.registry import auditlog
from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalSafeDeleteHitasModel, HitasModelDecimalField


# 'Asunnon myyntitapahtuma' / 'Kauppakirja' / 'Uusi myynti'
class ApartmentSale(ExternalSafeDeleteHitasModel):
    # 'Asunto'
    apartment = models.ForeignKey("Apartment", related_name="sales", on_delete=models.CASCADE, editable=False)

    # "Ilmoituspäivä"
    notification_date: datetime.date = models.DateField()
    # "Kauppakirjan päivämäärä"
    purchase_date: datetime.date = models.DateField()
    # "Kauppahinta"
    purchase_price: Decimal = HitasModelDecimalField()
    # "Yhtiölainaosuus"
    apartment_share_of_housing_company_loans: Decimal = HitasModelDecimalField()
    # "Kirjataanko kauppa tilastoihin?"
    exclude_from_statistics: bool = models.BooleanField(default=False)

    @property
    def total_price(self) -> Decimal:
        # "Velaton kauppahinta"
        return self.purchase_price + self.apartment_share_of_housing_company_loans

    @property
    def cost_area(self) -> int:
        return self.apartment.postal_code.cost_area

    def __str__(self):
        return f"Sale of {self.apartment} on {self.purchase_date}{' (E)' if self.exclude_from_statistics else ''}"

    class Meta:
        verbose_name = _("Apartment sale")
        verbose_name_plural = _("Apartment sales")
        ordering = ["-purchase_date"]


# This is for typing only
class ApartmentSaleWithAnnotations(ApartmentSale):
    sale_count: int

    class Meta:
        abstract = True


auditlog.register(ApartmentSale)
