#!/bin/bash
set -e
SSL_CERTS_ROOT='/usr/local/share/ca-certificates'

if [ ! -z "$LDAPS_CACERT" ]; then
  echo -e "$LDAPS_CACERT" > "$SSL_CERTS_ROOT/CAcustom.crt"
  dpkg-reconfigure --force ca-certificates
fi

if [ -z "$MYSQL_ADDR" ]; then
  MYSQL_ADDR="mysql"
fi

while ! nc -z $MYSQL_ADDR 3306; do
  echo "Waiting for MySQL server at '$MYSQL_ADDR' to accept connections on port 3306..."
  sleep 3s
done

#create database for service
if ! mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "use $DATABASES_NAME;"; then
  echo "CREATE DATABASE $DATABASES_NAME"
  mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE $DATABASES_NAME CHARACTER SET utf8 COLLATE utf8_general_ci;"
  mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE USER '$DATABASES_USER'@'%' IDENTIFIED BY '$DATABASES_PASSWORD';"
  mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "GRANT ALL PRIVILEGES ON $DATABASES_NAME.* TO '$DATABASES_USER'@'%';"
fi

if ! test -e $BDR_REG_APP/bdr_registry/localsettings.py; then
    gosu bdrreg python configure.py
fi

args=("$@")
gosu bdrreg python manage.py collectstatic --noinput
gosu bdrreg python manage.py migrate --fake-initial

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
