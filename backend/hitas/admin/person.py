from django.contrib import admin

from hitas.models import Person
from hitas.models.ownership import Ownership


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = [
        "last_name",
        "first_name",
        "email",
    ]
    readonly_fields = ("uuid",)


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = [
        "apartment",
        "owner",
        "percentage",
        "start_date",
        "end_date",
    ]
