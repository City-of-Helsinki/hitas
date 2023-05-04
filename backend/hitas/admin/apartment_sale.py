from django.contrib import admin

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models import ApartmentSale


@admin.register(ApartmentSale)
class ApartmentSaleAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    model = ApartmentSale
