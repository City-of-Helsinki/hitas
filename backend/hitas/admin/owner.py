import logging

from django.contrib import admin

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models import Owner
from hitas.models.ownership import Ownership

logger = logging.getLogger(__name__)


@admin.register(Owner)
class OwnerAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    list_display = [
        "name",
        "email",
        "bypass_conditions_of_sale",
    ]
    readonly_fields = [
        "uuid",
    ]


@admin.register(Ownership)
class OwnershipAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    list_display = [
        "apartment",
        "owner",
        "percentage",
    ]
