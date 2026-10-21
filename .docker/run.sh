#!/bin/bash
APP_ROOT=/opt/apps/convertit
export INIPASTE=${INIPASTE:-production.ini}
export CONVERTIT_INI=${CONVERTIT_INI:-$INIPASTE}
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-convertit.settings}

cd $APP_ROOT

. /opt/venv/bin/activate

gunicorn -c python:convertit.gunicorn_conf convertit.wsgi:application
