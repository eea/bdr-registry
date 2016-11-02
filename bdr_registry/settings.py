import os
import sys
from getenv import env
import ldap
from django_auth_ldap.config import LDAPSearch

class secure_str(str):
    """
    A string that doesn't print its contents on `repr()`. Useful to
    protect passwords.
    """
    __slots__ = ()
    __repr__ = object.__repr__


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = env('DEBUG', False)
ALLOWED_HOSTS = env('ALLOWED_HOSTS', ['localhost', '127.0.0.1'])
ADMIN_ALL_BDR_TABLES = env('ADMIN_ALL_BDR_TABLES', False)

DATABASES = env('DATABASES', {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': './db.sqlite',  # path to database file
    }
})

ASSETS_DEBUG = True

ADMINS = ()

MANAGERS = ADMINS

TIME_ZONE = 'Europe/Copenhagen'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = ''

MEDIA_URL = ''

STATIC_ROOT = env('STATIC_ROOT', os.path.join(BASE_DIR, 'static'))
STATIC_URL = env('STATIC_URL', '/static/')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SITE_URL = env('SITE_URL', '/')
LOGIN_REDIRECT_URL = SITE_URL
SECRET_KEY = env('SECRET_KEY', 'moo4ge4F')

ACCOUNTS_PREFIX = ''

MIDDLEWARE_CLASSES = (
    'frame.middleware.RequestMiddleware',
    'frame.middleware.UserMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'bdr_registry.local.ThreadLocalRequestMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
)

ROOT_URLCONF = 'bdr_registry.urls'

WSGI_APPLICATION = 'bdr_registry.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django_nose',
    'frame',
    'gunicorn',
    'raven.contrib.django',
    'widget_tweaks',
    'django_assets',
    'post_office',
    'bdr_management',
    'solo',
    'bdr_registry',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'bdr_registry.context_processors.settings_context',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        }
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(module)s %(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'stderr': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'root': {
        'handlers': ['stderr'],
    }
}

BDR_REVERSE_PROXY = env('BDR_REVERSE_PROXY', False)
BDR_SERVER_URL = env('BDR_SERVER_URL', 'http://example.com/')

# email addresses
BDR_HELPDESK_EMAIL = env('BDR_HELPDESK_EMAIL', '')
BDR_EMAIL_FROM = env('BDR_EMAIL_FROM', 'bdr@localhost')

# email server
EMAIL_BACKEND = env('EMAIL_BACKEND', 'post_office.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', 'localhost')
EMAIL_PORT = env('EMAIL_PORT', 25)

# authentication using LDAP
AUTH_LDAP_SERVER_URI = env('AUTH_LDAP_SERVER_URI', '')
AUTH_LDAP_BIND_DN = env('AUTH_LDAP_BIND_DN', '')
AUTH_LDAP_BIND_PASSWORD = secure_str(env('AUTH_LDAP_BIND_PASSWORD', ''))
AUTH_LDAP_BASE_DN = env('AUTH_LDAP_BASE_DN', '')
AUTH_LDAP_USER_SEARCH = LDAPSearch(AUTH_LDAP_BASE_DN,
                                  ldap.SCOPE_SUBTREE,
                                  '(uid=%(user)s)')

AUTH_LDAP_USER_ATTR_MAP = env('AUTH_LDAP_USER_ATTR_MAP', {
   "first_name": "givenName",
   "last_name": "sn",
   "email": "mail",
})

AUTHENTICATION_BACKENDS = env('AUTHENTICATION_BACKENDS', (
   'django_auth_ldap.backend.LDAPBackend',
   'django.contrib.auth.backends.ModelBackend',
   'frame.backends.FrameUserBackend',
))

FRAME_URL = env('FRAME_URL', '')
FRAME_VERIFY_SSL = env('FRAME_VERIFY_SSL', False)
FRAME_COOKIES = env('FRAME_COOKIES', [])

# credentials for updating LDAP accounts
LDAP_EDIT_SERVER = AUTH_LDAP_SERVER_URI
LDAP_EDIT_DN = env('LDAP_EDIT_DN', '')
LDAP_EDIT_PASSWORD = secure_str(env('LDAP_EDIT_PASSWORD', ''))

BDR_REPORTEK_ORGANISATION_URL = env('BDR_REPORTEK_ORGANISATION_URL', '#')
BDR_API_URL = env('BDR_API_PORTAL_URL', 'http://example.com/api')
BDR_AUDIT_LOG_FILE = env('BDR_AUDIT_LOG_FILE', None)

BDR_API_AUTH_USER = env('BDR_API_AUTH_USER', '')
BDR_API_AUTH_PASSWORD = env('BDR_API_AUTH_PASSWORD', '')
BDR_API_AUTH = (BDR_API_AUTH_USER, secure_str(BDR_API_AUTH_PASSWORD))

DATE_FORMAT = '%d %b %Y'

BDR_HELPDESK_GROUP = 'BDR helpdesk'
LOCALITIES_TABLE_URL = 'https://bdr.eionet.europa.eu/localities_table'
SELF_OBL_EXCLUDE = ['fgas']
FIRST_REPORTING_YEAR = 2012

#TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=bdr_registry,bdr_management',
]

try:
    from localsettings import *
except ImportError:
    pass


if 'test' in sys.argv:
    try:
        from test_settings import *
    except ImportError:
        pass

    # pop 'django.contrib.auth.middleware.RemoteUserMiddleware'
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES[:-1]
