#!/bin/bash
ssh -i /home/kai/.ssh/hetzner_key -o StrictHostKeyChecking=no root@188.245.70.100 "docker exec -i rung-postgres_prod-1 psql -U rung -d rung" << 'EOF'
SELECT id, telegram_id, username, balance FROM users WHERE telegram_id = 557407324;
SELECT * FROM ledger_entries WHERE user_id = (SELECT id FROM users WHERE telegram_id = 557407324);
SELECT * FROM topup_orders WHERE user_id = (SELECT id FROM users WHERE telegram_id = 557407324);
EOF
