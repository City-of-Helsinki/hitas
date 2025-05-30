from hitas.views.apartment import ApartmentViewSet
from hitas.views.apartment_list import ApartmentListViewSet
from hitas.views.apartment_max_price import ApartmentMaximumPriceViewSet
from hitas.views.apartment_sale import ApartmentSaleViewSet
from hitas.views.building import BuildingViewSet
from hitas.views.codes import ApartmentTypeViewSet, BuildingTypeViewSet, DeveloperViewSet
from hitas.views.condition_of_sale import ConditionOfSaleViewSet
from hitas.views.document import ApartmentDocumentViewSet, HousingCompanyDocumentViewSet
from hitas.views.email import (
    ConfirmedMaxPriceCalculationEmailViewSet,
    RegulationLetterEmailViewSet,
    UnconfirmedMaxPriceCalculationEmailViewSet,
)
from hitas.views.email_template import EmailTemplateViewSet
from hitas.views.external_sales_data import ExternalSalesDataView
from hitas.views.housing_company import HitasTypeViewSet, HousingCompanyViewSet, RegulationStatusViewSet
from hitas.views.indices import (
    ConstructionPriceIndex2005Equal100ViewSet,
    ConstructionPriceIndexViewSet,
    MarketPriceIndex2005Equal100ViewSet,
    MarketPriceIndexViewSet,
    MaximumPriceIndexViewSet,
    SurfaceAreaPriceCeilingCalculationDataViewSet,
    SurfaceAreaPriceCeilingViewSet,
)
from hitas.views.job_performance import JobPerformanceView
from hitas.views.owner import DeObfuscatedOwnerView, OwnerViewSet
from hitas.views.pdf_body import PDFBodyViewSet
from hitas.views.postal_code import HitasPostalCodeViewSet
from hitas.views.property_manager import PropertyManagerViewSet
from hitas.views.real_estate import RealEstateViewSet
from hitas.views.reports import (
    HalfHitasHousingCompaniesReportView,
    HousingCompanyStatesJSONReportView,
    HousingCompanyStatesReportView,
    MultipleOwnershipsReportView,
    OwnershipsByCompanyJSONReportView,
    OwnershipsByHousingCompanyReport,
    PropertyManagersReportView,
    RegulatedHousingCompaniesReportView,
    RegulatedOwnershipsReportView,
    SalesAndMaximumPricesReportView,
    SalesByPostalCodeAndAreaReportView,
    SalesReportView,
    UnregulatedHousingCompaniesReportView,
)
from hitas.views.sales_catalog import SalesCatalogCreateView, SalesCatalogValidateView
from hitas.views.thirty_year_regulation import ThirtyYearRegulationPostalCodesView, ThirtyYearRegulationView
