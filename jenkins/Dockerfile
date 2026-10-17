FROM jenkins/jenkins:lts-jdk21
USER root
RUN apt-get update \
 && (apt-get install -y --no-install-recommends docker-cli || apt-get install -y --no-install-recommends docker.io) \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*
RUN docker --version
