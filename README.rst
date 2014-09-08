BDR Organisations Registry
==========================

`bdr-registry`_ is a registry of company contacts (implemented as a
Django application) for the reporting process which is handled by the
`BDR Zope`_ application. Reporters from organisations can self-register
and then manage a list of contacts for their company. BDR helpdesk
can manage accounts and passwords and download CSV reports of
organisations.

.. _bdr-registry: https://bdr.eionet.europa.eu/registry/
.. _BDR Zope: https://bdr.eionet.europa.eu/


Workflows
---------

Company reporters
~~~~~~~~~~~~~~~~~~~~~~
Starting from the BDR homepage, reporters click on "Self-registration",
which takes them to a registration form on `bdr-registry`. The
information is saved in the `bdr-registry` database pending review by
helpdesk.

After they receive an account, reporters can follow a link on the
reporting folder, which takes them to a page in `bdr-registry`, where
they can update the company's contact details.

Helpdesk
~~~~~~~~
All helpdesk actions are performed via the `bdr management pages`_.

.. _bdr management pages: https://bdr.eionet.europa.eu/registry/management/

Helpdesk reviews self-registered organisations and creates LDAP accounts
and BDR reporting folders for them. These actions are performed via the
"action" menu after selecting one or more organisations. Optionally,
email notifications, containing the LDAP username and password, can be
sent to company contacts when the accounts are created, or at a
later time.

Helpdesk can download CSV reports of `companies`_ and `contact
persons`_.

.. _companies: https://bdr.eionet.europa.eu/registry/management/companies/export
.. _contact persons: https://bdr.eionet.europa.eu/registry/management/person/export


Architecture
------------

Authentication
~~~~~~~~~~~~~~
Authentication is performed using the Django authentication system
against the same LDAP server as the `BDR Zope` application.

User permissions for `bdr-registry` are configured via the `bdr management`_.
The `helpdesk` group grants permission to can edit/delete
any company, create/update LDAP accounts, reset passwords, and
create reporting folders in the `BDR Zope` application.

.. _bdr management: https://bdr.eionet.europa.eu/registry/management/

Company accounts have no special roles configured in
`bdr-registry`; they can edit their own company's contact details
based on the user id. They are however granted owner rights on their
reporting folder in the `BDR Zope` application, so they can upload files
and follow the envelope workflow steps.

Integration with other services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
`bdr-registry` creates/updates LDAP accounts using a privileged user,
configured using the ``LDAP_EDIT_*`` settings.

The `BDR Zope` application exposes an API to allow `bdr-registry` to
create folders for newly registered organisations. The endpoint is
configured using the ``BDR_API_*`` settings. The API is deployed in Zope
as a `Script (Python)` (source code at
``zope_api/create_organisation_folder.py``); the ``BDR_API_AUTH`` user
is granted Manager role on the entire `BDR Zope` application so it can
create reporting folders.

`WebQ`_ calls a `bdr-registry` API to fetch company details. This
API is protected using access tokens configured in the management interface.

When a user visits `bdr-registry` coming from the `BDR Zope`
application, and the user is not yet authenticated in `bdr-registry`,
the `HTTP Basic access authentication` information is used to log them
into `bdr-registry`.

.. _WebQ: http://webq.eionet.europa.eu/


Development and deployment
--------------------------
Install dependencies. It's a good idea to run this in a virtualenv_::

    $ pip install -r requirements-dev.txt

Create a local settings file by copying and modifying
``localsettings_example.py``.

Run the testsuite::

    $ ./manage.py test bdr_registry

Start the server locally::

    $ DJANGO_SETTINGS_MODULE=localsettings ./manage.py runserver

Run a management command, e.g. database initialization and migrations::

    $ DJANGO_SETTINGS_MODULE=localsettings ./manage.py syncdb
    $ DJANGO_SETTINGS_MODULE=localsettings ./manage.py migrate

The command to run the server in production::

    $ DJANGO_SETTINGS_MODULE=localsettings ./manage.py run_gunicorn

.. _virtualenv: http://www.virtualenv.org/
