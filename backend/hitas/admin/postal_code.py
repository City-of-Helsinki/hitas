from django.contrib import admin

from hitas.models import HitasPostalCode


@admin.register(HitasPostalCode)
class HitasPostalCodeAdmin(admin.ModelAdmin):
    list_display = [
        "value",
        "city",
        "cost_area",
    ]
    fields = ["uuid"] + list_display
    readonly_fields = [
        "uuid",
    ]
    ordering = ["value"]
