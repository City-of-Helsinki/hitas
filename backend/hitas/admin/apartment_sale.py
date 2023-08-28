from django.contrib import admin

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models import ApartmentSale


@admin.register(ApartmentSale)
class ApartmentSaleAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    model = ApartmentSale

    list_display = [
        "apartment",
        "purchase_date",
        "purchase_price",
        "exclude_from_statistics",
    ]

    list_filter = [
        "purchase_date",
        "exclude_from_statistics",
    ]
