BDR Company Registry
====================

A registry of company contacts for BDR_ environment reporting.

.. _BDR: https://bdr.eionet.europa.eu/

BDR is a Django app that is most easily deployed in a twelve-factor_
environment. The configuration comes from environment variables, logging
goes to `stderr`, and the web server is started by the command listed in
``Procfile``. Currently the project is deployed in production using
sarge_.

.. _twelve-factor: http://www.12factor.net/
.. _sarge: http://mgax.github.com/sarge/


Configuration variables
-----------------------
`bdr-registry` understands the following environment variables:

``BDR_REGISTRY_DEBUG``
    Set Django's ``DEBUG`` flag.

``BDR_REGISTRY_DATABASE``
    Path to SQLite database.

``BDR_ADMIN_EMAIL``
    Email address which receives notifications of newly self-registered
    organisations.

``BDR_EMAIL_FROM``
    Address used in `From:` field of outgoing email messages.

``BDR_REGISTRY_SENTRY_DSN``
    DSN of sentry_ server (optional.

``BDR_REGISTRY_DJANGO_SECRET``
    Secret key used by Django for sessions.

``BDR_REVERSE_PROXY``
    Set this to ``on`` when Django is behind a reverse proxy.

``BDR_STATIC_URL``
    URL where static files are served.

``BDR_AUTH_LDAP_SERVER``
    URL of LDAP server to use for authentication.

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

.. _honcho: https://github.com/nickstenning/honcho
.. _foreman: http://ddollar.github.com/foreman/

Install dependencies::

    $ pip install -r requirements-dev.txt

Start the server locally::

    $ honcho start

Run a management command, e.g. database initialization and migrations::

    $ honcho run './manage.py syncdb'
    $ honcho run './manage.py migrate'
