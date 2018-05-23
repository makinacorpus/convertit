FROM ubuntu:bionic
MAINTAINER Makina Corpus "contact@geotrek.fr"

RUN apt-get update && apt-get install -y -qq build-essential wget unoconv inkscape python-pip python-virtualenv && \
    apt-get autoclean && apt-get clean all && rm -rf /var/apt/lists/*

ADD . /opt/apps/convertit

WORKDIR /opt/apps/convertit

RUN virtualenv .
RUN ./bin/pip install Pillow django>=1.11.11 gunicorn
RUN ./bin/python setup.py develop

ADD .docker/run.sh /usr/local/bin/run

EXPOSE 6543
CMD ["/bin/sh", "-e", "/usr/local/bin/run"]
