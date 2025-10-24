#!/bin/sh
set -e

echo "Waiting for Postgres..."
until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done

echo "Postgres is ready!"

echo "Running Django migrations..."
python manage.py migrate --noinput

# echo "Collecting static files..."
# python manage.py collectstatic --noinput
if [ "$1" ]; then
  exec "$@"
else
    echo "Starting development server port $API_PORT"
    python manage.py runserver 0.0.0.0:$API_PORT
fi