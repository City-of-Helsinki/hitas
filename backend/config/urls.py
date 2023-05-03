from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from helusers import views

from hitas.views.health import HealthCheckView
from users.views import UserInfoView


class HitasLogoutView(views.LogoutView):
    success_url_allowed_hosts = settings.SOCIAL_AUTH_TUNNISTAMO_ALLOWED_REDIRECT_HOSTS


class HitasLogoutCompleteView(views.LogoutCompleteView):
    success_url_allowed_hosts = settings.SOCIAL_AUTH_TUNNISTAMO_ALLOWED_REDIRECT_HOSTS


helusers_pattern = (
    [
        path("login/", views.LoginView.as_view(), name="auth_login"),
        path("logout/", HitasLogoutView.as_view(), name="auth_logout"),
        path("logout/complete/", HitasLogoutCompleteView.as_view(), name="auth_logout_complete"),
    ],
    "helusers",
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("hitas.urls")),
    path("healthz", HealthCheckView.as_view(), name="health_check"),
    path("pysocial/", include("social_django.urls", namespace="social")),
    path("helauth/", include(helusers_pattern)),
    path("helauth/userinfo/", UserInfoView.as_view(), name="userinfo"),
]

if settings.DEBUG_TOOLBAR:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
        path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    ]

handler404 = "hitas.error_handlers.handle_404"
handler500 = "hitas.error_handlers.handle_500"
