
#!/bin/bash
set -euo pipefail

apt-get update -y
apt-get install -y docker.io
systemctl enable --now docker

docker run -d \
  --name telemed \
  --restart unless-stopped \
  -p 8501:8501 \
  -v telemed-data:/data \
  -e DOCTOR_PASSWORD='${password}' \
  ${image}
