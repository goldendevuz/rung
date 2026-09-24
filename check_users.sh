ssh -i /home/kai/.ssh/hetzner_key -o StrictHostKeyChecking=no root@188.245.70.100 "docker exec -i rung-postgres_prod-1 psql -U rung -d rung -c 'SELECT id, telegram_id, balance FROM users;'"
