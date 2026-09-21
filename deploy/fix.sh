#!/bin/bash
ssh -o StrictHostKeyChecking=no -i /home/kai/.ssh/hetzner_key root@188.245.70.100 << 'EOF'
set -e
cd /root/projects/rung
source .env
sed -i 's/^DATABASE_URL=.*//g' .env
echo "DATABASE_URL=postgresql+asyncpg://rung:${POSTGRES_PASSWORD}@postgres_prod:5432/rung" >> .env
# Let's verify it does not contain ${POSTGRES_PASSWORD} literally
grep DATABASE_URL .env
docker compose --profile prod down
docker compose --profile prod up -d
EOF
