# Rung — Project State

> Updated after each phase. Read this at the start of every session.

## Current Phase: S0 — Repo skeleton

### Status: COMPLETE

### Completed
- [x] git init -b main
- [x] .gitignore
- [x] Full directory structure
- [x] .env.example (all vars documented)
- [x] .env (generated secrets, BOT_TOKEN set)
- [x] docker-compose.yml (profiles: dev, prod, tunnel; all healthchecks)
- [x] Backend: FastAPI + /healthz + /readyz + /api/v1/ping
- [x] Backend: Alembic + empty first migration
- [x] Backend: Dockerfile (non-root)
- [x] Bot: aiogram 3 (idle if no token, heartbeat)
- [x] Frontend: Vite + React + TypeScript
- [x] Caddy: dev + prod configs
- [x] Makefile
- [x] GitHub Actions CI
- [x] pre-commit config
- [x] README.md
- [x] docs/STATE.md + DECISIONS.md

### Acceptance Gate Results
- See REPORT at the end of S0 session.

### Next Phase: S1
Build UI screens: home, daily, categories, rules, add-channel, about, login,
claim modal — using prototype as design authority.
