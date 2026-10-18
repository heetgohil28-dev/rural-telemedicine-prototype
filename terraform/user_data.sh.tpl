#!/bin/bash
set -euxo pipefail
apt-get update -y
apt-get install -y docker.io
systemctl enable --now docker
snap install aws-cli --classic
PW=$(/snap/bin/aws ssm get-parameter --name "${parameter}" --with-decryption --region "${region}" --query Parameter.Value --output text)
docker run -d --name telemed --restart unless-stopped -p 8501:8501 -v telemed-data:/data -e DOCTOR_PASSWORD="$PW" ${image}