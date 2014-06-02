import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG
ADMIN_ALL_BDR_TABLES = DEBUG

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

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SITE_URL = '/'
LOGIN_REDIRECT_URL = SITE_URL

BDR_REVERSE_PROXY = False

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'bdr_registry.local.ThreadLocalRequestMiddleware',
)

ROOT_URLCONF = 'bdr_registry.urls'

WSGI_APPLICATION = 'bdr_registry.wsgi.application'

TEMPLATE_DIRS = (
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'south',
    'gunicorn',
    'raven.contrib.django',
    'widget_tweaks',
    'bdr_registry',
    'django_assets',
    'post_office',
    'bdr_management',
    'django_settings',
)

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'bdr_registry.context_processors.settings_context',
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


BDR_HELPDESK_EMAIL = ''

EMAIL_BACKEND = 'post_office.EmailBackend'

BDR_EMAIL_FROM = 'bdr@localhost'
BDR_REPORTEK_ORGANISATION_URL = '#'
BDR_API_URL = None
BDR_API_AUTH = None
BDR_AUDIT_LOG_FILE = None

DATE_FORMAT = '%d %b %Y'

BDR_HELPDESK_GROUP = 'BDR helpdesk'

LOCALITIES_TABLE_URL = 'https://bdr.eionet.europa.eu/localities_table'

try:
    from localsettings import *
except ImportError:
    pass


if 'test' in sys.argv:
    try:
        from test_settings import *
    except ImportError:
        pass

DJANGO_SETTINGS = {
   'Reporting year': ('Integer', 2014),
}

FIRST_REPORTING_YEAR = 2012
