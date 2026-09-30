ARG DISTRO=noble

FROM ghcr.io/astral-sh/uv:latest AS uv

FROM ubuntu:${DISTRO} AS base
LABEL org.opencontainers.image.authors="Makina Corpus <contact@makina-corpus.com>"

RUN apt-get update && apt-get install -y -qq libreoffice default-jre libreoffice-java-common inkscape libmagic1 && \
    apt-get autoclean && apt-get clean all && rm -rf /var/apt/lists/*

WORKDIR /opt/apps/convertit

COPY .docker/run.sh /usr/local/bin/run

EXPOSE 6543
CMD ["/bin/sh", "-e", "/usr/local/bin/run"]

FROM base AS build
ARG PYTHON_VERSION=3.14

RUN apt-get update && apt-get install -y -qq build-essential ca-certificates && \
    apt-get autoclean && apt-get clean all && rm -rf /var/apt/lists/*

COPY --from=uv /uv /uvx /bin/

ENV UV_PYTHON_INSTALL_DIR=/opt/python

RUN uv python install ${PYTHON_VERSION} --install-dir ${UV_PYTHON_INSTALL_DIR}

RUN uv venv /opt/venv --python ${PYTHON_VERSION}

COPY requirements.txt /requirements.txt

RUN uv pip install --no-cache --python /opt/venv/bin/python "setuptools<81" wheel && \
    uv pip install --no-cache --python /opt/venv/bin/python -r /requirements.txt

COPY convertit /opt/apps/convertit/convertit
COPY setup.py /opt/apps/convertit/setup.py
COPY README.rst /opt/apps/convertit/README.rst

RUN uv pip install --no-cache --no-deps --python /opt/venv/bin/python .


FROM build AS dev

COPY requirements-dev.txt /requirements-dev.txt

RUN uv pip install --no-cache --python /opt/venv/bin/python -r /requirements-dev.txt

FROM base AS prod

COPY --from=build /opt/python /opt/python
COPY --from=build /opt/venv /opt/venv
COPY convertit /opt/apps/convertit/convertit
COPY setup.py /opt/apps/convertit/setup.py
COPY README.rst /opt/apps/convertit/README.rst
COPY docker.ini /opt/apps/convertit/production.ini
VOLUME /var/cache/convertit/downloads
VOLUME /var/cache/convertit/converted