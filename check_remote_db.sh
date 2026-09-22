#!/bin/bash
ssh -o StrictHostKeyChecking=no -i /home/kai/.ssh/hetzner_key root@188.245.70.100 'docker exec rung-postgres_prod-1 psql -U rung -d rung -c " SELECT * FROM alembic_version
