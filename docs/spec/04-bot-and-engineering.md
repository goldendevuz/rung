# Bot Behavior, Engineering and Security Rules

> Part of the Rung spec. Source of truth together with AGENTS.md. Section numbers below are historical; ignore the numbering.

## 12. Bot behavior

- `/start` (with optional `link_` / `topup_` payloads), persistent menu button that opens the Web App, `/balance`, `/topup` (Stars packages + Paynet instructions), `/help`.
- Admin commands (ID allowlist): `/admin` panel with inline buttons — recent Stars payments with a Refund button, pending Paynet requests with Approve/Reject, hide/unhide listing, stats.
- User notifications: top-up success, claim success, outbid (someone took your rank), renewal results.
- Uzbek texts first, all strings in one i18n module (uz -> en -> ru order).

## 14. Engineering and security rules

- Strict typing (mypy or pyright, TypeScript strict), ruff, eslint, prettier, pre-commit. Tests: pytest (ledger, ranking, concurrency, auth, refund state machine, period rollover with a frozen clock), Vitest for logic, Playwright smoke tests.
- GitHub Actions CI: lint, type-check, tests, Docker build.
- Security: input validation everywhere, rate limiting (Redis), strict CORS, secure headers via Caddy, upload validation, SSRF protection, webhook/secret checks, no secrets in images, DB and Redis NOT published to the host in prod, least-privilege DB user for the app, structured JSON logs with request ids, `/healthz` and `/readyz`, audit log for all money and admin actions.
- Docker: multi-stage images, non-root users, healthchecks, named volumes, `restart: unless-stopped`, migrations run as a one-shot service before the backend starts.
- Seed script (idempotent) creates categories, settings and DEMO data only when `SEED_DEMO=true`.



## Frontend build tooling note

**Package manager in Docker:** 
pm install is used inside rontend/Dockerfile.dev
(and will be used in the prod Dockerfile) instead of pnpm install. This is because
pnpm 9+ introduced ERR_PNPM_IGNORED_BUILDS which blocks esbuild postinstall in
non-interactive environments. See DECISIONS.md D007.

The committed lockfile is rontend/package-lock.json.
Developer-facing commands (outside Docker) may use pnpm or npm interchangeably.
