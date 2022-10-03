from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import HitasModelDecimalField


class AbstractIndex(models.Model):
    month = models.DateField(primary_key=True)
    value = HitasModelDecimalField()

    class Meta:
        abstract = True


# 'Enimmäishintaindeksi'
class MaxPriceIndex(AbstractIndex):
    class Meta:
        verbose_name = _("Max price index")
        verbose_name_plural = _("Max price indices")


# 'Markkinahintaindeksi'
class MarketPriceIndex(AbstractIndex):
    class Meta:
        verbose_name = _("Market price index for apartments constructed in January 2005 or after")
        verbose_name_plural = _("Market price indices for apartment constructed in January 2005 or after")


class MarketPriceIndexPre2005(AbstractIndex):
    class Meta:
        verbose_name = _("Market price index for apartments constructed before January 2005")
        verbose_name_plural = _("Market price indices for apartment constructed before January 2005")


# 'Rakennuskustannusindeksi'
class ConstructionPriceIndex(AbstractIndex):
    class Meta:
        verbose_name = _("Construction price index year for apartments constructed in January 2005 and after")
        verbose_name_plural = _("Construction price indices for apartments constructed in January 2005 and after")


class ConstructionPriceIndexPre2005(AbstractIndex):
    class Meta:
        verbose_name = _("Construction price index for apartments constructed before January 2005")
        verbose_name_plural = _("Construction price indices for apartments constructed before January 2005")
