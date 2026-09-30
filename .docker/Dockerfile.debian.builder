ARG DISTRO=debian:bookworm

FROM ghcr.io/astral-sh/uv:latest AS uv

FROM ${DISTRO} AS base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq -o Acquire::Languages=none && \
    apt-get install -yqq --no-install-recommends \
    dpkg-dev \
    debhelper \
    git \
    devscripts \
    equivs \
    ca-certificates \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /usr/local/bin/uv

WORKDIR /workspace
COPY . /workspace

ARG PYTHON_VERSION=3.14
ENV PYTHON_VERSION=${PYTHON_VERSION}

RUN chmod +x .docker/build-deb.sh && .docker/build-deb.sh

WORKDIR /dpkg
