from django.contrib import admin

from hitas.models import PropertyManager


@admin.register(PropertyManager)
class PropertyManagerAdmin(admin.ModelAdmin):
    pass
