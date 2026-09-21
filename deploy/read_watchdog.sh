#!/bin/bash
ssh -o StrictHostKeyChecking=no -i /home/kai/.ssh/hetzner_key root@188.245.70.100 << 'EOF'
cat /root/projects/exploit-server/scripts/watchdog.sh
EOF
