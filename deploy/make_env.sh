#!/bin/bash
ssh -o StrictHostKeyChecking=no -i /home/kai/.ssh/hetzner_key root@188.245.70.100 << 'EOF'
cat << 'INNEREOF' > /root/projects/rung/.env
ENV=prod
TZ=Asia/Tashkent
DEV_AUTH=false
SEED_DEMO=false
SHOW_DEMO_BUTTON=true
STARS_ENABLED=true
PUBLIC_BASE_URL=https://rung.shats.uz
WEBAPP_URL=https://rung.shats.uz
SECRET_KEY=$(openssl rand -hex 32)
INTERNAL_API_TOKEN=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 24)
BOT_TOKEN=
TUNNEL_TOKEN=
INNEREOF
chmod 600 /root/projects/rung/.env
EOF
