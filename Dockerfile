FROM ubuntu:jammy as base
MAINTAINER Makina Corpus "contact@makina-corpus.com"

RUN apt-get update && apt-get install -y -qq python3 libreoffice default-jre libreoffice-java-common inkscape python3-magic && \
    apt-get autoclean && apt-get clean all && rm -rf /var/apt/lists/*

WORKDIR /opt/apps/convertit

ADD .docker/run.sh /usr/local/bin/run

EXPOSE 6543
CMD ["/bin/sh", "-e", "/usr/local/bin/run"]

FROM base as build
RUN apt-get update && apt-get install -y -qq build-essential python3-venv python3-dev && \
    apt-get autoclean && apt-get clean all && rm -rf /var/apt/lists/*

ADD . /opt/apps/convertit

RUN python3 -m venv . && ./bin/pip install --no-cache-dir pip setuptools wheel -U
RUN ./bin/python setup.py install

FROM base as prod

COPY --from=build /opt/apps/convertit /opt/apps/convertit
ADD .docker/run.sh /usr/local/bin/run
