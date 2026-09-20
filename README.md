# Rung

**Bir pog'ona yuqoriga.** — O'zbek Telegram kanallarining ochiq reytingi.

Rung — reklama beruvchilar uchun Telegram kanallar katalogi. Reytingdagi o'rin
ichki valyuta **B coin** bilan sotib olinadi. Ovoz yo'q — faqat bozor.

## Tezkor ishga tushirish

```bash
cp .env.example .env   # .env ni to'ldiring
make up                # docker compose --profile dev up -d --build
```

Ochilgan manzillar:
- Web UI: http://localhost
- Backend API: http://localhost/api/v1/ping
- Healthcheck: http://localhost/healthz

## Stack

| Layer     | Tech |
|-----------|------|
| Backend   | Python 3.12, FastAPI, SQLAlchemy 2, Alembic, asyncpg, arq |
| Bot       | aiogram 3, long polling |
| Frontend  | React 18, Vite, TypeScript strict, Tailwind, TanStack Query |
| Infra     | Docker Compose (profiles: dev, prod, tunnel), Caddy, PostgreSQL 16, Redis 7 |

## Papkalar

```
backend/    FastAPI ilovasi va worker
bot/        Telegram bot (aiogram 3)
frontend/   React + Vite
deploy/     Caddy, Dockerfile configs
docs/       Spec, state, decisions, screenshots
```

## Rivojlantirish qo'llanmasi

Batafsil: `docs/spec/`, `docs/STATE.md`, `docs/DECISIONS.md`.
