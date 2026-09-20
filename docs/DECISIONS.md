# Rung — Architectural Decisions

> Append-only. Format: date, ID, decision, rationale.

## 2026-09-20 — S0

### D001: Separate service names per profile (postgres vs postgres_prod)
Docker Compose does not cleanly support per-profile port overrides.
Separate service names make localhost port exposure explicit (dev only).

### D002: Bot stays alive when BOT_TOKEN is empty
Bot container must not crash. It logs a warning and loops on heartbeat.
Required so S0 acceptance gate can verify all containers are healthy.

### D003: First Alembic migration is empty
S0 establishes the migration pipeline only. Tables added in S1.

### D004: Caddy proxies /* to Vite dev server in dev profile
HMR WebSockets pass through Caddy's reverse_proxy natively.

### D005: CORS_ORIGINS is a comma-separated env var
Allows adding tunnel hostnames without code changes.

### D006: ENABLED_LISTING_KINDS=channel (v1 only)
Other kinds reserved but not creatable in v1 per spec S0 section 6.

## 2026-09-20 — S0 fixes

### D007: Frontend uses npm install instead of pnpm for Docker builds
pnpm 9+ introduced ERR_PNPM_IGNORED_BUILDS which blocks esbuild's postinstall
script in non-interactive environments (Docker). The fix is documented in
frontend/Dockerfile.dev: npm installs packages, pnpm (installed globally) runs
the dev/build scripts (it finds node_modules normally). pnpm is still the
developer-facing tool; npm is only used inside Docker image builds.

### D008: Caddy healthcheck uses `caddy validate` not admin API
The caddy admin API (localhost:2019) is not enabled in the dev Caddyfile by
default. `caddy validate --config /etc/caddy/Caddyfile` is a zero-dependency
check that verifies the config is loadable and the server is in a working state.

### D009: Postgres and Redis dev ports bound to 127.0.0.1 only
Publishing on 0.0.0.0 exposes dev DB/cache to the local network. Changed to
127.0.0.1:5432:5432 and 127.0.0.1:6379:6379 per security requirement.
