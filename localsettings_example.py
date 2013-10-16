from bdr_registry.settings import *


class secure_str(str):
    """
    A string that doesn't print its contents on `repr()`. Useful to
    protect passwords.
    """
    __slots__ = ()
    __repr__ = object.__repr__


# DEBUG = TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': './db.sqlite',  # path to database file
    }
}

STATIC_ROOT = ''
STATIC_URL = '/static/'
SITE_URL = '/'
LOGIN_REDIRECT_URL = SITE_URL
SECRET_KEY = 'foo'  # replace this with a random string
# BDR_REVERSE_PROXY = True  # enable this when behind a reverse proxy


## email addresses
# BDR_HELPDESK_EMAIL = 'helpdesk@example.com'
# BDR_EMAIL_FROM = 'helpdesk@example.com'
# BDR_ORGEMAIL_ODS_BCC = ['foo@example.com', 'bar@example.com']
# BDR_ORGEMAIL_FGAS_BCC = ['foo@example.com', 'bar@example.com']


## email server
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 25


## sentry configuration
# INSTALLED_APPS += ('raven.contrib.django',)
# RAVEN_CONFIG = {
#     'dsn': 'http://example.com/.....',
# }


## authentication using LDAP
# AUTH_LDAP_SERVER_URI = "ldap://localhost:389/"
# AUTH_LDAP_BIND_DN = ""
# AUTH_LDAP_BIND_PASSWORD = ""
#
# import ldap
# from django_auth_ldap.config import LDAPSearch
# AUTH_LDAP_USER_SEARCH = LDAPSearch("o=EIONET,l=Europe",
#                                    ldap.SCOPE_SUBTREE,
#                                    "(uid=%(user)s)")
#
# AUTH_LDAP_USER_ATTR_MAP = {
#     "first_name": "givenName",
#     "last_name": "sn",
#     "email": "mail",
# }
#
# AUTHENTICATION_BACKENDS = (
#     'django_auth_ldap.backend.LDAPBackend',
#     'django.contrib.auth.backends.ModelBackend',
# )


## credentials for updating LDAP accounts
# LDAP_EDIT_SERVER = _ldap_edit_server
# LDAP_EDIT_DN = 'joe'
# LDAP_EDIT_PASSWORD = secure_str('s3cr37')


## integration with BDR Zope application
# BDR_REPORTEK_ORGANISATION_URL = '#'
# BDR_API_URL = 'http://example.com/api'
# BDR_API_AUTH = ('apiuser', secure_str('apipassword'))
# BDR_AUDIT_LOG_FILE = './bdr_audit.log'
