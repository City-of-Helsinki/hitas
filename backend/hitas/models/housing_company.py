import re

from crum import get_current_user
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumIntegerField

from hitas.models._base import ExternalHitasModel
from hitas.models.areas import hitas_city, hitas_cost_area
from hitas.models.codes import BuildingType, Developer, FinancingMethod, PostalCode
from hitas.models.property_manager import PropertyManager


def validate_business_id(value: str) -> None:
    # Example valid value: '1234567-8'
    match = re.search(r"^(\d{7})-(\d)$", value)

    if match is None:
        raise ValidationError(
            _("'%(value)s' is not a valid business id."),
            params={"value": value},
        )

    # TODO: verify business id with the check digit


def validate_property_id(value: str) -> None:
    # Example valid value: '1-1234-321-56'
    match = re.search(r"^\d{1,4}-\d{1,4}-\d{1,4}-\d{1,4}$", value)

    if match is None:
        raise ValidationError(
            _("%(value)s is not an valid property id"),
            params={"value": value},
        )


def validate_building_id(value: str) -> None:
    # Example valid value: '100012345A'
    permanent_building_id_match = re.search(r"^1(\d{8})[A-Za-z0-9]$", value)
    if permanent_building_id_match is not None:
        # TODO: verify building id with the check digit
        return

    building_id_match = re.search(r"^\d{1,4}-\d{1,4}-\d{1,4}-\d{1,4} [A-Za-z0-9] \d{3}$", value)
    if building_id_match is None:
        raise ValidationError(
            _("%(value)s is not an valid property id"),
            params={"value": value},
        )
    # TODO: verify building id with the check digit


class HousingCompanyState(Enum):
    NOT_READY = 0
    LESS_THAN_30_YEARS = 1
    GREATER_THAN_30_YEARS_NOT_FREE = 2
    GREATER_THAN_30_YEARS_FREE = 3
    GREATER_THAN_30_YEARS_PLOT_DEPARTMENT_NOTIFICATION = 4
    READY_NO_STATISTICS = 5

    class Labels:
        NOT_READY = _("Not Ready")
        LESS_THAN_30_YEARS = _("Less than 30 years")
        GREATER_THAN_30_YEARS_NOT_FREE = _("Greater than 30 years, not free")
        GREATER_THAN_30_YEARS_FREE = _("Greater than 30 years, free")
        GREATER_THAN_30_YEARS_PLOT_DEPARTMENT_NOTIFICATION = _("Greater than 30 years, plot department notification")
        READY_NO_STATISTICS = _("Ready, no statistics")


# Taloyhtiö
class HousingCompany(ExternalHitasModel):
    # Official spelling of the housing company name
    official_name = models.CharField(max_length=1024)
    # More human-friendly housing company name
    display_name = models.CharField(max_length=1024)

    state = EnumIntegerField(HousingCompanyState, default=HousingCompanyState.NOT_READY)
    # Business ID / 'y-tunnus'
    business_id = models.CharField(max_length=9, validators=[validate_business_id], help_text=_("Format: 1234567-8"))

    street_address = models.CharField(max_length=1024)
    postal_code = models.ForeignKey(PostalCode, on_delete=models.PROTECT)

    building_type = models.ForeignKey(BuildingType, on_delete=models.PROTECT)
    financing_method = models.ForeignKey(FinancingMethod, on_delete=models.PROTECT)
    property_manager = models.ForeignKey(PropertyManager, on_delete=models.PROTECT)
    developer = models.ForeignKey(Developer, on_delete=models.PROTECT)

    # 'hankinta-arvo'
    acquisition_price = models.DecimalField(max_digits=15, decimal_places=2)
    # 'toteutunut hankinta-arvo'
    realized_acquisition_price = models.DecimalField(null=True, blank=True, max_digits=15, decimal_places=2)
    # 'ensisijaislaina'
    primary_loan = models.DecimalField(max_digits=15, decimal_places=2)
    # 'Myyntihintaluettelon vahvistamispäivä'
    sales_price_catalogue_confirmation_date = models.DateField(null=True, blank=True)
    # 'ilmoituspäivä'
    notification_date = models.DateField(null=True, blank=True)

    legacy_id = models.CharField(max_length=10, blank=True)
    notes = models.TextField(blank=True)
    last_modified_datetime = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True)

    @property
    def city(self):
        return hitas_city(self.postal_code.value)

    @property
    def area(self):
        return hitas_cost_area(self.postal_code.value)

    @property
    def area_display(self):
        pc = self.postal_code
        return f"{hitas_city(pc.value)}-{hitas_cost_area(pc.value)}: {pc.description}"

    def save(self, *args, **kwargs):
        current_user = get_current_user()
        if current_user is not None:
            self.last_modified_by = current_user
        super(HousingCompany, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Housing company")
        verbose_name_plural = _("Housing companies")
        ordering = ["id"]

        constraints = [
            models.CheckConstraint(name="acquisition_price_positive", check=models.Q(acquisition_price__gte=0)),
            models.CheckConstraint(
                name="realized_acquisition_price_positive", check=models.Q(realized_acquisition_price__gte=0)
            ),
        ]

    def __str__(self):
        return self.display_name


# Kiinteistö
class RealEstate(ExternalHitasModel):
    housing_company = models.ForeignKey(HousingCompany, on_delete=models.PROTECT, related_name="real_estates")

    # 'kiinteistötunnus'
    property_identifier = models.CharField(
        max_length=19, validators=[validate_property_id], help_text=_("Format: 1234-1234-1234-1234")
    )

    street_address = models.CharField(max_length=1024)
    postal_code = models.ForeignKey(PostalCode, on_delete=models.PROTECT)

    @property
    def city(self):
        return hitas_city(self.postal_code.value)

    class Meta:
        verbose_name = _("Real estate")
        verbose_name_plural = _("Real estates")

    def __str__(self):
        return self.property_identifier


# Rakennus
class Building(ExternalHitasModel):
    real_estate = models.ForeignKey(RealEstate, on_delete=models.PROTECT, related_name="buildings")
    completion_date = models.DateField(null=True)

    street_address = models.CharField(max_length=1024)
    postal_code = models.ForeignKey(PostalCode, on_delete=models.PROTECT)

    # 'rakennustunnus'
    building_identifier = models.CharField(
        blank=True,
        max_length=25,
        validators=[validate_building_id],
        help_text=_("Format: 100012345A or 91-17-16-1 S 001"),
    )

    @property
    def city(self):
        return hitas_city(self.postal_code.value)

    class Meta:
        verbose_name = _("Building")
        verbose_name_plural = _("Buildings")

    def __str__(self):
        return self.building_identifier
