from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from hitas.views.housing_company import HousingCompanyView

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"housing-companies", HousingCompanyView, basename="housing-company")
urlpatterns = router.urls

urlpatterns = [path("admin/", admin.site.urls), path("api/v1/", include((router.urls, "hitas")))]
