from django.contrib import admin

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models import ExternalSalesData


@admin.register(ExternalSalesData)
class ExternalSalesDataAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    model = ExternalSalesData
