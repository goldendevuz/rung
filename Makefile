.PHONY: up down logs test lint seed migrate build shell-backend shell-bot shots audit

COMPOSE  = docker compose
PW_VER   = 1.46.0
SHOTS_DIR = docs/screenshots/s1

up: pick-ports
	$(COMPOSE) --profile dev up -d --build

pick-ports:
	@bash scripts/pick-ports.sh

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

prod-up: check-demo
	$(COMPOSE) --profile prod up -d --build

check-demo:
	@if grep -q 'ENV=prod' .env && grep -q 'PUBLIC_BASE_URL=https://rung.uz' .env && grep -q 'SHOW_DEMO_BUTTON=true' .env; then \
		echo "ERROR: Demo button is enabled on final production URL (rung.uz). Remove SHOW_DEMO_BUTTON=true."; exit 1; \
	fi

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

audit:
	@mkdir -p deploy/audit/shots
	docker run --rm --network host \
		-e BASE=$(or $(BASE),https://rung.shats.uz) \
		-e EXPECT_DEMO=$(or $(EXPECT_DEMO),true) \
		-v $(PWD)/deploy/audit/audit.mjs:/tmp/audit.mjs:ro \
		-v $(PWD)/deploy/audit/shots:/tmp/pw/shots \
		mcr.microsoft.com/playwright:v$(PW_VER)-jammy \
		bash -c "mkdir -p /tmp/pw && cd /tmp/pw && \
		  npm init -y -q 2>/dev/null && \
		  npm install playwright@$(PW_VER) --no-package-lock -q && \
		  cp /tmp/audit.mjs . && node audit.mjs"

