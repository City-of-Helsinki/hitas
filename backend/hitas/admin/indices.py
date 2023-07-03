from django.contrib import admin

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models import (
    ConstructionPriceIndex,
    ConstructionPriceIndex2005Equal100,
    MarketPriceIndex,
    MarketPriceIndex2005Equal100,
    MaximumPriceIndex,
    SurfaceAreaPriceCeiling,
)


@admin.register(
    MaximumPriceIndex,
    ConstructionPriceIndex,
    ConstructionPriceIndex2005Equal100,
    MarketPriceIndex,
    MarketPriceIndex2005Equal100,
    SurfaceAreaPriceCeiling,
)
class IndexAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    list_display = ["value", "month"]
    fields = list_display
