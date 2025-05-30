from django.urls import include, path
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from hitas import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"housing-companies", views.HousingCompanyViewSet, basename="housing-company")
router.register(r"property-managers", views.PropertyManagerViewSet, basename="property-manager")
router.register(r"apartments", views.ApartmentListViewSet, basename="apartment")
router.register(r"owners", views.OwnerViewSet, basename="owner")
router.register(r"owners/deobfuscated", views.DeObfuscatedOwnerView, basename="owner-deobfuscated")
router.register(r"conditions-of-sale", views.ConditionOfSaleViewSet, basename="conditions-of-sale")
router.register(r"thirty-year-regulation", views.ThirtyYearRegulationView, basename="thirty-year-regulation")
router.register(
    r"thirty-year-regulation/postal-codes",
    views.ThirtyYearRegulationPostalCodesView,
    basename="thirty-year-regulation-postal-codes",
)
router.register(r"indices/maximum-price-index", views.MaximumPriceIndexViewSet, basename="maximum-price-index")
router.register(r"indices/market-price-index", views.MarketPriceIndexViewSet, basename="market-price-index")
router.register(
    r"indices/market-price-index-2005-equal-100",
    views.MarketPriceIndex2005Equal100ViewSet,
    basename="market-price-index-2005-equal-100",
)
router.register(
    r"indices/construction-price-index",
    views.ConstructionPriceIndexViewSet,
    basename="construction-price-index",
)
router.register(
    r"indices/construction-price-index-2005-equal-100",
    views.ConstructionPriceIndex2005Equal100ViewSet,
    basename="construction-price-index-2005-equal-100",
)
router.register(
    r"indices/surface-area-price-ceiling",
    views.SurfaceAreaPriceCeilingViewSet,
    basename="surface-area-price-ceiling",
)
router.register(
    r"indices/surface-area-price-ceiling-calculation-data",
    views.SurfaceAreaPriceCeilingCalculationDataViewSet,
    basename="surface-area-price-ceiling-calculation-data",
)
router.register(
    r"external-sales-data",
    views.ExternalSalesDataView,
    basename="external-sales-data",
)
router.register(
    r"email-templates/(?P<type>\w+)",
    views.EmailTemplateViewSet,
    basename="email-template",
)
router.register(
    r"pdf-bodies",
    views.PDFBodyViewSet,
    basename="pdf-body",
)
router.register(
    r"email/send-confirmed-max-price-calculation-pdf",
    views.ConfirmedMaxPriceCalculationEmailViewSet,
    basename="confirmed-max-price-calculation-email",
)
router.register(
    r"email/send-unconfirmed-max-price-calculation-pdf",
    views.UnconfirmedMaxPriceCalculationEmailViewSet,
    basename="unconfirmed-max-price-calculation-email",
)
router.register(
    r"email/send-regulation-letter",
    views.RegulationLetterEmailViewSet,
    basename="regulation-letter-email",
)

# /api/v1/reports/download-sales-report
router.register(r"reports/download-sales-report", views.SalesReportView, basename="sales-report")

# /api/v1/reports/download-sales-and-maximum-prices-report
router.register(
    r"reports/download-sales-and-maximum-prices-report",
    views.SalesAndMaximumPricesReportView,
    basename="sales-and-maximum-prices-report",
)

# /api/v1/reports/download-regulated-housing-companies-report
router.register(
    r"reports/download-regulated-housing-companies-report",
    views.RegulatedHousingCompaniesReportView,
    basename="regulated-housing-companies-report",
)

# /api/v1/reports/download-half-hitas-housing-companies-report
router.register(
    r"reports/download-half-hitas-housing-companies-report",
    views.HalfHitasHousingCompaniesReportView,
    basename="half-hitas-housing-companies-report",
)

# /api/v1/reports/download-unregulated-housing-companies-report
router.register(
    r"reports/download-unregulated-housing-companies-report",
    views.UnregulatedHousingCompaniesReportView,
    basename="unregulated-housing-companies-report",
)

# /api/v1/reports/download-property-managers-report
router.register(
    r"reports/download-property-managers-report",
    views.PropertyManagersReportView,
    basename="property-managers-report",
)

# /api/v1/reports/housing-company-states
router.register(
    r"reports/housing-company-states",
    views.HousingCompanyStatesJSONReportView,
    basename="housing-company-states",
)

# /api/v1/reports/download-housing-company-states-report
router.register(
    r"reports/download-housing-company-states-report",
    views.HousingCompanyStatesReportView,
    basename="housing-company-states-report",
)

# /api/v1/reports/download-sales-by-postal-code-and-area-report
router.register(
    r"reports/download-sales-by-postal-code-and-area-report",
    views.SalesByPostalCodeAndAreaReportView,
    basename="sales-by-postal-code-and-area-report",
)

# /api/v1/reports/download-regulated-ownerships-report
router.register(
    r"reports/download-regulated-ownerships-report",
    views.RegulatedOwnershipsReportView,
    basename="regulated-ownerships-report",
)

# /api/v1/reports/download-multiple-ownerships-report
router.register(
    r"reports/download-multiple-ownerships-report",
    views.MultipleOwnershipsReportView,
    basename="multiple-ownerships-report",
)

# /api/v1/reports/ownership-by-housing-company/<pk>
router.register(
    r"reports/ownership-by-housing-company-report",
    views.OwnershipsByCompanyJSONReportView,
    basename="ownership-by-housing-company-report",
)

# /api/v1/reports/download-ownership-by-housing-company/<pk>
router.register(
    r"reports/download-ownership-by-housing-company-report",
    views.OwnershipsByHousingCompanyReport,
    basename="download-ownership-by-housing-company-report",
)


# /api/v1/job-performance/{source}
router.register(
    r"job-performance",
    views.JobPerformanceView,
    basename="job-performance",
)

# Codes
router.register(r"postal-codes", views.HitasPostalCodeViewSet, basename="postal-code")
router.register(r"building-types", views.BuildingTypeViewSet, basename="building-type")
router.register(r"developers", views.DeveloperViewSet, basename="developer")
router.register(r"apartment-types", views.ApartmentTypeViewSet, basename="apartment-type")
router.register(r"hitas-types", views.HitasTypeViewSet, basename="hitas-type")
router.register(r"regulation-statuses", views.RegulationStatusViewSet, basename="regulation-status")

# Nested routers
housing_company_router = NestedSimpleRouter(router, r"housing-companies", lookup="housing_company")

# /api/v1/housing-companies/{housing_company_id}/real-estates
housing_company_router.register(r"real-estates", views.RealEstateViewSet, basename="real-estate")

# /api/v1/housing-companies/{housing_company_id}/apartments
housing_company_router.register(r"apartments", views.ApartmentViewSet, basename="apartment")

# /api/v1/housing-companies/{housing_company_id}/documents
housing_company_router.register(r"documents", views.HousingCompanyDocumentViewSet, basename="document")

# /api/v1/housing-companies/{housing_company_id}/sales-catalog-validate
housing_company_router.register(
    r"sales-catalog-validate", views.SalesCatalogValidateView, basename="sales-catalog-validate"
)

# /api/v1/housing-companies/{housing_company_id}/sales-catalog-create
housing_company_router.register(r"sales-catalog-create", views.SalesCatalogCreateView, basename="sales-catalog-create")

real_estate_router = NestedSimpleRouter(housing_company_router, r"real-estates", lookup="real_estate")
apartment_router = NestedSimpleRouter(housing_company_router, r"apartments", lookup="apartment")

# /api/v1/housing-companies/{housing_company_id}/real-estates/{real_estate_id}/buildings
real_estate_router.register(r"buildings", views.BuildingViewSet, basename="building")

# /api/v1/housing-companies/{housing_company_id}/apartments/{apartment_id}/maximum-price
apartment_router.register(r"maximum-prices", views.ApartmentMaximumPriceViewSet, basename="maximum-price")

# /api/v1/housing-companies/{housing_company_id}/apartments/{apartment_id}/sales
apartment_router.register(r"sales", views.ApartmentSaleViewSet, basename="apartment-sale")

# /api/v1/housing-companies/{housing_company_id}/apartments/{apartment_id}/documents
apartment_router.register(r"documents", views.ApartmentDocumentViewSet, basename="document")

app_name = "hitas"
urlpatterns = [
    path("", include(router.urls)),
    path("", include(housing_company_router.urls)),
    path("", include(real_estate_router.urls)),
    path("", include(apartment_router.urls)),
]
