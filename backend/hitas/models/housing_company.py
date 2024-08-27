import datetime
from decimal import Decimal
from types import DynamicClassAttribute
from typing import Optional

from auditlog.models import LogEntry
from auditlog.registry import auditlog
from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import F, Sum
from django.db.models.functions import Cast
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
from hitas.utils import max_date_if_all_not_null


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
    # Puolihitas, Ei sisällytetä tilastoihin
    HALF_HITAS = "half_hitas"
    # Vanhat säännöt, Ei hyväksytä rakennusaikaista korkoa, Ei sisällytetä tilastoihin
    RENTAL_HITAS_I = "rental_hitas_1"
    # Vanhat säännöt, Ei hyväksytä rakennusaikaista korkoa, Ei sisällytetä tilastoihin
    RENTAL_HITAS_II = "rental_hitas_2"
    # Uudet säännöt. Ryhmärakentamiskohde, jälleenmyynti sallittu vaikka taloyhtiö ei ole vielä valmis
    RR_NEW_HITAS = "rr_new_hitas"

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
        RR_NEW_HITAS = _("RR Uusi Hitas")

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
            cls.RR_NEW_HITAS,
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
        return self.completion_date is not None

    @property
    def completion_date(self) -> datetime.date:
        # Allow caches for the instance
        if hasattr(self, "_completion_date"):
            return self._completion_date

        self._completion_date = (
            HousingCompany.objects.filter(id=self.id)
            .annotate(_completion_date=max_date_if_all_not_null("real_estates__buildings__apartments__completion_date"))
            .values_list("_completion_date", flat=True)
            .first()
        )
        return self._completion_date

    @property
    def release_date(self) -> Optional[datetime.date]:
        if self.regulation_status == RegulationStatus.REGULATED:
            return None

        # Legacy release date overrides dynamic release date from regulation model
        _release_date: Optional[datetime.date] = self.legacy_release_date
        if _release_date:
            self._release_date = _release_date
            return self._release_date

        # Allow caches for the instance
        if hasattr(self, "_release_date"):
            if self._release_date is not None:
                return self._release_date

        # Try to find the release date from 30 year regulation
        from hitas.services.housing_company import get_regulation_release_date

        regulation_release_date = get_regulation_release_date(self.id)
        if regulation_release_date:
            self._release_date = regulation_release_date
            return self._release_date

        # Housing company is released, but not in a regulation, so it was released manually. Get the date from logs.
        if self.regulation_status == RegulationStatus.RELEASED_BY_PLOT_DEPARTMENT:
            # Find the latest log entry that contains regulation status changes
            log_entry = (
                LogEntry.objects.get_for_object(self)
                .annotate(changes_as_json=Cast("changes", output_field=models.JSONField()))
                .filter(changes_as_json__regulation_status__isnull=False)
                .exclude(  # Ignore cases where regulation status was not actually changed
                    changes_as_json__regulation_status__0="Released by Plot Department",
                    changes_as_json__regulation_status__1="Released by Plot Department",
                )
                .order_by("-timestamp", "-id")
                .first()
            )
            if (
                log_entry is not None
                and log_entry.changes_as_json["regulation_status"][1] == "Released by Plot Department"
            ):
                self._release_date = log_entry.timestamp.date()
                return self._release_date

        # Release date was not found
        return None

    @property
    def property_manager_changed_at(self) -> Optional[datetime.datetime]:
        latest_logentry: LogEntry = (
            LogEntry.objects.get_for_object(self)
            .annotate(changes_as_json=Cast("changes", output_field=models.JSONField()))
            .filter(
                action__in=[LogEntry.Action.UPDATE, LogEntry.Action.CREATE],
                changes_as_json__property_manager__isnull=False,
            )
            # Ignore cases where property manager was not actually changed
            .exclude(changes_as_json__property_manager__0=F("changes_as_json__property_manager__1"))
            .order_by("-timestamp", "-id")
            .first()
        )
        if latest_logentry is not None:
            return latest_logentry.timestamp
        return None

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


class HousingCompanyWithRegulatedReportAnnotations(HousingCompany):
    completion_date: datetime.date
    surface_area: Optional[Decimal]
    realized_acquisition_price: Optional[Decimal]
    avg_price_per_square_meter: Optional[Decimal]
    apartment_count: int

    class Meta:
        abstract = True


class HousingCompanyWithUnregulatedReportAnnotations(HousingCompany):
    completion_date: datetime.date
    release_date: Optional[datetime.date]
    apartment_count: int

    class Meta:
        abstract = True


class HousingCompanyWithStateReportAnnotations(HousingCompany):
    completion_date: datetime.date
    apartment_count: int

    class Meta:
        abstract = True


class HousingCompanyMarketPriceImprovement(HitasMarketPriceImprovement):
    housing_company = models.ForeignKey(
        "HousingCompany",
        on_delete=models.CASCADE,
        related_name="market_price_improvements",
    )


# This is for typing only
class HousingCompanyMarketPriceImprovementWithIndex(HousingCompanyMarketPriceImprovement):
    completion_date_index: Decimal
    completion_date_index_2005eq100: Decimal

    class Meta:
        abstract = True


class HousingCompanyConstructionPriceImprovement(HitasImprovement):
    housing_company = models.ForeignKey(
        "HousingCompany",
        on_delete=models.CASCADE,
        related_name="construction_price_improvements",
    )


# This is for typing only
class HousingCompanyConstructionPriceImprovementWithIndex(HousingCompanyConstructionPriceImprovement):
    completion_date_index: Decimal
    completion_date_index_2005eq100: Decimal

    class Meta:
        abstract = True


auditlog.register(HousingCompany)
auditlog.register(HousingCompanyMarketPriceImprovement)
auditlog.register(HousingCompanyConstructionPriceImprovement)
