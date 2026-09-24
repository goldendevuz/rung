#!/bin/bash
ssh -i /home/kai/.ssh/hetzner_key -o StrictHostKeyChecking=no root@188.245.70.100 "grep -i 'DATAFAST' /root/projects/rung/.env || echo 'NOT_FOUND'"
