from django import forms
from django.contrib import admin
from subforms.fields import DynamicArrayField

from hitas.admin.audit_log import AuditLogHistoryAdminMixin
from hitas.models.pdf_body import PDFBody


class PDFBodyAdminForm(forms.ModelForm):
    texts = DynamicArrayField(subfield=forms.CharField(max_length=10_000, widget=forms.Textarea))

    class Meta:
        model = PDFBody
        fields = [
            "name",
            "texts",
        ]


@admin.register(PDFBody)
class PDFBodyAdmin(AuditLogHistoryAdminMixin, admin.ModelAdmin):
    form = PDFBodyAdminForm
    list_display = ["name"]
