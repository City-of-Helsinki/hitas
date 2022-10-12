from django.contrib import admin
from nested_inline.admin import NestedModelAdmin, NestedTabularInline

from hitas.models import (
    Apartment,
    ApartmentConstructionPriceImprovement,
    ApartmentMarketPriceImprovement,
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
class HousingCompanyAdmin(NestedModelAdmin):
    model = HousingCompany
    inlines = (
        RealEstateAdmin,
        HousingCompanyMarketPriceImprovementAdmin,
        HousingCompanyConstructionPriceImprovementAdmin,
    )
    readonly_fields = ("last_modified_datetime", "last_modified_by", "id", "uuid", "city", "area_display")


class ApartmentMarketPriceImprovementAdmin(NestedTabularInline):
    model = ApartmentMarketPriceImprovement


class ApartmentConstructionPriceImprovementAdmin(NestedTabularInline):
    model = ApartmentConstructionPriceImprovement


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = [
        "street_address",
        "apartment_number",
        "postal_code",
        "state",
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
