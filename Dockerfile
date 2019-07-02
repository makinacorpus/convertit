FROM ubuntu:19.04
MAINTAINER Makina Corpus "contact@makina-corpus.com"

ADD . /opt/apps/convertit

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
    pip3 install -e /opt/apps/convertit/ && \
    pip3 install gunicorn

ADD .docker/run.sh /usr/local/bin/run

EXPOSE 8000

CMD ["/bin/sh", "-e", "/usr/local/bin/run"]
