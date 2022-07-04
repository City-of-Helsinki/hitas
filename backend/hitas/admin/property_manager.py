from django.contrib import admin

from hitas.models import PropertyManager


@admin.register(PropertyManager)
class PropertyManagerAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "email",
        "street_address",
        "postal_code",
    ]
    fields = ["uuid"] + list_display
    readonly_fields = ("uuid",)
