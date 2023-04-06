from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from hitas.views.health import HealthCheckView
from users.views import UserInfoView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("hitas.urls")),
    path("healthz", HealthCheckView.as_view(), name="health_check"),
    path("pysocial/", include("social_django.urls", namespace="social")),
    path("helauth/", include("helusers.urls")),
    path("helauth/userinfo/", UserInfoView.as_view(), name="userinfo"),
]

if settings.DEBUG_TOOLBAR:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
        path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    ]

handler404 = "hitas.error_handlers.handle_404"
handler500 = "hitas.error_handlers.handle_500"
