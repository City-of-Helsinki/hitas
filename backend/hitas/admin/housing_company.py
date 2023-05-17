from django.contrib import admin
from nested_inline.admin import NestedModelAdmin, NestedTabularInline

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models import (
    Building,
    HousingCompany,
    HousingCompanyConstructionPriceImprovement,
    HousingCompanyMarketPriceImprovement,
    RealEstate,
)


class HousingCompanyMarketPriceImprovementAdmin(NestedTabularInline):
    model = HousingCompanyMarketPriceImprovement


class HousingCompanyConstructionPriceImprovementAdmin(NestedTabularInline):
    model = HousingCompanyConstructionPriceImprovement


class BuildingAdmin(NestedTabularInline):
    model = Building
    extra = 1


class RealEstateAdmin(NestedTabularInline):
    model = RealEstate
    extra = 1
    inlines = (BuildingAdmin,)


@admin.register(HousingCompany)
class HousingCompanyAdmin(AuditLogHistoryAdminMixin, NestedModelAdmin):
    model = HousingCompany
    inlines = (
        RealEstateAdmin,
        HousingCompanyMarketPriceImprovementAdmin,
        HousingCompanyConstructionPriceImprovementAdmin,
    )
    readonly_fields = ("id", "uuid", "city", "area_display")
