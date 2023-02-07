from django.contrib import admin

from hitas.models import Owner
from hitas.models.ownership import Ownership


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "email",
        "bypass_conditions_of_sale",
    ]
    readonly_fields = [
        "uuid",
    ]


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = [
        "apartment",
        "owner",
        "percentage",
    ]
