#!/bin/bash
ssh -o StrictHostKeyChecking=no -i /home/kai/.ssh/hetzner_key root@188.245.70.100 << 'EOF'
set -e

# Load current POSTGRES_PASSWORD
source /root/projects/rung/.env

if ! grep -q "^DATABASE_URL=" /root/projects/rung/.env; then
  echo "DATABASE_URL=postgresql+asyncpg://rung:${POSTGRES_PASSWORD}@postgres_prod:5432/rung" >> /root/projects/rung/.env
fi

cd /root/projects/rung
echo "=== Building backend_prod ==="
docker compose --profile prod build backend_prod

echo "=== Building worker_prod ==="
docker compose --profile prod build worker_prod

echo "=== Building bot_prod ==="
docker compose --profile prod build bot_prod

echo "=== Building frontend ==="
# Frontend doesn't have a Dockerfile.prod. It is mounted into caddy.
docker run --rm -v /root/projects/rung/frontend:/app -w /app node:20 bash -c "npm install && NODE_OPTIONS=--max-old-space-size=1024 npm run build"
EOF
