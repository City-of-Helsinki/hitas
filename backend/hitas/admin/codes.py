from django.contrib import admin

from hitas.models.codes import BuildingType, Developer, FinancingMethod, PostalCode


@admin.register(BuildingType, FinancingMethod, PostalCode, Developer)
class CodeAdmin(admin.ModelAdmin):
    list_display = (
        "value",
        "description",
        "in_use",
        "order",
        "legacy_code_number",
        "legacy_start_date",
        "legacy_end_date",
    )
