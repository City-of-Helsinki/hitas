import helusers.views
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve

from hitas.views.health import HealthCheckView
from users.views import UserInfoView


class HitasLogoutView(helusers.views.LogoutView):
    success_url_allowed_hosts = settings.SOCIAL_AUTH_TUNNISTAMO_ALLOWED_REDIRECT_HOSTS


class HitasLogoutCompleteView(helusers.views.LogoutCompleteView):
    success_url_allowed_hosts = settings.SOCIAL_AUTH_TUNNISTAMO_ALLOWED_REDIRECT_HOSTS


helusers_pattern = (
    [
        path("login/", helusers.views.LoginView.as_view(), name="auth_login"),
        path("logout/", HitasLogoutView.as_view(), name="auth_logout"),
        path("logout/complete/", HitasLogoutCompleteView.as_view(), name="auth_logout_complete"),
        path(
            "logout/oidc/backchannel/",
            csrf_exempt(helusers.views.OIDCBackChannelLogout.as_view()),
            name="oidc_backchannel",
        ),
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
    # Static files can be served using django's built in static file server
    # since they are only used to serve admin panel assets.
    path(f"{settings.STATIC_URL.lstrip('/').rstrip('/')}/<path:path>", serve, {"document_root": settings.STATIC_ROOT}),
]

if settings.DEBUG:
    urlpatterns += [
        path(
            f"{settings.MEDIA_URL.lstrip('/').rstrip('/')}/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}
        ),
    ]

if settings.DEBUG_TOOLBAR:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
        path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    ]

handler404 = "hitas.error_handlers.handle_404"
handler500 = "hitas.error_handlers.handle_500"
