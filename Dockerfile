FROM ubuntu:19.04

RUN apt-get update && \
    apt-get install -y python3-pip \
    libreoffice \
    git-core \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info && \
    rm -r /var/lib/apt/lists/* && \
    pip3 install -e git+https://github.com/courtem/convertit.git@server#egg=convertit

CMD bash -c "(soffice --nologo --nodefault \
            --nofirststartwizard --invisible \
            --headless --norestore --accept='socket,host=localhost,port=2002,tcpNoDelay=1;urp;StarOffice.ComponentContext' &) && \
            (gunicorn -b '0.0.0.0:8000' convertit.application:app)"
