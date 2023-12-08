#!/bin/bash
APP_ROOT=/opt/apps/convertit
INIPASTE=${INIPASTE:-production.ini}

cd $APP_ROOT

. /opt/venv/bin/activate

gunicorn --workers=1 --paste=$INIPASTE --bind=0.0.0.0:6543
