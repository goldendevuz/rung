.PHONY: up down logs test lint seed migrate build shell-backend shell-bot shots

COMPOSE  = docker compose
PW_VER   = 1.46.0
SHOTS_DIR = docs/screenshots/s1

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

shots:
	@mkdir -p $(SHOTS_DIR)
	docker run --rm --network host \
		-v $(PWD)/deploy/shots/shots.js:/tmp/shots.js:ro \
		-v $(PWD)/$(SHOTS_DIR):/shots \
		mcr.microsoft.com/playwright:v$(PW_VER)-jammy \
		bash -c "mkdir /tmp/pw && cd /tmp/pw && \
		  npm init -y -q 2>/dev/null && \
		  npm install @playwright/test@$(PW_VER) --no-package-lock -q && \
		  cp /tmp/shots.js . && node shots.js"
	@echo "Saved: $(SHOTS_DIR)/desktop-1440x900.png, $(SHOTS_DIR)/mobile-390x844.png"

smoke:
	docker run --rm --network host \
		-v $(PWD)/deploy/shots/smoke.js:/tmp/smoke.js:ro \
		mcr.microsoft.com/playwright:v$(PW_VER)-jammy \
		bash -c "mkdir -p /tmp/pw && cd /tmp/pw && \
		  npm init -y -q 2>/dev/null && \
		  npm install @playwright/test@$(PW_VER) --no-package-lock -q && \
		  cp /tmp/smoke.js . && node smoke.js"
