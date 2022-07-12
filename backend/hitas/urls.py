from django.urls import include, path
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from hitas import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"housing-companies", views.HousingCompanyViewSet, basename="housing-company")

# Nested routers
# /api/v1/housing-companies/{housing_company_id}/real-estates
real_estate_router = NestedSimpleRouter(router, r"housing-companies", lookup="housing_company")
real_estate_router.register(r"real-estates", views.RealEstateViewSet, basename="real-estate")

# /api/v1/housing-companies/{housing_company_id}/real-estates/{real_estate_id}/buildings
building_router = NestedSimpleRouter(real_estate_router, r"real-estates", lookup="real_estate")
building_router.register(r"buildings", views.BuildingViewSet, basename="building")

app_name = "hitas"
urlpatterns = [
    path("", include(router.urls)),
    path("", include(real_estate_router.urls)),
    path("", include(building_router.urls)),
]
