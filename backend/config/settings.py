import os
import re

import environ
from dateutil.relativedelta import relativedelta
from django.utils.log import DEFAULT_LOGGING
from django.utils.translation import gettext_lazy as _
from helusers import defaults
from rest_framework.authentication import TokenAuthentication

# ----- ENV Setup --------------------------------------------------------------------------------------

root = environ.Path(__file__) - 2
assert os.path.exists(root("manage.py"))
var_root = root("var")

BASE_DIR = root()


def relativedelta_months(value: int) -> relativedelta:
    return relativedelta(months=value)


env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, None),
    ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(str, "postgres:///hitas"),
    VAR_ROOT=(str, var_root),
    STATIC_URL=(str, "/static/"),
    MEDIA_URL=(str, "/media/"),
    CORS_ALLOWED_ORIGINS=(list, []),
    UWSGI_WARMUP=(bool, True),
    DJANGO_LOG_LEVEL=(str, "INFO"),
    SENTRY_DSN=(str, None),
    SENTRY_ENVIRONMENT=(str, "unknown"),
    SENTRY_SAMPLE_RATE=(float, 1.0),
    SENTRY_TRACES_SAMPLE_RATE=(float, 0.1),
    SHOW_FULFILLED_CONDITIONS_OF_SALE_FOR_MONTHS=(relativedelta_months, relativedelta(months=2)),
    OIDC_API_AUDIENCE=(str, ""),
    OIDC_API_AUTHORIZATION_FIELD=(str, ""),
    OIDC_API_ISSUER=(str, ""),
    OIDC_API_REQUIRE_SCOPE_FOR_AUTHENTICATION=(bool, False),
    OIDC_API_SCOPE_PREFIX=(str, None),
    SOCIAL_AUTH_TUNNISTAMO_KEY=(str, ""),
    SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT=(str, ""),
    SOCIAL_AUTH_TUNNISTAMO_SECRET=(str, ""),
    SOCIAL_AUTH_TUNNISTAMO_ALLOWED_REDIRECT_HOSTS=(list, ["localhost:3000"]),
    ALLOWED_AD_GROUPS=(list, []),
)
env.read_env(os.path.join(BASE_DIR, ".env"))


# ----- Basic settings  --------------------------------------------------------------------------------

DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
var_root = env.path("VAR_ROOT")
STATIC_ROOT = var_root("static")
MEDIA_ROOT = var_root("media")
STATIC_URL = env("STATIC_URL")
MEDIA_URL = env("MEDIA_URL")
UWSGI_WARMUP = env("UWSGI_WARMUP")

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
TEST_RUNNER = "hitas.tests.runner.HitasDatabaseRunner"

# How long to show fulfilled (=deleted) conditions of sale from the endpoints
SHOW_FULFILLED_CONDITIONS_OF_SALE_FOR_MONTHS: relativedelta = env("SHOW_FULFILLED_CONDITIONS_OF_SALE_FOR_MONTHS")

# ----- CORS and CSRF settings -------------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_EXPOSE_HEADERS = ["Content-Disposition"]
CORS_ALLOW_CREDENTIALS = True

# In Django 3.2, this should not include schema.
# This was changed in django 4.0+ so that schema is mandatory,
# so this should be changed when updating to django 4.0+.
# https://docs.djangoproject.com/en/dev/releases/4.0/#format-change
CSRF_TRUSTED_ORIGINS = [re.sub(r"^https?://", "", host) for host in CORS_ALLOWED_ORIGINS]
if CSRF_TRUSTED_ORIGINS:
    # Allow 'csrftoken' cookie to be read/used by all subdomains, e.g. the frontend
    CSRF_COOKIE_DOMAIN = "." + ".".join(CSRF_TRUSTED_ORIGINS[0].split(".")[1:])

# ----- Installed apps ---------------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_jinja",
    "helusers.apps.HelusersConfig",
    "helusers.apps.HelusersAdminConfig",
    "social_django",
    "auditlog",
    "users",
    "hitas",
    "nested_inline",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "health_check",
    "corsheaders",
    "safedelete",
]

# ----- Middleware -------------------------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "crum.CurrentRequestUserMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
]

# ----- Database ---------------------------------------------------------------------------------------

DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ----- Templates --------------------------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "DIRS": [],
        "APP_DIRS": True,
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ----- Logging ----------------------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": DEFAULT_LOGGING["filters"],
    "formatters": DEFAULT_LOGGING["formatters"],
    "handlers": DEFAULT_LOGGING["handlers"]
    | {
        "default": {
            "class": "logging.StreamHandler",
        }
    },
    "loggers": DEFAULT_LOGGING["loggers"],
    "root": {
        "handlers": ["default"],
        "level": env("DJANGO_LOG_LEVEL"),
    },
}

if env("SENTRY_DSN"):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    from .utils import get_current_version

    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),
        release=get_current_version(),
        environment=env("SENTRY_ENVIRONMENT"),
        integrations=[DjangoIntegration()],
        sample_rate=env("SENTRY_SAMPLE_RATE"),
        traces_sample_rate=env("SENTRY_TRACES_SAMPLE_RATE"),
    )

# ----- Internationalization ---------------------------------------------------------------------------

LANGUAGE_CODE = "fi"
LANGUAGES = [
    ("fi", _("Finnish")),
    ("en", _("English")),
]
LOCALE_PATHS = ["./templates/locale"]
TIME_ZONE = "Europe/Helsinki"
USE_I18N = False
USE_L10N = True
USE_TZ = True

# ----- Django Rest Framework --------------------------------------------------------------------------

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "hitas.exceptions.exception_handler",
    "COERCE_DECIMAL_TO_STRING": False,
    "DEFAULT_FILTER_BACKENDS": ["hitas.views.utils.HitasFilterBackend"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "config.settings.BearerAuthentication",  # DEV-tokens
        "rest_framework.authentication.SessionAuthentication",  # Helsinki profile sessions
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "users.permissions.IsAdminOrHasRequiredADGroups",
    ],
    "DEFAULT_RENDERER_CLASSES": ["hitas.types.HitasJSONRenderer"],
}

if DEBUG:
    # Enable browsable API renderer
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].append("rest_framework.renderers.BrowsableAPIRenderer")

# ----- Authentication settings ------------------------------------------------------------------------

OIDC_API_TOKEN_AUTH = {
    "AUDIENCE": env("OIDC_API_AUDIENCE"),
    "ISSUER": env.url("OIDC_API_ISSUER"),
    "API_AUTHORIZATION_FIELD": env("OIDC_API_AUTHORIZATION_FIELD"),
    "REQUIRE_API_SCOPE_FOR_AUTHENTICATION": env("OIDC_API_REQUIRE_SCOPE_FOR_AUTHENTICATION"),
    "API_SCOPE_PREFIX": env("OIDC_API_SCOPE_PREFIX"),
}

SOCIAL_AUTH_TUNNISTAMO_KEY = env("SOCIAL_AUTH_TUNNISTAMO_KEY")
SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT = env("SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT")
SOCIAL_AUTH_TUNNISTAMO_SECRET = env("SOCIAL_AUTH_TUNNISTAMO_SECRET")
SOCIAL_AUTH_TUNNISTAMO_SCOPE = ["ad_groups"]
SOCIAL_AUTH_TUNNISTAMO_AUTH_EXTRA_ARGUMENTS = {"ui_locales": "fi"}
SOCIAL_AUTH_TUNNISTAMO_ALLOWED_REDIRECT_HOSTS = env("SOCIAL_AUTH_TUNNISTAMO_ALLOWED_REDIRECT_HOSTS")
SOCIAL_AUTH_TUNNISTAMO_PIPELINE = defaults.SOCIAL_AUTH_PIPELINE

HELUSERS_PASSWORD_LOGIN_DISABLED = False
HELUSERS_BACK_CHANNEL_LOGOUT_ENABLED = False

# One of these AD groups is required for API access
ALLOWED_AD_GROUPS: list[str] = env("ALLOWED_AD_GROUPS")

AUTHENTICATION_BACKENDS = [
    "helusers.tunnistamo_oidc.TunnistamoOIDCAuth",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/admin/login/"

SESSION_SERIALIZER = "django.contrib.sessions.serializers.PickleSerializer"


class BearerAuthentication(TokenAuthentication):
    keyword = "Bearer"


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ----- Debug toolbar ----------------------------------------------------------------------------------

DEBUG_TOOLBAR = False
if DEBUG:
    try:
        import debug_toolbar  # noqa

        DEBUG_TOOLBAR = True
    except ImportError:
        pass

    if DEBUG_TOOLBAR:
        INSTALLED_APPS.append("debug_toolbar")
        MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

        import socket

        hostname, aliases, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

# ------------------------------------------------------------------------------------------------------
