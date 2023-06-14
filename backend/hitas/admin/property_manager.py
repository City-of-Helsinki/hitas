from django.contrib import admin

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models import PropertyManager


@admin.register(PropertyManager)
class PropertyManagerAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    list_display = [
        "name",
        "email",
    ]
    fields = ["uuid"] + list_display
    readonly_fields = ("uuid",)
