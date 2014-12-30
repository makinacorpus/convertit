#!/bin/bash
APP_ROOT=/opt/apps/convertit
BRANCH=master
INIPASTE=${INIPASTE:-production.ini}

cd $APP_ROOT
git pull origin $BRANCH

bin/gunicorn_paster --workers=1 $INIPASTE
