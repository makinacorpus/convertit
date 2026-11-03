ARG DISTRO=resolute

FROM ghcr.io/astral-sh/uv:latest AS uv

FROM debian:trixie-slim AS base
LABEL org.opencontainers.image.authors="Makina Corpus <contact@makina-corpus.com>"

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked  \
    apt-get update && \
    apt-get install -y -qq --no-install-recommends \
        ca-certificates \
        libcairo2 \
        libmagic1 \
        libreoffice-calc-nogui \
        libreoffice-writer-nogui

WORKDIR /opt/apps/convertit

COPY .docker/run.sh /usr/local/bin/run

EXPOSE 6543
CMD ["/bin/sh", "-e", "/usr/local/bin/run"]

FROM base AS build
ARG PYTHON_VERSION=3.14

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked  \
    apt-get update && \
    apt-get install -y -qq --no-install-recommends build-essential

COPY --from=uv /uv /uvx /bin/

ENV UV_PYTHON_INSTALL_DIR=/opt/python

RUN uv python install ${PYTHON_VERSION} --install-dir ${UV_PYTHON_INSTALL_DIR}

RUN uv venv /opt/venv --python ${PYTHON_VERSION}

RUN --mount=type=bind,src=./requirements.txt,dst=/requirements.txt \
    --mount=type=cache,sharing=locked,uid=1001,gid=1001 \
    uv pip install --no-cache --python /opt/venv/bin/python -r /requirements.txt

COPY convertit /opt/apps/convertit/convertit
COPY manage.py /opt/apps/convertit/manage.py
COPY pyproject.toml /opt/apps/convertit/pyproject.toml
COPY README.md /opt/apps/convertit/README.md

RUN uv pip install --no-cache --no-deps --python /opt/venv/bin/python .


FROM build AS dev

RUN --mount=type=bind,src=./requirements-dev.txt,dst=/requirements-dev.txt \
    --mount=type=cache,sharing=locked,uid=1001,gid=1001 \
    uv pip install --no-cache --python /opt/venv/bin/python -r /requirements-dev.txt

FROM base AS prod

COPY --from=build /opt/python /opt/python
COPY --from=build /opt/venv /opt/venv
COPY convertit /opt/apps/convertit/convertit
COPY manage.py /opt/apps/convertit/manage.py
COPY pyproject.toml /opt/apps/convertit/pyproject.toml
COPY README.md /opt/apps/convertit/README.md
COPY docker.ini /opt/apps/convertit/production.ini
VOLUME /var/cache/convertit/downloads
VOLUME /var/cache/convertit/converted