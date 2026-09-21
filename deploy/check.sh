#!/bin/bash
ssh -o StrictHostKeyChecking=no -i /home/kai/.ssh/hetzner_key root@188.245.70.100 << 'EOF'
set -e
cd /root/projects/rung
cat docker-compose.yml | grep -A 10 "postgres_prod:"
EOF
