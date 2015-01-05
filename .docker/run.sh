#!/bin/bash
APP_ROOT=/opt/apps/convertit
BRANCH=master
INIPASTE=${INIPASTE:-production.ini}

cd $APP_ROOT
git pull origin $BRANCH

bin/celery -P solo -A convertit.converters.tasks worker &
bin/gunicorn_paster --workers=4 $INIPASTE
