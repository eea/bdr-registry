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


Deployment using `sarge`
------------------------
1. First of all, install sarge_ in a folder on the server. We'll call it
   ``$SARGE_HOME`` below. A good choice is ``/var/local/bdr-registry``.
   Don't forget to set up an init script that starts
   ``$SARGE_HOME/bin/supervisord`` at boot.

   ::

       $ sudo mkdir $SARGE_HOME; sudo chown `whoami`: $SARGE_HOME
       $ python <(curl -fsSL raw.github.com/mgax/sarge/master/install_sarge.py) $SARGE_HOME
       $ cd $SARGE_HOME

2. Upload a configuration file in ``$SARGE_HOME/etc/app/config.json``::

       {
         "DATABASE": "/var/local/bdr-registry/var/db/db.sqlite",
         "BDR_HELPDESK_EMAIL": "bdr.helpdesk@eea.europa.eu",
         "BDR_EMAIL_FROM": "BDR Registration <bdr-registration@eionet.europa.eu>",
         "DJANGO_SECRET": "some random string",
         "REVERSE_PROXY": "on"
       }

3. Configure an external (stable) port number and a range of ports for
   deployments. Add the following two lines to
   ``$SARGE_HOME/etc/sarge.yaml`` changing the numbers as needed. At
   deployment, `sarge` will allocate a new port number from
   `port_range`, and proxy connections from the stable port (the one in
   `port_map`).

   ::

       "port_map": {"web": "0.0.0.0:12300"},
       "port_range": [12310, 12349]


4. Copy all dependencies to ``$SARGE_HOME/dist``, either as source
   distributions or wheel_ files. During deployment `pip` does not
   search for packages over the network because it takes too much time.

5. Deploy the application. This can be done with the `fabric` script
   included, provided that ``TARGET`` is set in ``.env``::

       $ honcho run fab deploy

6. Set up a front-end web server (apache, nginx) to proxy requests to
the application on the port configured above. The server might need to
set ``X-Forwarded-Script-Name`` and ``X-Forwarded-Proto`` so the
application generates correct URLs.

.. _wheel: http://wheel.readthedocs.org/
.. _sarge: http://mgax.github.com/sarge/
