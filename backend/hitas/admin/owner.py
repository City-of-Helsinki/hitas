import logging

from django.contrib import admin

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models import Owner
from hitas.models.housing_company import RegulationStatus
from hitas.models.ownership import Ownership
from hitas.services.owner import exclude_obfuscated_owners

logger = logging.getLogger(__name__)


@admin.register(Owner)
class OwnerAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    list_display = [
        "name",
        "identifier",
        "email",
        "bypass_conditions_of_sale",
        "non_disclosure",
    ]
    readonly_fields = [
        "uuid",
    ]
    list_filter = [
        "valid_identifier",
        "bypass_conditions_of_sale",
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return exclude_obfuscated_owners(qs)


@admin.register(Ownership)
class OwnershipAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    list_display = [
        "apartment",
        "owner",
        "percentage",
    ]

    readonly_fields = [
        "owner",
        "sale",
        "conditions_of_sale",
        "percentage",
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            sale__apartment__building__real_estate__housing_company__regulation_status=RegulationStatus.REGULATED
        )
