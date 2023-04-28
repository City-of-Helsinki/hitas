import logging

from django.contrib import admin
from django.db.models import QuerySet

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models import Owner
from hitas.models.ownership import Ownership
from hitas.services.owner import log_access_if_owner_has_non_disclosure

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

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            queryset: QuerySet[Owner] = response.context_data["cl"].queryset
            for owner in queryset:
                log_access_if_owner_has_non_disclosure(owner)
        except Exception as error:
            logger.exception("Couldn't log access to owners.", exc_info=error)

        return response

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        log_access_if_owner_has_non_disclosure(obj)
        return obj


@admin.register(Ownership)
class OwnershipAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    list_display = [
        "apartment",
        "owner",
        "percentage",
    ]

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            queryset: QuerySet[Ownership] = response.context_data["cl"].queryset
            for ownership in queryset:
                log_access_if_owner_has_non_disclosure(ownership.owner)
        except Exception as error:
            logger.exception("Couldn't log access to owners.", exc_info=error)

        return response

    def get_object(self, request, object_id, from_field=None):
        obj: Ownership = super().get_object(request, object_id, from_field)
        log_access_if_owner_has_non_disclosure(obj.owner)
        return obj
