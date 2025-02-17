from pathlib import Path

import environ
import helusers.defaults
from dateutil.relativedelta import relativedelta
from django.utils.log import DEFAULT_LOGGING
from django.utils.translation import gettext_lazy
from rest_framework.authentication import TokenAuthentication

# ----- ENV Setup --------------------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent


def relativedelta_months(value: int) -> relativedelta:
    return relativedelta(months=value)


env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, None),
    ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(str, "postgres:///hitas"),
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
    HELUSERS_BACK_CHANNEL_LOGOUT_ENABLED=(bool, False),
    ALLOWED_AD_GROUPS=(list, []),
    DEFAULT_FROM_EMAIL=(str, "hitas@hel.fi"),
    EMAIL_HOST=(str, "smtp.gmail.com"),
    EMAIL_PORT=(int, 587),
    EMAIL_HOST_USER=(str, ""),
    EMAIL_HOST_PASSWORD=(str, ""),
    EMAIL_USE_TLS=(bool, True),
    AZURE_ACCOUNT_NAME=(str, None),
    AZURE_ACCOUNT_KEY=(str, None),
    AZURE_CONTAINER=(str, None),
)
env.read_env(BASE_DIR / ".env")


# ----- Basic settings  --------------------------------------------------------------------------------

DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
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

if CORS_ALLOWED_ORIGINS:
    # CORS_ALLOWED_ORIGINS items must be in the format e.g. 'http://localhost:3000' or 'https://hitas.dev.hel.ninja'
    CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

    # When not running locally, set the CSRF_COOKIE_DOMAIN variable
    if CORS_ALLOWED_ORIGINS[0].split("://")[1].split(":")[0] not in ["localhost", "127.0.0.1"]:
        # Assume that all urls are in the same domain except for the first part, e.g. 'hitas.dev.hel.ninja'
        # Take the first url and remove the first domain part to e.g. 'dev.hel.ninja'
        # Lastly add a dot in front of the url to make it a domain, e.g. '.dev.hel.ninja'
        # This allow 'csrftoken' cookie to be read/used by all subdomains, e.g. the frontend
        CSRF_COOKIE_DOMAIN = "." + ".".join(CORS_ALLOWED_ORIGINS[0].split(".")[1:])

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
    "subforms",
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

# ----- Static files -----------------------------------------------------------------------------------

STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "static/"

# ----- File uploads -----------------------------------------------------------------------------------

MEDIA_ROOT = BASE_DIR / "mediaroot"
MEDIA_URL = "media/"

AZURE_ACCOUNT_NAME = env("AZURE_ACCOUNT_NAME")
AZURE_ACCOUNT_KEY = env("AZURE_ACCOUNT_KEY")
AZURE_CONTAINER = env("AZURE_CONTAINER")
AZURE_URL_EXPIRATION_SECS = 7200
AZURE_CONNECTION_STRING = (
    f"DefaultEndpointsProtocol=https;"
    f"AccountName={AZURE_ACCOUNT_NAME};"
    f"AccountKey={AZURE_ACCOUNT_KEY};"
    f"EndpointSuffix=core.windows.net"
)
if AZURE_ACCOUNT_NAME is not None:
    DEFAULT_FILE_STORAGE = "storages.backends.azure_storage.AzureStorage"

# ----- Email ------------------------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

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
TIME_ZONE = "Europe/Helsinki"
USE_I18N = False
USE_TZ = True
LANGUAGES = [
    ("fi", gettext_lazy("Finnish")),
    ("en", gettext_lazy("English")),
]
LOCALE_PATHS = [
    BASE_DIR / "static" / "locale",
]

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
SOCIAL_AUTH_TUNNISTAMO_AUTH_EXTRA_ARGUMENTS = {"ui_locales": "fi"}
SOCIAL_AUTH_TUNNISTAMO_ALLOWED_REDIRECT_HOSTS = env("SOCIAL_AUTH_TUNNISTAMO_ALLOWED_REDIRECT_HOSTS")
SOCIAL_AUTH_TUNNISTAMO_PIPELINE = (
    *helusers.defaults.SOCIAL_AUTH_PIPELINE,
    "hitas.helauth.pipelines.migrate_user_from_tunnistamo_to_tunnistus",
)

HELUSERS_PASSWORD_LOGIN_DISABLED = False
HELUSERS_BACK_CHANNEL_LOGOUT_ENABLED = env("HELUSERS_BACK_CHANNEL_LOGOUT_ENABLED")

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

        try:
            _, _, ips = socket.gethostbyname_ex(socket.gethostname())
            INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1"]
        except Exception:
            INTERNAL_IPS = ["127.0.0.1", "localhost"]

# ------------------------------------------------------------------------------------------------------
