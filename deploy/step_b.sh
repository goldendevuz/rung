#!/bin/bash
ssh -o StrictHostKeyChecking=no -i /home/kai/.ssh/hetzner_key root@188.245.70.100 << 'EOF'
mkdir -p /root/backups/rung-d1
crontab -l > /root/backups/rung-d1/crontab-before.txt
crontab -l | sed 's|^\(0 3 .*/root/projects/qoraqozon/scripts/backup_db.sh\)|#D1-DISABLED \1|g' | \
sed 's|^\(\*/5 .*/root/projects/qoraqozon/scripts/healthcheck_alert.sh\)|#D1-DISABLED \1|g' | \
sed 's|^\(\*/30 .*/root/projects/exploit-server/scripts/watchdog.sh\)|#D1-DISABLED \1|g' > /tmp/newcron
crontab /tmp/newcron
docker stop 3dc86fe95456 aa208a68d377 8dcc13c65b89 57dff2ed6f79

# Update .env
sed -i 's/^BOT_TOKEN=.*/BOT_TOKEN=8836766632:AAEChSguGOM9IaXS8pGdc-0hC6UysL3VdsU/' /root/projects/rung/.env
sed -i 's/^TUNNEL_TOKEN=.*/TUNNEL_TOKEN=eyJhIjoiMTg3YzQxNGI2ZDNjY2I0ODQxNjk0MmQ1NDM1MTQ2ZjAiLCJ0IjoiNDRjMGM2ODMtNmNjYy00ZGUyLWIwMzgtMGFlYjYyMzEyMzFhIiwicyI6Ik1ESXdaV1ZpWWpJdE0ySTBPQzAwWlRrM0xUazFZV1l0WlRZM016UTNaVFEwTVRSbCJ9/' /root/projects/rung/.env

echo '--- CRONTAB AFTER ---'
crontab -l
echo '--- DOCKER PS AFTER ---'
docker ps
EOF
