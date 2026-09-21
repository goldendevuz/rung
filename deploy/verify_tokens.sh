#!/bin/bash
ssh -o StrictHostKeyChecking=no -i /home/kai/.ssh/hetzner_key root@188.245.70.100 << 'EOF'
awk -F= '/^(BOT_TOKEN|TUNNEL_TOKEN)=/{print $1, ($2==""?"EMPTY":"set")}' /root/projects/rung/.env
EOF
