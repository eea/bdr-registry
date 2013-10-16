
DEBUG = False
TEMPLATE_DEBUG = DEBUG
ADMIN_ALL_BDR_TABLES = DEBUG

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

STATIC_ROOT = ''

STATIC_URL = '/static/'

STATICFILES_DIRS = ()

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
    'bdr_registry',
    'south',
    'gunicorn',
    'raven.contrib.django',
    'widget_tweaks',
)

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
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

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

BDR_EMAIL_FROM = 'bdr@localhost'

BDR_ORGEMAIL_ODS_BCC = []
BDR_ORGEMAIL_FGAS_BCC = []



BDR_REPORTEK_ORGANISATION_URL = '#'

BDR_API_URL = None
BDR_API_AUTH = None


BDR_AUDIT_LOG_FILE = None


try:
    from localsettings import *
except ImportError:
    pass
