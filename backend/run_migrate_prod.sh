#!/bin/bash
cat drop.sql | docker compose -f ../docker-compose.yml exec -T postgres_prod psql -U rung -d rung
docker compose -f ../docker-compose.yml exec -T backend_prod alembic upgrade head
