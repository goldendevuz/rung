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
