from django.contrib import admin

from hitas.models import Person
from hitas.models.owner import Owner


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = [
        "last_name",
        "first_name",
        "social_security_number",
    ]
    readonly_fields = ("uuid",)


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = [
        "apartment",
        "person",
        "ownership_percentage",
        "ownership_start_date",
        "ownership_end_date",
    ]
