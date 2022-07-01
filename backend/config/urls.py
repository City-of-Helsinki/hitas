from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from hitas.views.housing_company import HousingCompanyViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"housing-companies", HousingCompanyViewSet, basename="housing-company")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((router.urls, "hitas"))),
]

handler404 = "hitas.error_handlers.handle_404"
handler500 = "hitas.error_handlers.handle_500"
