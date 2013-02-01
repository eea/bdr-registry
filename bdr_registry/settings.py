import os

DEBUG = bool(os.environ.get('DEBUG'))
TEMPLATE_DEBUG = DEBUG
ADMIN_ALL_BDR_TABLES = (DEBUG or os.environ.get('ADMIN_ALL_BDR_TABLES') == 'on')

ADMINS = ()

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('DATABASE', 'db.sqlite'),
    }
}

TIME_ZONE = 'Europe/Copenhagen'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = ''

MEDIA_URL = ''

STATIC_ROOT = os.environ.get('STATIC_ROOT', '')

STATIC_URL = os.environ.get('STATIC_URL', '/static/')

STATICFILES_DIRS = ()

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = os.environ.get('DJANGO_SECRET', 'asdf')

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

_sentry_dsn = os.environ.get('SENTRY_DSN')
if _sentry_dsn:
    INSTALLED_APPS += ('raven.contrib.django',)
    RAVEN_CONFIG = {
        'dsn': _sentry_dsn,
    }

BDR_HELPDESK_EMAIL = os.environ.get('BDR_HELPDESK_EMAIL', '')
_email_server = os.environ.get('EMAIL_SERVER', '')
if _email_server:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST, _email_port = _email_server.split(':')
    EMAIL_PORT = int(_email_port)
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

BDR_EMAIL_FROM = os.environ.get('BDR_EMAIL_FROM', 'bdr@localhost')

_auth_ldap_server = os.environ.get('AUTH_LDAP_SERVER')
if _auth_ldap_server:
    AUTH_LDAP_SERVER_URI = _auth_ldap_server
    AUTH_LDAP_BIND_DN = ""
    AUTH_LDAP_BIND_PASSWORD = ""

    import ldap
    from django_auth_ldap.config import LDAPSearch
    AUTH_LDAP_USER_SEARCH = LDAPSearch("o=EIONET,l=Europe",
                                       ldap.SCOPE_SUBTREE,
                                       "(uid=%(user)s)")

    AUTH_LDAP_USER_ATTR_MAP = {
        "first_name": "givenName",
        "last_name": "sn",
        "email": "mail",
    }

    AUTHENTICATION_BACKENDS = (
        'django_auth_ldap.backend.LDAPBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

_ldap_edit_server = os.environ.get('LDAP_EDIT_SERVER')
if _ldap_edit_server:
    LDAP_EDIT_SERVER = _ldap_edit_server
    (LDAP_EDIT_DN, LDAP_EDIT_PASSWORD) = \
        os.environ.get('LDAP_EDIT_LOGIN').split(':')

BDR_REPORTEK_ORGANISATION_URL = os.environ.get(
    'BDR_REPORTEK_ORGANISATION_URL', '#')
BDR_API_URL = os.environ.get('BDR_API_URL')
BDR_API_AUTH = os.environ.get('BDR_API_AUTH')
