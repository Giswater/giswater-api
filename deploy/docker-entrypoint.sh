#!/bin/sh
# Production entrypoint: named Docker volumes mount as root-owned; ensure /app/logs
# is writable by the app user before dropping privileges.
set -e

mkdir -p /app/logs
chown -R app:app /app/logs

if [ "$(id -u)" = "0" ]; then
  exec su -s /bin/sh app -c 'cd /app && exec gunicorn -c gunicorn.conf.py app.main:app'
fi

exec gunicorn -c gunicorn.conf.py app.main:app
