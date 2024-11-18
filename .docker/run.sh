#!/bin/bash
APP_ROOT=/opt/apps/convertit
INIPASTE=${INIPASTE:-production.ini}

cd $APP_ROOT

. /opt/venv/bin/activate

pserve $INIPASTE
