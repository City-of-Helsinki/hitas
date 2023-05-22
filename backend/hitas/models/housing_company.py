import datetime
from decimal import Decimal
from types import DynamicClassAttribute
from typing import Optional

from auditlog.registry import auditlog
from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumField
from safedelete.models import SOFT_DELETE_CASCADE

from hitas.models._base import (
    ExternalSafeDeleteHitasModel,
    HitasImprovement,
    HitasMarketPriceImprovement,
    HitasModelDecimalField,
)
from hitas.models.utils import validate_business_id


class HitasType(Enum):
    # Vanhat säännöt, Ei sisällytetä tilastoihin
    NON_HITAS = "non_hitas"
    # Vanhat säännöt
    HITAS_I = "hitas_1"
    # Vanhat säännöt
    HITAS_II = "hitas_2"
    # Vanhat säännöt, Ei hyväksytä rakennusaikaista korkoa
    HITAS_I_NO_INTEREST = "hitas_1_no_interest"
    # Vanhat säännöt, Ei hyväksytä rakennusaikaista korkoa
    HITAS_II_NO_INTEREST = "hitas_2_no_interest"
    # Uudet säännöt, (Ei ole rakennusaikaista korkoa)
    NEW_HITAS_I = "new_hitas_1"
    # Uudet säännöt, (Ei ole rakennusaikaista korkoa)
    NEW_HITAS_II = "new_hitas_2"
    # Puoli-Hitas, Ei sisällytetä tilastoihin
    HALF_HITAS = "half_hitas"
    # Vanhat säännöt, Ei hyväksytä rakennusaikaista korkoa, Ei sisällytetä tilastoihin
    RENTAL_HITAS_I = "rental_hitas_1"
    # Vanhat säännöt, Ei hyväksytä rakennusaikaista korkoa, Ei sisällytetä tilastoihin
    RENTAL_HITAS_II = "rental_hitas_2"

    class Labels:
        NON_HITAS = _("Ei Hitas")
        HITAS_I = _("Hitas I")
        HITAS_II = _("Hitas II")
        HITAS_I_NO_INTEREST = _("Hitas I, Ei korkoja")
        HITAS_II_NO_INTEREST = _("Hitas II, Ei korkoja")
        NEW_HITAS_I = _("Uusi Hitas I")
        NEW_HITAS_II = _("Uusi Hitas II")
        HALF_HITAS = _("Puolihitas")
        RENTAL_HITAS_I = _("Vuokratalo Hitas I")
        RENTAL_HITAS_II = _("Vuokratalo Hitas II")

    @DynamicClassAttribute
    def new_hitas_ruleset(self) -> bool:
        return self in HitasType.with_new_hitas_ruleset()

    @DynamicClassAttribute
    def old_hitas_ruleset(self) -> bool:
        return self not in HitasType.with_new_hitas_ruleset()

    @DynamicClassAttribute
    def exclude_from_statistics(self) -> bool:
        return self in HitasType.with_exclude_from_statistics()

    @DynamicClassAttribute
    def include_in_statistics(self) -> bool:
        return self not in HitasType.with_exclude_from_statistics()

    @DynamicClassAttribute
    def no_interest(self) -> bool:
        return self in HitasType.with_no_interest()

    @classmethod
    def with_new_hitas_ruleset(cls) -> list["HitasType"]:
        return [  # type: ignore
            cls.NEW_HITAS_I,
            cls.NEW_HITAS_II,
        ]

    @classmethod
    def with_exclude_from_statistics(cls) -> list["HitasType"]:
        return [  # type: ignore
            cls.NON_HITAS,
            cls.HALF_HITAS,
            cls.RENTAL_HITAS_I,
            cls.RENTAL_HITAS_II,
        ]

    @classmethod
    def with_no_interest(cls) -> list["HitasType"]:
        return [  # type: ignore
            cls.HITAS_I_NO_INTEREST,
            cls.HITAS_II_NO_INTEREST,
            cls.RENTAL_HITAS_I,
            cls.RENTAL_HITAS_II,
        ]


class RegulationStatus(Enum):
    REGULATED = "regulated"
    RELEASED_BY_HITAS = "released_by_hitas"
    RELEASED_BY_PLOT_DEPARTMENT = "released_by_plot_department"

    class Labels:
        REGULATED = _("Regulated")
        RELEASED_BY_HITAS = _("Released by Hitas")
        RELEASED_BY_PLOT_DEPARTMENT = _("Released by Plot Department")


# Taloyhtiö / "Osakeyhtiö"
class HousingCompany(ExternalSafeDeleteHitasModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    # Official spelling of the housing company name
    official_name: str = models.CharField(max_length=1024, unique=True)
    # More human-friendly housing company name
    display_name: str = models.CharField(max_length=1024, unique=True)

    # 'Yhtiö tunnus'
    business_id: Optional[str] = models.CharField(
        max_length=9,
        null=True,
        validators=[validate_business_id],
        help_text=_("Format: 1234567-1"),
    )

    # 'Osoite'
    street_address: str = models.CharField(max_length=1024)
    # 'Postikoodi'
    postal_code = models.ForeignKey("HitasPostalCode", on_delete=models.PROTECT, related_name="housing_companies")
    # 'Talotyyppi'
    building_type = models.ForeignKey("BuildingType", on_delete=models.PROTECT, related_name="housing_companies")

    # 'Hitas-tyyppi'
    hitas_type: HitasType = EnumField(HitasType, max_length=20)
    # 'Sääntelyn tila'
    regulation_status: RegulationStatus = EnumField(RegulationStatus, default=RegulationStatus.REGULATED, max_length=27)

    # 'Rakennuttaja'
    developer = models.ForeignKey(
        "Developer",
        on_delete=models.PROTECT,
        related_name="housing_companies",
    )
    # 'Isännöitsijä'
    property_manager = models.ForeignKey(
        "PropertyManager",
        on_delete=models.PROTECT,
        related_name="housing_companies",
        null=True,
    )
    # 'Tilastoidaanko' / "Näkyvätkö yhtiön asuntojen kaupat tilastoissa?"
    exclude_from_statistics: bool = models.BooleanField(default=False)

    # 'Hankinta-arvo'
    acquisition_price: Decimal = HitasModelDecimalField()
    # 'Ensisijaislaina'
    primary_loan: Optional[Decimal] = HitasModelDecimalField(null=True, blank=True)

    # 'Muistiinpanot'
    notes: str = models.TextField(blank=True)

    # 'Myyntihintaluettelon vahvistamispäivä (migraatiosta saatu tieto)'
    sales_price_catalogue_confirmation_date: Optional[datetime.date] = models.DateField(null=True, blank=True)
    # 'Sääntelystä vapautumispäivä (migraatiosta saatu tieto)'
    legacy_release_date: Optional[datetime.date] = models.DateField(null=True, blank=True)

    # TODO: To be removed
    # [DEPREKOITU] 'Rahoistustyypppi'
    financing_method = models.ForeignKey("FinancingMethod", on_delete=models.PROTECT, related_name="housing_companies")

    @property
    def city(self) -> str:
        return self.postal_code.city

    @property
    def area(self) -> int:
        return self.postal_code.cost_area

    @property
    def area_display(self) -> str:
        return f"{self.city}-{self.area}: {self.postal_code.value}"

    @property
    def total_shares_count(self) -> int:
        from hitas.models import Apartment

        return (
            Apartment.objects.filter(building__real_estate__housing_company=self, share_number_start__isnull=False)
            .annotate(shares_count=F("share_number_end") - F("share_number_start") + 1)
            .aggregate(sum_shares_count=Sum("shares_count"))["sum_shares_count"]
        )

    @property
    def is_over_thirty_years_old(self) -> bool:
        from hitas.models import Apartment

        newest_apartment: Optional[Apartment] = (
            Apartment.objects.filter(building__real_estate__housing_company=self).order_by("-completion_date").first()
        )
        if not newest_apartment:
            return False
        if newest_apartment.completion_date is None:
            return False

        return relativedelta(timezone.now().date(), newest_apartment.completion_date).years >= 30

    @property
    def is_completed(self) -> bool:
        from hitas.models import Apartment

        newest_apartment: Optional[Apartment] = (
            Apartment.objects.filter(building__real_estate__housing_company=self).order_by("-completion_date").first()
        )
        if not newest_apartment:
            return False

        return bool(newest_apartment.completion_date)

    @property
    def release_date(self) -> Optional[datetime.date]:
        # Legacy release date overrides dynamic release date from regulation model
        _release_date: Optional[datetime.date] = self.legacy_release_date
        if _release_date:
            self._release_date = _release_date
            return self._release_date

        # Allow caches for the instance
        if hasattr(self, "_release_date"):
            return self._release_date

        from hitas.services.housing_company import get_regulation_release_date

        self._release_date = get_regulation_release_date(self.id)
        return self._release_date

    class Meta:
        verbose_name = _("Housing company")
        verbose_name_plural = _("Housing companies")
        ordering = ["id"]

        constraints = [
            models.CheckConstraint(name="acquisition_price_positive", check=models.Q(acquisition_price__gte=0)),
        ]

    def __str__(self):
        return self.display_name


class HousingCompanyWithAnnotations(HousingCompany):
    completion_date: datetime.date
    completion_month: datetime.date
    realized_acquisition_price: Optional[Decimal]
    surface_area: Optional[Decimal]
    avg_price_per_square_meter: Optional[Decimal]
    property_manager_last_edited: Optional[datetime.datetime]

    class Meta:
        abstract = True


class HousingCompanyMarketPriceImprovement(HitasMarketPriceImprovement):
    housing_company = models.ForeignKey(
        "HousingCompany",
        on_delete=models.CASCADE,
        related_name="market_price_improvements",
    )


class HousingCompanyConstructionPriceImprovement(HitasImprovement):
    housing_company = models.ForeignKey(
        "HousingCompany",
        on_delete=models.CASCADE,
        related_name="construction_price_improvements",
    )


auditlog.register(HousingCompany)
auditlog.register(HousingCompanyMarketPriceImprovement)
auditlog.register(HousingCompanyConstructionPriceImprovement)
