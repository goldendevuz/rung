#!/bin/bash
ssh -o StrictHostKeyChecking=no -i /home/kai/.ssh/hetzner_key root@188.245.70.100 << 'EOF'
set -e
cd /root/projects/rung

# Fix .env variables by generating actual random strings
SECRET_KEY=$(openssl rand -hex 32)
INTERNAL_API_TOKEN=$(openssl rand -hex 32)
# base64 can contain + and /, so use hex for postgres password to avoid url encoding issues
POSTGRES_PASSWORD=$(openssl rand -hex 24)

sed -i "s/^SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env
sed -i "s/^INTERNAL_API_TOKEN=.*/INTERNAL_API_TOKEN=${INTERNAL_API_TOKEN}/" .env
sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${POSTGRES_PASSWORD}/" .env
sed -i "s|^DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://rung:${POSTGRES_PASSWORD}@postgres_prod:5432/rung|" .env

echo "=== Shutting down ==="
docker compose --profile prod down

echo "=== Removing old postgres volume ==="
docker volume rm rung_postgres_data || true

echo "=== Starting up ==="
docker compose --profile prod up -d
EOF
