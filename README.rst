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


Deployment using `sarge`
------------------------
1. First of all, install sarge_ in a folder on the server. We'll call it
``$SARGE_HOME`` below. A good choice is ``/var/local/bdr-registry``.
Don't forget to set up an init script that starts
``$SARGE_HOME/bin/supervisord`` at boot.

.. _sarge: http://mgax.github.com/sarge/

::

    $ sudo mkdir $SARGE_HOME; sudo chown `whoami`: $SARGE_HOME
    $ python <(curl -fsSL raw.github.com/mgax/sarge/master/install_sarge.py) $SARGE_HOME
    $ cd $SARGE_HOME

2. Upload a configuration file in ``$SARGE_HOME/etc/app/config.json``::

    {
      "BDR_REGISTRY_DATABASE": "/var/local/bdr-registry/var/db/db.sqlite",
      "BDR_ADMIN_EMAIL": "bdr.helpdesk@eea.europa.eu",
      "BDR_EMAIL_FROM": "BDR Registration <bdr-registration@eionet.europa.eu>",
      "BDR_REGISTRY_DJANGO_SECRET": "some random string",
      "BDR_REVERSE_PROXY": "on"
    }

3. Configure an external (stable) port number and a range of ports for
deployments. Add the following two lines to
``$SARGE_HOME/etc/sarge.yaml`` changing the numbers as needed. At
deployment, `sarge` will allocate a new port number from `port_range`,
and proxy connections from the stable port (the one in `port_map`).

::

    "port_map": {"web": "0.0.0.0:12300"},
    "port_range": [12310, 12349]


4. Copy all dependencies to ``$SARGE_HOME/dist``, either as source
distributions or wheel_ files. During deployment `pip` does not search
for packages over the network because it takes too much time.

.. _wheel: http://wheel.readthedocs.org/

5. Deploy the application. This requires a tarball of the repository
which can be obtained by running ``git archive HEAD >
bdr-registry.tar``.

::

    $ bin/sarge deploy bdr-registry.tar web

6. Set up a front-end web server (apache, nginx) to proxy requests to
the application on the port configured above. The server might need to
set ``X-Forwarded-Script-Name`` and ``X-Forwarded-Proto`` so the
application generates correct URLs.
