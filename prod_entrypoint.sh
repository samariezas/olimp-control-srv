#!/usr/bin/env bash
set -xe

# TODO: look over the warnings, maybe add --fail-level WARNING
python manage.py check --deploy
python manage.py collectstatic --clear --noinput
python manage.py migrate --noinput

# for worker count, see: https://gunicorn.org/design/#how-many-workers
su ctrl -c "python -m gunicorn --bind 0.0.0.0:8000 --workers $(( 2 * $(nproc) + 1 )) ctrl_srv.wsgi:application"
