import os

import environ
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import TokenAuthentication

# Set up .env
root = environ.Path(__file__) - 2
assert os.path.exists(root("manage.py"))
var_root = root("var")

BASE_DIR = root()

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
    SENTRY_DSN=(str, None),
    SENTRY_ENVIRONMENT=(str, "unknown"),
    SENTRY_SAMPLE_RATE=(float, 1.0),
    SENTRY_TRACES_SAMPLE_RATE=(float, 0.1),
)
env.read_env(os.path.join(BASE_DIR, ".env"))

DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
var_root = env.path("VAR_ROOT")
STATIC_ROOT = var_root("static")
MEDIA_ROOT = var_root("media")
STATIC_URL = env("STATIC_URL")
MEDIA_URL = env("MEDIA_URL")
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
UWSGI_WARMUP = env("UWSGI_WARMUP")

# Application definition
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
]

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

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEST_RUNNER = "hitas.tests.runner.HitasDatabaseRunner"


class BearerAuthentication(TokenAuthentication):
    keyword = "Bearer"


REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "hitas.exceptions.exception_handler",
    "COERCE_DECIMAL_TO_STRING": False,
    "DEFAULT_FILTER_BACKENDS": ("hitas.views.utils.HitasFilterBackend",),
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["config.settings.BearerAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}

if DEBUG:
    # Enable session authentication for browseable API renderer
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].append("rest_framework.authentication.SessionAuthentication")
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
        "hitas.types.HitasJSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ]
else:
    # Disable browseable API renderer if DEBUG is not set
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = ("hitas.types.HitasJSONRenderer",)

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

CORS_EXPOSE_HEADERS = ["Content-Disposition"]

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/admin/login/"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": env.db("DATABASE_URL"),
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

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
