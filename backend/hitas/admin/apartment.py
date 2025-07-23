from django.contrib import admin
from nested_inline.admin import NestedTabularInline

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models import (
    Apartment,
    ApartmentConstructionPriceImprovement,
    ApartmentMarketPriceImprovement,
    ApartmentMaximumPriceCalculation,
)


class ApartmentMarketPriceImprovementAdmin(NestedTabularInline):
    model = ApartmentMarketPriceImprovement


class ApartmentConstructionPriceImprovementAdmin(NestedTabularInline):
    model = ApartmentConstructionPriceImprovement


@admin.register(Apartment)
class ApartmentAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    list_display = [
        "housing_company",
        "street_address",
        "apartment_number",
        "stair",
        "postal_code",
        "surface_area",
        "completion_date",
    ]

    list_filter = [
        "completion_date",
        "building__real_estate__housing_company",
    ]

    readonly_fields = ("uuid",)

    inlines = (
        ApartmentMarketPriceImprovementAdmin,
        ApartmentConstructionPriceImprovementAdmin,
    )

    def housing_company(self, obj):
        return obj.building.real_estate.housing_company


@admin.register(ApartmentMaximumPriceCalculation)
class ApartmentMaximumPriceCalculationAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    list_display = [
        "uuid",
        "apartment",
        "maximum_price",
        "calculation_date",
        "valid_until",
        "confirmed_at",
    ]
    search_fields = ["apartment__street_address", "apartment__apartment_number"]
    list_filter = ["calculation_date", "confirmed_at"]

    readonly_fields = ("uuid",)

    def apartment(self, obj):
        return obj.apartment
