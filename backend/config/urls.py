from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from hitas.views.health import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("hitas.urls")),
    path("healthz", HealthCheckView.as_view(), name="health_check"),
]

if settings.DEBUG_TOOLBAR:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
        path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    ]

handler404 = "hitas.error_handlers.handle_404"
handler500 = "hitas.error_handlers.handle_500"
