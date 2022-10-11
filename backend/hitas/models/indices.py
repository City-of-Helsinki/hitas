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
        verbose_name = _("Market price index for apartments constructed before January 2011")
        verbose_name_plural = _("Market price indices for apartment constructed before January 2011")


class MarketPriceIndex2005Equal100(AbstractIndex):
    class Meta:
        verbose_name = _("Market price index for apartments constructed in January 2011 onwards")
        verbose_name_plural = _("Market price indices for apartment constructed in January 2011 onwards")


# 'Rakennuskustannusindeksi'
class ConstructionPriceIndex(AbstractIndex):
    class Meta:
        verbose_name = _("Construction price index for apartments constructed before January 2011")
        verbose_name_plural = _("Construction price indices for apartments constructed before January 2011")


class ConstructionPriceIndex2005Equal100(AbstractIndex):
    class Meta:
        verbose_name = _("Construction price index year for apartments constructed in January 2005 onwards")
        verbose_name_plural = _("Construction price indices for apartments constructed in January 2005 onwards")


# 'Rajaneliöhinta'
class SurfaceAreaPriceCeiling(AbstractIndex):
    class Meta:
        verbose_name = _("Surface area price ceiling")
        verbose_name_plural = _("Surface area price ceiling")
