from django.contrib import admin

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models import ConditionOfSale


@admin.register(ConditionOfSale)
class ConditionOfSaleAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    model = ConditionOfSale
