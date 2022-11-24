from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from hitas.models._base import HitasModelDecimalField


class AbstractIndex(models.Model):
    month = models.DateField(primary_key=True)
    value = HitasModelDecimalField(
        validators=[MinValueValidator(1)],
    )

    class Meta:
        abstract = True


# 'Enimmäishintaindeksi'
class MaximumPriceIndex(AbstractIndex):
    class Meta:
        verbose_name = _("Maximum price index")
        verbose_name_plural = _("Maximum price indices")
        constraints = [
            models.CheckConstraint(name="maximum_price_index_value_positive", check=models.Q(value__gt=0)),
        ]


# 'Markkinahintaindeksi'
class MarketPriceIndex(AbstractIndex):
    class Meta:
        verbose_name = _("Market price index for apartments constructed before January 2011")
        verbose_name_plural = _("Market price indices for apartment constructed before January 2011")
        constraints = [
            models.CheckConstraint(name="market_price_index_value_positive", check=models.Q(value__gt=0)),
        ]


class MarketPriceIndex2005Equal100(AbstractIndex):
    class Meta:
        verbose_name = _("Market price index for apartments constructed in January 2011 onwards")
        verbose_name_plural = _("Market price indices for apartment constructed in January 2011 onwards")
        constraints = [
            models.CheckConstraint(name="market_price_2005_index_value_positive", check=models.Q(value__gt=0)),
        ]


# 'Rakennuskustannusindeksi'
class ConstructionPriceIndex(AbstractIndex):
    class Meta:
        verbose_name = _("Construction price index for apartments constructed before January 2011")
        verbose_name_plural = _("Construction price indices for apartments constructed before January 2011")
        constraints = [
            models.CheckConstraint(name="construction_price_index_value_positive", check=models.Q(value__gt=0)),
        ]


class ConstructionPriceIndex2005Equal100(AbstractIndex):
    class Meta:
        verbose_name = _("Construction price index year for apartments constructed in January 2005 onwards")
        verbose_name_plural = _("Construction price indices for apartments constructed in January 2005 onwards")
        constraints = [
            models.CheckConstraint(name="construction_price_2005_index_value_positive", check=models.Q(value__gt=0)),
        ]


# 'Rajaneliöhinta'
class SurfaceAreaPriceCeiling(AbstractIndex):
    class Meta:
        verbose_name = _("Surface area price ceiling")
        verbose_name_plural = _("Surface area price ceiling")
