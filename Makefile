.PHONY: up down logs test lint seed migrate build shell-backend shell-bot

COMPOSE = docker compose

up:
	$(COMPOSE) --profile dev up -d --build

down:
	$(COMPOSE) --profile dev --profile prod --profile tunnel down

logs:
	$(COMPOSE) logs -f --tail=100

migrate:
	$(COMPOSE) run --rm migrate

seed:
	$(COMPOSE) exec backend python -m app.db.seed

test:
	$(COMPOSE) exec backend pytest -x -q

lint:
	$(COMPOSE) exec backend ruff check . && mypy app

prod-up:
	$(COMPOSE) --profile prod up -d --build

shell-backend:
	$(COMPOSE) exec backend bash

shell-bot:
	$(COMPOSE) exec bot bash
