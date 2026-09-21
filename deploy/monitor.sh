#!/bin/bash
ssh -o StrictHostKeyChecking=no -i /home/kai/.ssh/hetzner_key root@188.245.70.100 << 'EOF'
set -e

cd /root/projects/rung

echo "=== Compose PS ==="
docker compose --profile prod ps -a

echo "=== Cloudflared Logs ==="
docker logs rung-cloudflared-1 2>&1 | grep -i "registered tunnel connection" || docker logs rung-cloudflared-1 2>&1 | tail -n 10 | grep -v "TUNNEL_TOKEN"

echo "=== Starting 10 minute monitoring ==="
for i in {1..5}; do
    echo "--- Minute $((i*2)) ---"
    free -m
    docker stats --no-stream
    dmesg -T | grep -i oom | tail -n 5 || true
    if [ $i -lt 5 ]; then
        sleep 120
    fi
done

echo "Monitoring complete."
EOF
