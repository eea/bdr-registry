BDR Organisations Registry
==========================

`bdr-registry`_ is a registry of organisation contacts (implemented as a
Django application) for the reporting process which is handled by the
`BDR Zope`_ application. Reporters from organisations can self-register
and then manage a list of contacts for their organisation. BDR helpdesk
can manage accounts and passwords and download CSV reports of
organisations.

.. _bdr-registry: https://bdr.eionet.europa.eu/registry/
.. _BDR Zope: https://bdr.eionet.europa.eu/


Workflows
---------

Organisation reporters
~~~~~~~~~~~~~~~~~~~~~~
Starting from the BDR homepage, reporters click on "Self-registration",
which takes them to a registration form on `bdr-registry`. The
information is saved in the `bdr-registry` database pending review by
helpdesk.

After they receive an account, reporters can follow a link on the
reporting folder, which takes them to a page in `bdr-registry`, where
they can update the organisation's contact details.

Helpdesk
~~~~~~~~
All helpdesk actions are performed via the `Django admin pages`_.

.. _Django admin pages: https://bdr.eionet.europa.eu/registry/admin/

Helpdesk reviews self-registered organisations and creates LDAP accounts
and BDR reporting folders for them. These actions are performed via the
"action" menu after selecting one or more organisations. Optionally,
email notifications, containing the LDAP username and password, can be
sent to organisation contacts when the accounts are created, or at a
later time.

Helpdesk can download CSV reports of organisations_ and `contact
persons`_.

.. _organisations: https://bdr.eionet.europa.eu/registry/admin/bdr_registry/organisation/export
.. _contact persons: https://bdr.eionet.europa.eu/registry/admin/bdr_registry/person/export


Architecture
------------

Authentication
~~~~~~~~~~~~~~
Authentication is performed using the Django authentication system
against the same LDAP server as the `BDR Zope` application.

User permissions for `bdr-registry` are configured via the `admin
interface`_. The `helpdesk` group grants permission to can edit/delete
any organisation, create/update LDAP accounts, reset passwords, and
create reporting folders in the `BDR Zope` application.

.. _admin interface: https://bdr.eionet.europa.eu/registry/admin/

Organisation accounts have no special roles configured in
`bdr-registry`; they can edit their own organisation's contact details
based on the user id. They are however granted owner rights on their
reporting folder in the `BDR Zope` application, so they can upload files
and follow the envelope workflow steps.

Integration with other services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
`bdr-registry` creates/updates LDAP accounts using a privileged user,
configured using the ``LDAP_EDIT_SERVER`` and ``LDAP_EDIT_LOGIN``
settings.

The `BDR Zope` application exposes an API to allow `bdr-registry` to
create folders for newly registered organisations. The endpoint is
configured using the ``BDR_API_URL`` and ``BDR_API_AUTH`` settings. The
API is deployed in Zope as a `Script (Python)` (source code at
``zope_api/create_organisation_folder.py``); the ``BDR_API_AUTH`` user
is granted Manager role on the entire `BDR Zope` application so it can
create reporting folders.

`WebQ`_ calls a `bdr-registry` API to fetch organisation details. This
API is protected using access tokens configured in the admin interface.

When a user visits `bdr-registry` coming from the `BDR Zope`
application, and the user is not yet authenticated in `bdr-registry`,
the `HTTP Basic access authentication` information is used to log them
into `bdr-registry`.

.. _WebQ: http://webq.eionet.europa.eu/


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
    URL pattern for links back to a organisation's reporting page.

``LDAP_EDIT_SERVER``, ``LDAP_EDIT_LOGIN``
    Server and credentials for modifying LDAP organisation accounts.

``ADMIN_ALL_BDR_TABLES``
    If set to ``on``, show `account` table in the Django admin.

``BDR_API_URL``
    URL for the BDR API. Currently ``https://bdr.eionet.europa.eu/api``.

``BDR_API_AUTH``
    Username and password for authentication to BDR API, separated by
    ``:``, for example ``joe:s3cr37``.

``AUDIT_LOG_FILE``
    Log file to write audit trail for sensitive operations (e.g.
    changing organisation passwords, creating reporting folders).


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

Run the testsuite::

    $ ./manage.py test bdr_registry

Start the server locally::

    $ honcho start

Run a management command, e.g. database initialization and migrations::

    $ honcho run './manage.py syncdb'
    $ honcho run './manage.py migrate'
