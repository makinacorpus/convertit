#!/bin/bash
APP_ROOT=/opt/apps/convertit
INIPASTE=${INIPASTE:-production.ini}

cd $APP_ROOT

. /opt/apps/convertit/bin/activate

gunicorn --workers=1 --paste=$INIPASTE
