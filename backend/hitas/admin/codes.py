from django.contrib import admin

from hitas.models import ApartmentType, BuildingType, Developer, FinancingMethod


@admin.register(BuildingType, FinancingMethod, Developer, ApartmentType)
class CodeAdmin(admin.ModelAdmin):
    list_display = [
        "value",
        "description",
        "in_use",
        "order",
        "legacy_code_number",
        "legacy_start_date",
        "legacy_end_date",
    ]
    fields = ["uuid"] + list_display
    readonly_fields = [
        "uuid",
        "legacy_code_number",
        "legacy_start_date",
        "legacy_end_date",
    ]
