from django.contrib import admin

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models import HitasPostalCode


@admin.register(HitasPostalCode)
class HitasPostalCodeAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
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
