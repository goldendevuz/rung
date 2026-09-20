# Rung — Agent Rules (AGENTS.md)

Rung is a paid-ranking directory of products and startups (Uzbekistan first, then global). Rank is bought with the internal currency "B coin". There is NO voting. Surfaces: a React website, and the Telegram bot `@rung_uz_bot` (aiogram) which opens the SAME website as a Telegram Mini App (no separate mini app codebase). Tagline: "Climb one rung." (uz: "Bir pog'ona yuqoriga.")

This file is deliberately short. Details live in `docs/spec/*.md`.

## 0. How to work

- You are the sole engineer. The owner does not write code; he only pastes phase prompts. Work autonomously inside each phase.
- CONTEXT DISCIPLINE: at the start of EVERY session and EVERY phase, read this file, `docs/STATE.md`, `docs/DECISIONS.md` and the spec files named in the phase prompt. Never rely on memory of earlier chats.
- After every meaningful step, update `docs/STATE.md` (done / in progress / next / open issues) so a fresh session can resume without the chat history.
- If something is ambiguous, choose the default in the spec (or the most conservative option), record it in `docs/DECISIONS.md`, and continue. Ask only for real blockers (missing secrets, credentials, irreversible or production-affecting actions).
- Never commit secrets or print them in logs/reports. `.env` is git-ignored; `.env.example` is complete and documented.
- After each phase: run tests and linters, `docker compose up -d --build`, commit (Conventional Commits), push to GitHub `main`, tag `phase-N`, then give the REPORT (section 5).
- Quality bar: production-grade. No placeholder screens, no fake data in real code paths, no TODOs left in money, auth or ranking flows. Features are deliberately NOT artificially limited.

## 1. Stack (fixed)

- Backend: Python 3.12, FastAPI, SQLAlchemy 2 async, Alembic, asyncpg, Pydantic v2, PostgreSQL 16, Redis 7, arq (worker + cron), uv.
- Bot: aiogram 3, long polling for now. The bot never touches the DB; it calls the backend internal API with `INTERNAL_API_TOKEN`.
- Frontend: React 18, Vite, TypeScript strict, Tailwind, TanStack Query, React Router, i18next, framer-motion, zod, pnpm.
- Infra: Docker Compose (profiles `dev`, `prod`, `tunnel`), Caddy as the single reverse proxy (`/api` -> backend, `/` -> frontend), optional cloudflared.
- One monorepo `rung`: `backend/ bot/ frontend/ deploy/ docs/`.

## 2. Non-negotiable invariants

- Money: integer units only (1 B = 1000 units, BIGINT), never floats. Balance never negative (CHECK). Ledger is append-only (DB trigger blocks UPDATE/DELETE). Every money endpoint needs an `Idempotency-Key`.
- Ranking: each period type is a separate market; rank is DERIVED from `paid_units DESC, entered_at ASC`, never stored. Claiming happens in one transaction under a board row lock. Concurrency tests are mandatory.
- Tabs and counters are computed live from the database; no static datasets or hardcoded period lists. A period tab shows only if it has at least one active entry.
- SOFT DELETE everywhere (`deleted_at`, `deleted_by`, `delete_reason`). No hard deletes in application code. Real data is never lost. The word "archive/arxiv" is never shown in the UI.
- Payments store provider, currency, provider amount and charge id from day one; the UI shows only B amounts (flag `SHOW_PAYMENT_DETAILS`, default false).
- Security: validate all input, rate limit, SSRF-safe URL fetching, HMAC-verified Telegram initData, admin allowlist re-checked on every admin action and audited, no secrets in images, DB/Redis never public in prod.
- UI: must look and feel premium and be its own product. Outbid.lol is a quality benchmark only; never copy its markup, classes, copy, colors, icons or layout.
- Language: UI is Uzbek only until v1 is complete (keys prepared for en, then ru).

## 3. Spec index (read what the phase prompt names)

| File | Covers |
|---|---|
| `docs/spec/01-money-ranking-periods.md` | money rules, ranking formulas, periods, rollover, auto-renew |
| `docs/spec/02-payments-auth.md` | Stars, Paynet, refund (beta), auth, linking, dev login |
| `docs/spec/03-listings-clicks-data-api.md` | listings, moderation, click stats, data model, API |
| `docs/spec/04-bot-and-engineering.md` | bot behavior, tests, CI, Docker, security rules |
| `docs/spec/05-ui-ux.md` | design identity, palette, screens, motion, i18n |

## 4. Environments

- Local: WSL Ubuntu 22.04, repo at `/home/kai/projects/rung`. GitHub: private repo `rung` under `goldendevuz` (use `gh`; if unauthenticated, tell the owner exactly what to run).
- Env vars (all in `.env.example`): `ENV`, `POSTGRES_*`, `REDIS_URL`, `SECRET_KEY`, `INTERNAL_API_TOKEN`, `BOT_TOKEN`, `BOT_USERNAME=rung_uz_bot`, `ADMIN_TG_IDS=557407324`, `GOOGLE_CLIENT_ID/SECRET`, `PUBLIC_BASE_URL`, `WEBAPP_URL`, `DEV_AUTH`, `SHOW_PAYMENT_DETAILS=false`, `SEED_DEMO`, `TZ=Asia/Tashkent`.
- No domain yet. Browser testing: `http://localhost` (local) or the VPS IP over HTTP. Telegram Mini Apps need HTTPS: use a cloudflared quick tunnel (`tunnel` profile, temporary URL) for testing; `rung.uz` and a named cloudflared tunnel come later.
- Production target (deploy phase only, after explicit owner approval): Hetzner Ubuntu VPS, repo cloned into `/root/projects/rung`, `prod` profile.

## 5. Definition of done and REPORT

A phase is done when tests and lint pass, the stack starts with one command, everything is pushed, and docs (`STATE.md`, `DECISIONS.md`, `RUNBOOK.md`) are updated. End every phase with a REPORT: what was built; how to run it; local URLs; a step-by-step manual test script; env vars the owner must fill in; known gaps; decisions taken; and the exact question(s), if any, needed before the next phase.
