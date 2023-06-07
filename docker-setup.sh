#!/bin/bash
set -e

if [ -z "$POSTGRES_ADDR" ]; then
  export POSTGRES_ADDR="postgres"
fi

while ! nc -z $POSTGRES_ADDR 5432; do
  echo "Waiting for Postgres server at '$POSTGRES_ADDR' to accept connections on port 5432..."
  sleep 1s
done

if ! test -e $BDR_REG_APP/bdr_registry/localsettings.py; then
    python configure.py
fi

args=("$@")
python manage.py collectstatic --noinput

if [ "x$DJANGO_MIGRATE" = 'xyes' ]; then
    python manage.py migrate
fi


case $1 in
    manage)
        python manage.py ${args[@]:1}
        ;;
    run)
        gunicorn bdr_registry.wsgi:application \
            --name bdr_registry \
            --bind 0.0.0.0:$BDR_REG_PORT \
            --workers 3 \
            --access-logfile - \
            --error-logfile -
        ;;
    *)
esac
