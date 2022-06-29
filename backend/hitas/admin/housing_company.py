from django.contrib import admin
from nested_inline.admin import NestedModelAdmin, NestedTabularInline

from hitas.models import Building, HousingCompany, RealEstate


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
    inlines = (RealEstateAdmin,)
    readonly_fields = ("last_modified_datetime", "last_modified_by", "id", "uuid", "city", "area_display")
