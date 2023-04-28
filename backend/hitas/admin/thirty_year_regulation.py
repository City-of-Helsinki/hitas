from django.contrib import admin
from nested_inline.admin import NestedTabularInline

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models import ThirtyYearRegulationResults, ThirtyYearRegulationResultsRow


class ThirtyYearRegulationResultsRowAdmin(NestedTabularInline):
    model = ThirtyYearRegulationResultsRow
    extra = 1


@admin.register(ThirtyYearRegulationResults)
class ThirtyYearRegulationResultsAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    model = ThirtyYearRegulationResults
    inlines = [ThirtyYearRegulationResultsRowAdmin]
