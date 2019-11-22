FROM ubuntu:bionic
MAINTAINER Makina Corpus "contact@makina-corpus.com"

RUN apt-get update && apt-get install -y -qq build-essential wget unoconv inkscape virtualenv && \
    apt-get autoclean && apt-get clean all && rm -rf /var/apt/lists/*

ADD . /opt/apps/convertit

WORKDIR /opt/apps/convertit

RUN virtualenv -p python3 .
RUN ./bin/python setup.py install

ADD .docker/run.sh /usr/local/bin/run

EXPOSE 6543
CMD ["/bin/sh", "-e", "/usr/local/bin/run"]
