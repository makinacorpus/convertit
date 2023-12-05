build_deb:
	docker pull $(DISTRO)
	docker build -t convertit_deb -f .docker/Dockerfile.debian.builder --build-arg DISTRO=$(DISTRO) .
	docker run --name convertit_deb_run -t convertit_deb bash -c "exit"
	docker cp convertit_deb_run:/dpkg ./
	docker stop convertit_deb_run
	docker rm convertit_deb_run
