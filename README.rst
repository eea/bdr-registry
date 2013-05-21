BDR Company Registry
====================

A registry of company contacts for BDR_ environment reporting.

.. _BDR: https://bdr.eionet.europa.eu/


Deployment
----------

BDR is a Django app that is most easily deployed in a twelve-factor_
environment. The configuration comes from environment variables, logging
goes to `stderr`, and the web server is started by the command listed in
``Procfile``.

.. _twelve-factor: http://www.12factor.net/


Configuration variables
-----------------------
`bdr-registry` understands the following environment variables:

``DEBUG``
    Set Django's ``DEBUG`` flag.

``DATABASE``
    Path to SQLite database.

``BDR_HELPDESK_EMAIL``
    Email address which receives notifications of newly self-registered
    organisations.

``EMAIL_SERVER``
    SMTP server for outgoing email (for example ``localhost:25``). If
    blank or missing, email messages will be printed to `stdout`
    instead.

``BDR_EMAIL_FROM``
    Address used in `From:` field of outgoing email messages.

``SENTRY_DSN``
    DSN of sentry_ server (optional).

``DJANGO_SECRET``
    Secret key used by Django for sessions.

``REVERSE_PROXY``
    Set this to ``on`` when Django is behind a reverse proxy.

``STATIC_URL``
    URL where static files are served.

``AUTH_LDAP_SERVER``
    URL of LDAP server to use for authentication.

``BDR_REPORTEK_ORGANISATION_URL``
    URL pattern for links back to a company's reporting page.

``LDAP_EDIT_SERVER``, ``LDAP_EDIT_LOGIN``
    Server and credentials for modifying LDAP company accounts.

``ADMIN_ALL_BDR_TABLES``
    If set to ``on``, show `account` table in the Django admin.

``BDR_API_URL``
    URL for the BDR API. Currently ``https://bdr.eionet.europa.eu/api``.

``BDR_API_AUTH``
    Username and password for authentication to BDR API, separated by
    ``:``, for example ``joe:s3cr37``.

``AUDIT_LOG_FILE``
    Log file to write audit trail for sensitive operations (e.g.
    changing company passwords, creating reporting folders).


.. _sentry: http://pypi.python.org/pypi/sentry


Development
-----------
For local development here's a quick setup guide. It's a good idea to
do everything within a virtualenv_.

.. _virtualenv: http://www.virtualenv.org/

Here's a sample ``.env`` file for use with honcho_ or foreman_. Place
this at the root of the repository::

    BDR_REGISTRY_DEBUG=on
    BDR_REGISTRY_DATABASE=/tmp/db.sqlite
    BDR_EMAIL_FROM=BDR Registration <bdr-registration@eionet.europa.eu>
    TARGET=zope@vulture:/var/local/bdr-registry

.. _honcho: https://github.com/nickstenning/honcho
.. _foreman: http://ddollar.github.com/foreman/

Install dependencies::

    $ pip install -r requirements-dev.txt

Start the server locally::

    $ honcho start

Run a management command, e.g. database initialization and migrations::

    $ honcho run './manage.py syncdb'
    $ honcho run './manage.py migrate'
