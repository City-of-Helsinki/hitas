from django.contrib import admin

from hitas.models.property_manager import PropertyManager


@admin.register(PropertyManager)
class PropertyManagerAdmin(admin.ModelAdmin):
    pass
