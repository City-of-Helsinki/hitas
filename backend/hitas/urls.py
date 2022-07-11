from django.urls import include, path
from rest_framework import routers

from hitas import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"housing-companies", views.HousingCompanyViewSet, basename="housing-company")

app_name = "hitas"
urlpatterns = [
    path("", include(router.urls)),
]
