#!/bin/bash
ssh -o StrictHostKeyChecking=no -i /home/kai/.ssh/hetzner_key root@188.245.70.100 << 'EOF'
grep -E '^(ENV|DEV_AUTH|SEED_DEMO|SHOW_DEMO_BUTTON)=' /root/projects/rung/.env
echo '---'
free -m
echo '---'
df -h /
echo '---'
docker ps
EOF
