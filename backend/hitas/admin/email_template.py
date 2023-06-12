from django.contrib import admin

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models.email_template import EmailTemplate


@admin.register(EmailTemplate)
class EmailTemplateAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    list_display = ["name"]
