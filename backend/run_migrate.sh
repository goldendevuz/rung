#!/bin/bash
cat drop.sql | docker compose -f ../docker-compose.yml exec -T postgres psql -U rung -d rung
docker compose -f ../docker-compose.yml exec -T backend alembic upgrade head
