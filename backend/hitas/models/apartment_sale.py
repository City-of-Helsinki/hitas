from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import ExternalHitasModel, HitasModelDecimalField


# 'Asunnon myyntitapahtuma' / 'Kauppakirja' / 'Uusi myynti'
class ApartmentSale(ExternalHitasModel):

    apartment = models.ForeignKey("Apartment", related_name="sales", on_delete=models.CASCADE)

    # "Ilmoituspäivä"
    notification_date = models.DateField()
    # "Kauppakirjan päivämäärä"
    purchase_date = models.DateField()
    # "Kauppahinta"
    purchase_price = HitasModelDecimalField()
    # "Yhtiölainaosuus"
    apartment_share_of_housing_company_loans = HitasModelDecimalField()
    # "Kirjataanko kauppa tilastoihin?"
    exclude_in_statistics = models.BooleanField(default=False)

    @property
    def total_price(self) -> Decimal:
        # "Velaton kokonaishinta"
        return self.purchase_price + self.apartment_share_of_housing_company_loans

    @property
    def cost_area(self) -> int:
        return self.apartment.postal_code.cost_area

    def __str__(self):
        return f"Sale of {self.apartment} on {self.purchase_date}{' (E)' if self.exclude_in_statistics else ''}"

    class Meta:
        verbose_name = _("Apartment sale")
        verbose_name_plural = _("Apartment sales")
        ordering = ["-purchase_date"]
