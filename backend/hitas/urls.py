from django.urls import include, path
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from hitas import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"housing-companies", views.HousingCompanyViewSet, basename="housing-company")
router.register(r"property-managers", views.PropertyManagerViewSet, basename="property-manager")
router.register(r"apartments", views.ApartmentListViewSet, basename="apartment")
router.register(r"persons", views.PersonViewSet, basename="person")

# Codes
router.register(r"postal-codes", views.HitasPostalCodeViewSet, basename="postal-code")
router.register(r"financing-methods", views.FinancingMethodViewSet, basename="financing-method")
router.register(r"building-types", views.BuildingTypeViewSet, basename="building-type")
router.register(r"developers", views.DeveloperViewSet, basename="developer")
router.register(r"apartment-types", views.ApartmentTypeViewSet, basename="apartment-type")

# Nested routers
# /api/v1/housing-companies/{housing_company_id}/real-estates
housing_company_router = NestedSimpleRouter(router, r"housing-companies", lookup="housing_company")
housing_company_router.register(r"real-estates", views.RealEstateViewSet, basename="real-estate")

# /api/v1/housing-companies/{housing_company_id}/real-estates/{real_estate_id}/buildings
real_estate_router = NestedSimpleRouter(housing_company_router, r"real-estates", lookup="real_estate")
real_estate_router.register(r"buildings", views.BuildingViewSet, basename="building")

# /api/v1/housing-companies/{housing_company_id}/apartments
housing_company_router.register(r"apartments", views.ApartmentViewSet, basename="apartment")

app_name = "hitas"
urlpatterns = [
    path("", include(router.urls)),
    path("", include(housing_company_router.urls)),
    path("", include(real_estate_router.urls)),
]
