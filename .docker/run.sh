#!/bin/bash
APP_ROOT=/opt/apps/convertit
INIPASTE=${INIPASTE:-production.ini}

cd $APP_ROOT

bin/gunicorn_paster --workers=1 $INIPASTE
