ARG DISTRO=jammy

FROM ubuntu:${DISTRO} AS base
LABEL org.opencontainers.image.authors="Makina Corpus <contact@makina-corpus.com>"


RUN apt-get update && apt-get install -y -qq python3 libreoffice default-jre libreoffice-java-common inkscape python3-magic && \
    apt-get autoclean && apt-get clean all && rm -rf /var/apt/lists/*


WORKDIR /opt/apps/convertit

COPY .docker/run.sh /usr/local/bin/run

EXPOSE 6543
CMD ["/bin/sh", "-e", "/usr/local/bin/run"]

FROM base AS build
RUN apt-get update && apt-get install -y -qq build-essential python3-venv python3-dev && \
    apt-get autoclean && apt-get clean all && rm -rf /var/apt/lists/*

COPY requirements.txt /requirements.txt

RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir pip setuptools wheel -U && /opt/venv/bin/pip install --no-cache-dir -U -r /requirements.txt


FROM build AS dev

COPY dev-requirements.txt /dev-requirements.txt

RUN /opt/venv/bin/pip install --no-cache-dir -U -r /dev-requirements.txt

FROM base AS prod

COPY --from=build /opt/apps/convertit /opt/apps/convertit
COPY --from=build /opt/venv /opt/venv
COPY convertit /opt/apps/convertit/convertit
COPY setup.py /opt/apps/convertit/setup.py
COPY README.rst /opt/apps/convertit/README.rst
RUN /opt/venv/bin/pip install .
COPY production.ini /opt/apps/convertit/production.ini
