DISTRO ?= debian:bookworm
PYTHON_VERSION ?= 3.14
VERSION ?= $(shell tr -d '[:space:]' < convertit/VERSION 2>/dev/null || echo "2.2.6")

build_deb:
	docker pull $(DISTRO)
	docker build -t convertit_deb -f .docker/Dockerfile.debian.builder \
		--build-arg DISTRO=$(DISTRO) \
		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
		--build-arg VERSION=$(VERSION) .
	docker run --name convertit_deb_run -t convertit_deb bash -c "exit"
	docker cp convertit_deb_run:/dpkg ./
	docker stop convertit_deb_run
	docker rm convertit_deb_run

deps:
	docker compose run --remove-orphans --no-deps --rm web bash -c "uv pip compile setup.py -o requirements.txt && uv pip compile requirements-dev.in -o requirements-dev.txt"
