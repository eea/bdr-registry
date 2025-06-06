from getenv import env
import ldap
import os
import sys

from django_auth_ldap.config import LDAPSearch
from bdr_registry.honeypot import honey_pot_value, honey_pot_checker


class secure_str(str):
    """
    A string that doesn't print its contents on `repr()`. Useful to
    protect passwords.
    """

    __slots__ = ()
    __repr__ = object.__repr__


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = env("DEBUG", False)
ALLOWED_HOSTS = env("ALLOWED_HOSTS", ["localhost", "127.0.0.1", "0.0.0.0"])
ADMIN_ALL_BDR_TABLES = env("ADMIN_ALL_BDR_TABLES", True)

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

DATABASES = {
    "default": {
        "ENGINE": env("DATABASES_ENGINE", "django.db.backends.sqlite3"),
        "NAME": env("DATABASES_NAME", "/db.sqlite"),
        "USER": env("DATABASES_USER", ""),
        "PASSWORD": env("DATABASES_PASSWORD", ""),
        "HOST": env("DATABASES_HOST", ""),
    }
}

ASSETS_DEBUG = True

ADMINS = ()

MANAGERS = ADMINS

TIME_ZONE = "Europe/Copenhagen"

LANGUAGE_CODE = "en-us"

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = ""

MEDIA_URL = ""

STATIC_ROOT = env("STATIC_ROOT", os.path.join(BASE_DIR, "static"))
STATIC_URL = env("STATIC_URL", "/static/")

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

SITE_URL = env("SITE_URL", "/")
LOGIN_REDIRECT_URL = SITE_URL
SECRET_KEY = env("SECRET_KEY", "moo4ge4F")

ACCOUNTS_PREFIX = ""

MIDDLEWARE = [
    "frame.middleware.RequestMiddleware",
    "frame.middleware.UserMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "bdr_registry.local.ThreadLocalRequestMiddleware",
    "django.contrib.auth.middleware.RemoteUserMiddleware",
]

ROOT_URLCONF = "bdr_registry.urls"

WSGI_APPLICATION = "bdr_registry.wsgi.application"

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admin",
    "django.contrib.staticfiles",
    "frame",
    "gunicorn",
    "widget_tweaks",
    "django_assets",
    "honeypot",
    "post_office",
    "bdr_management",
    "solo",
    "bdr_registry",
    "captcha",
)

# sentry configuration
if env("SENTRY_DSN", ""):
    INSTALLED_APPS += ("raven.contrib.django.raven_compat",)
    RAVEN_CONFIG = {"dsn": env("SENTRY_DSN")}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                "bdr_registry.context_processors.settings_context",
                "bdr_registry.context_processors.sentry",
                "bdr_registry.context_processors.use_sidemenu",
            ],
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        },
    },
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s %(module)s %(levelname)s %(message)s",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "stderr": {
            "level": "DEBUG" if DEBUG else "INFO",
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "root": {
        "handlers": ["stderr"],
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 3000,
        "OPTIONS": {"MAX_ENTRIES": 150},
    }
}

BDR_REVERSE_PROXY = env("BDR_REVERSE_PROXY", False)
BDR_SERVER_URL = env("BDR_SERVER_URL", "http://example.com/")

# email addresses
BDR_HELPDESK_EMAIL = env("BDR_HELPDESK_EMAIL", "")

BDR_EMAIL_FROM = env("BDR_EMAIL_FROM", "bdr@localhost")
HDV_EMAIL_FROM = env("HDV_EMAIL_FROM", "hdv@localhost")
HDV_RESIM_EMAIL_FROM = env("HDV_RESIM_EMAIL_FROM", "hdv@localhost")
ENABLE_HDV_EDITING = env("ENABLE_HDV_EDITING", False)
ENABLE_HDV_RESIM_EDITING = env("ENABLE_HDV_RESIM_EDITING", False)

HDV_MAIL_HEADERS = {
    "X-OTRS-IsVisibleForCustomer": "0",
    "X-OTRS-Loop": "True",
    "X-OTRS-Queue": "HDV CO2 monitoring",
}

HDV_RESIM_MAIL_HEADERS = {
    "X-OTRS-IsVisibleForCustomer": "0",
    "X-OTRS-Loop": "True",
    "X-OTRS-Queue": "HDV CO2 monitoring",
}

# email server
EMAIL_BACKEND = env("EMAIL_BACKEND", "post_office.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", "localhost")
EMAIL_PORT = env("EMAIL_PORT", 25)

# authentication using LDAP
AUTH_LDAP_SERVER_URI = env("AUTH_LDAP_SERVER_URI", "")
AUTH_LDAP_BIND_DN = env("AUTH_LDAP_BIND_DN", "")
AUTH_LDAP_BIND_PASSWORD = secure_str(env("AUTH_LDAP_BIND_PASSWORD", ""))
AUTH_LDAP_BASE_DN = env("AUTH_LDAP_BASE_DN", "")
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    AUTH_LDAP_BASE_DN, ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
)

AUTH_LDAP_USER_ATTR_MAP = env(
    "AUTH_LDAP_USER_ATTR_MAP",
    {
        "first_name": "givenName",
        "last_name": "sn",
        "email": "mail",
    },
)

AUTHENTICATION_BACKENDS = env(
    "AUTHENTICATION_BACKENDS",
    (
        "django_auth_ldap.backend.LDAPBackend",
        "django.contrib.auth.backends.ModelBackend",
        "frame.backends.FrameUserBackend",
    ),
)

FRAME_URL = env("FRAME_URL", "")
FRAME_VERIFY_SSL = env("FRAME_VERIFY_SSL", False)
FRAME_COOKIES = env("FRAME_COOKIES", [])
USE_ZOPE_LOGIN = env("USE_ZOPE_LOGIN", False)

# credentials for updating LDAP accounts
LDAP_EDIT_SERVER = AUTH_LDAP_SERVER_URI
LDAP_EDIT_DN = env("LDAP_EDIT_DN", "")
LDAP_EDIT_PASSWORD = secure_str(env("LDAP_EDIT_PASSWORD", ""))

BDR_REPORTEK_ORGANISATION_URL = env("BDR_REPORTEK_ORGANISATION_URL", "#")
BDR_API_URL = env("BDR_API_PORTAL_URL", "")
BDR_AUDIT_LOG_FILE = env("BDR_AUDIT_LOG_FILE", None)

BDR_API_AUTH_USER = env("BDR_API_AUTH_USER", "")
BDR_API_AUTH_PASSWORD = env("BDR_API_AUTH_PASSWORD", "")
BDR_API_AUTH = (BDR_API_AUTH_USER, secure_str(BDR_API_AUTH_PASSWORD))

USE_SIDEMENU = env("USE_SIDEMENU", False)
BDR_SIDEMENU_URL = env("BDR_SIDEMENU_URL", "http://example.com/left_menu")
DATE_FORMAT = "%d %b %Y"

BDR_HELPDESK_GROUP = "BDR helpdesk"
LOCALITIES_TABLE_URL = "https://bdr.eionet.europa.eu/localities_table"
SELF_OBL_EXCLUDE = ["fgas", "ods", "mercury", "hdv", "hdv_resim"]
FIRST_REPORTING_YEAR = 2012

# random name, not honeypot :)
HONEYPOT_FIELD_NAME = "company_identifier"
HONEYPOT_FORMAT = "%d%m%Y%H%S%M"
HONEYPOT_VALUE = honey_pot_value
HONEYPOT_VERIFIER = honey_pot_checker

try:
    from localsettings import *
except ImportError:
    pass


if "test" in sys.argv:
    try:
        from bdr_registry.test_settings import *
    except ImportError:
        pass

    # pop 'django.contrib.auth.middleware.RemoteUserMiddleware'
    MIDDLEWARE = MIDDLEWARE[:-1]
    CAPTCHA_TEST_MODE = True
