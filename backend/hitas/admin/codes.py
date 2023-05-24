from django.contrib import admin

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models import ApartmentType, BuildingType, Developer


@admin.register(BuildingType, Developer, ApartmentType)
class CodeAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    list_display = [
        "value",
        "description",
        "in_use",
        "order",
        "legacy_code_number",
        "legacy_start_date",
        "legacy_end_date",
    ]
    fields = ["uuid"] + list_display
    readonly_fields = [
        "uuid",
        "legacy_code_number",
        "legacy_start_date",
        "legacy_end_date",
    ]
