#!/bin/bash
soffice --nologo --nodefault --nofirststartwizard --invisible --headless --norestore --accept='socket,host=localhost,port=2002,tcpNoDelay=1;urp;StarOffice.ComponentContext' &
gunicorn -b '0.0.0.0:8000' convertit.application:app
