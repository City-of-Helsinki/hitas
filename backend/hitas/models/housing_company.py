from crum import get_current_user
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumField
from safedelete.models import SOFT_DELETE_CASCADE

from hitas.models._base import ExternalHitasModel, HitasImprovement, HitasModelDecimalField
from hitas.models.utils import validate_business_id


class HousingCompanyState(Enum):
    NOT_READY = "not_ready"
    LESS_THAN_30_YEARS = "lt_30_years"
    GREATER_THAN_30_YEARS_NOT_FREE = "gt_30_years_not_free"
    GREATER_THAN_30_YEARS_FREE = "gt_30_years_free"
    GREATER_THAN_30_YEARS_PLOT_DEPARTMENT_NOTIFICATION = "gt_30_years_plot_department_notification"
    HALF_HITAS = "half_hitas"
    READY_NO_STATISTICS = "ready_no_statistics"

    class Labels:
        NOT_READY = _("Not Ready")
        LESS_THAN_30_YEARS = _("Less than 30 years")
        GREATER_THAN_30_YEARS_NOT_FREE = _("Greater than 30 years, not free")
        GREATER_THAN_30_YEARS_FREE = _("Greater than 30 years, free")
        GREATER_THAN_30_YEARS_PLOT_DEPARTMENT_NOTIFICATION = _("Greater than 30 years, plot department notification")
        HALF_HITAS = _("Half hitas")  # Puolihtas
        READY_NO_STATISTICS = _("Ready, no statistics")


# Taloyhtiö
class HousingCompany(ExternalHitasModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    # Official spelling of the housing company name
    official_name = models.CharField(max_length=1024, unique=True)
    # More human-friendly housing company name
    display_name = models.CharField(max_length=1024, unique=True)

    state = EnumField(HousingCompanyState, default=HousingCompanyState.NOT_READY, max_length=40)
    # Business ID / 'y-tunnus'
    business_id = models.CharField(
        max_length=9, validators=[validate_business_id], help_text=_("Format: 1234567-8"), null=True
    )

    street_address = models.CharField(max_length=1024)
    postal_code = models.ForeignKey("HitasPostalCode", on_delete=models.PROTECT, related_name="housing_companies")

    building_type = models.ForeignKey("BuildingType", on_delete=models.PROTECT, related_name="housing_companies")
    financing_method = models.ForeignKey("FinancingMethod", on_delete=models.PROTECT, related_name="housing_companies")
    property_manager = models.ForeignKey(
        "PropertyManager", on_delete=models.PROTECT, related_name="housing_companies", null=True
    )
    developer = models.ForeignKey("Developer", on_delete=models.PROTECT, related_name="housing_companies")

    # 'hankinta-arvo'
    acquisition_price = HitasModelDecimalField()
    # 'ensisijaislaina'
    primary_loan = HitasModelDecimalField(null=True, blank=True)
    # 'Myyntihintaluettelon vahvistamispäivä'
    sales_price_catalogue_confirmation_date = models.DateField(null=True, blank=True)
    # 'ilmoituspäivä'
    notification_date = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True)
    last_modified_datetime = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, related_name="housing_companies"
    )

    @property
    def city(self):
        return self.postal_code.city

    @property
    def area(self):
        return self.postal_code.cost_area

    @property
    def area_display(self):
        return f"{self.city}-{self.area}: {self.postal_code.value}"

    def save(self, *args, **kwargs):
        current_user = get_current_user()
        if current_user is not None and current_user.is_authenticated:
            self.last_modified_by = current_user
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Housing company")
        verbose_name_plural = _("Housing companies")
        ordering = ["id"]

        constraints = [
            models.CheckConstraint(name="acquisition_price_positive", check=models.Q(acquisition_price__gte=0)),
        ]

    def __str__(self):
        return self.display_name


class HousingCompanyMarketPriceImprovement(HitasImprovement):
    housing_company = models.ForeignKey(
        "HousingCompany", on_delete=models.CASCADE, related_name="market_price_improvements"
    )


class HousingCompanyConstructionPriceImprovement(HitasImprovement):
    housing_company = models.ForeignKey(
        "HousingCompany", on_delete=models.CASCADE, related_name="construction_price_improvements"
    )
