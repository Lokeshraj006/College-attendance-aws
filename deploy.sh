#!/usr/bin/env bash
# =============================================================================
#  deploy.sh – Bootstrap an Ubuntu 22.04/24.04 EC2 instance and launch the app
#
#  Run once on a fresh instance:
#      chmod +x deploy.sh && sudo ./deploy.sh
#
#  Prerequisites on EC2:
#    • Ubuntu 22.04 or 24.04 LTS
#    • Security Group:  inbound TCP 80 OPEN,  TCP 22 OPEN (your IP only)
#                       TCP 3306 NOT OPEN,    TCP 8000 NOT OPEN
# =============================================================================
set -euo pipefail

# ── 1. System update ──────────────────────────────────────────────────────────
echo "==> Updating system packages..."
apt-get update -y && apt-get upgrade -y

# ── 2. Install Docker Engine ──────────────────────────────────────────────────
echo "==> Installing Docker..."
apt-get install -y ca-certificates curl gnupg lsb-release

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Allow the default ubuntu user to run docker without sudo
usermod -aG docker ubuntu || true

# ── 3. Clone / copy the project ───────────────────────────────────────────────
APP_DIR="/opt/college-attendance"
echo "==> Setting up project at ${APP_DIR}..."
mkdir -p "${APP_DIR}"

# If running from the repo root, just copy files; otherwise git clone:
# git clone https://github.com/YOUR_USER/College-attendance-aws.git "${APP_DIR}"
# ↑ Uncomment above and remove the cp block below when using git

cp -r . "${APP_DIR}/"
cd "${APP_DIR}"

# ── 4. Create .env if it doesn't exist ───────────────────────────────────────
if [ ! -f .env ]; then
  echo "==> .env not found – creating from .env.example"
  cp .env.example .env
  echo ""
  echo "⚠  IMPORTANT: Edit ${APP_DIR}/.env and set a strong DB_PASSWORD"
  echo "   and correct FRONTEND_ORIGINS before proceeding."
  echo "   Run:  nano ${APP_DIR}/.env"
  echo ""
  read -rp "Press ENTER once you have edited .env to continue, or Ctrl+C to abort..."
fi

# ── 5. Build and start containers ─────────────────────────────────────────────
echo "==> Building images and starting services..."
docker compose up -d --build

# ── 6. Show running containers and open ports ─────────────────────────────────
echo ""
echo "=== Running containers ==="
docker compose ps

echo ""
echo "=== Port exposure summary ==="
echo "  Port  80  → PUBLIC  (nginx: React SPA + /api reverse-proxy)"
echo "  Port 8000 → PRIVATE (FastAPI – internal Docker network only)"
echo "  Port 3306 → PRIVATE (MySQL – internal Docker network only)"
echo ""
echo "  Verify with:  sudo ss -tlnp | grep -E '80|8000|3306'"
echo ""
echo "✅ Deployment complete – visit http://$(curl -s ifconfig.me)"

