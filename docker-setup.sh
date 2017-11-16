#!/bin/bash
set -e
SSL_CERTS_ROOT='/usr/local/share/ca-certificates'

if [ ! -z "$LDAPS_CACERT" ]; then
  echo -e "$LDAPS_CACERT" > "$SSL_CERTS_ROOT/CAcustom.crt"
  dpkg-reconfigure --force ca-certificates
fi

if [ -z "$POSTGRES_ADDR" ]; then
  export POSTGRES_ADDR="postgres"
fi

while ! nc -z $POSTGRES_ADDR 5432; do
  echo "Waiting for Postgres server at '$POSTGRES_ADDR' to accept connections on port 5432..."
  sleep 1s
done

if ! test -e $BDR_REG_APP/bdr_registry/localsettings.py; then
    gosu bdrreg python configure.py
fi

args=("$@")
gosu bdrreg python manage.py collectstatic --noinput
gosu bdrreg python manage.py migrate

case $1 in
    manage)
        gosu bdrreg python manage.py ${args[@]:1}
        ;;
    run)
        gosu bdrreg gunicorn bdr_registry.wsgi:application \
            --name bdr_registry \
            --bind 0.0.0.0:$BDR_REG_PORT \
            --workers 3 \
            --access-logfile - \
            --error-logfile -
        ;;
    *)
esac
