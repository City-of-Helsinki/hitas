from django.contrib import admin
from nested_inline.admin import NestedTabularInline

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models import Apartment, ApartmentConstructionPriceImprovement, ApartmentMarketPriceImprovement


class ApartmentMarketPriceImprovementAdmin(NestedTabularInline):
    model = ApartmentMarketPriceImprovement


class ApartmentConstructionPriceImprovementAdmin(NestedTabularInline):
    model = ApartmentConstructionPriceImprovement


@admin.register(Apartment)
class ApartmentAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    list_display = [
        "street_address",
        "apartment_number",
        "postal_code",
        "surface_area",
        "housing_company",
    ]
    readonly_fields = ("uuid",)

    inlines = (
        ApartmentMarketPriceImprovementAdmin,
        ApartmentConstructionPriceImprovementAdmin,
    )

    def housing_company(self, obj):
        return obj.building.real_estate.housing_company
