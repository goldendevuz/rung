# Architectural Decisions

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2 async, Alembic, asyncpg, PostgreSQL 16.
- **Frontend**: React, Vite, TanStack Query.
- **Bot**: aiogram.
- **Deployment**: Docker Compose, Caddy for reverse proxy and HTTPS.
- **S1 Fixes**:
  - `PAGE_SIZE` reverted to 12 as per spec and prototype.
  - Money calculations strictly use integer units (1 B = 1000 units) to prevent string math bugs.
  - Categories fetch and display `name_uz` and active `listing_count`.
  - Stats API (`/api/v1/stats/public`) accurately returns real totals: `total_listings` (active listings/channels), `total_paid_units` (sum of active paid units), `visits_today` (real verified views).
  - Test suite expanded for rank ties, quotes math, pagination and boundary logic.

## S2 Decisions (2026-09-21)

### Feature flags — payment providers and auth
- `STARS_ENABLED=false` — Telegram Stars payment kept behind flag, not deleted. Will be re-enabled when decided.
- `PAYNET_ENABLED=false` — Paynet (manual UZS) kept behind flag, not deleted. Will be re-enabled when decided.
- `GOOGLE_AUTH_ENABLED=false` — Google OAuth kept behind flag. The login page hides the Google button when false.

### Payment provider — Checkout.uz
- Payments will be automatic UZS through **Checkout.uz** as specified in `docs/spec/06-checkout-uz.md`.
- Implemented in a later slice (not yet coded).
- `PAYMENT_PROVIDER_TEXT` env var (default `"to'lov tez orada"`) is returned by `GET /api/v1/public-config` and rendered in the hero price note and claim sheet.

### Authentication — Telegram only
- Auth is Telegram-only:
  1. **Mini App**: `initData` HMAC validation (unchanged).
  2. **Website login via bot deep link**: `https://t.me/rung_uz_bot?start=login_<one-time-token>` — user clicks in browser → Telegram opens bot → bot confirms → site receives session cookie.
- The login page shows only the Telegram button (Google is hidden while `GOOGLE_AUTH_ENABLED=false`).
- Google OAuth code stays in the codebase behind the flag; not deleted.

### Seed split
- `seed_reference()` — seeds 13 categories + default settings. Always runs on backend startup.
- `seed_demo()` — seeds demo listings and boards. Only runs when `SEED_DEMO=true`.
- `make seed` / `run_seed()` kept for backward compat (runs both).

### OG meta tags
- `og:url` and `og:image` in `frontend/index.html` now use `%VITE_PUBLIC_BASE_URL%` (Vite substitution at build/serve time). No hardcoded `rung.uz`.

### Demo button
- `SHOW_DEMO_BUTTON` env var (default `false`) controls visibility of the Demo button in the topbar.
- Value is returned by `GET /api/v1/public-config` — frontend fetches it at runtime; no build-time VITE_ env var needed.

### Hero and claim sheet copy
- Neither mentions Stars nor Paynet. Payment provider line comes from `public-config.payment_provider_text`.
- Rules page: Stars/Paynet-specific sentences removed from the "To'lovdan keyin" section.

## S4 Decisions (2026-09-22)

### inPAY.uz Automatic UZS Top-Up
- Replaces Checkout.uz with **inPAY.uz** hosted checkout for automatic UZS payments (`1 B = 1000 UZS`).
- Flow: Client calls `POST /api/v1/wallet/topup`, backend requests bearer token from inPAY (`GET /authorization/`, cached in Redis for ~23h), calls `POST /create/` with `callback_url` and `return_url`, stores pending `TopupOrder`, and returns `{pay_url, order_id}`.
- Hosted checkout only (`pay_url`). Never calls `/api/v1/cardsystem/*`.
- Webhook verification: `POST /api/v1/payments/inpay/callback` receives untrusted webhook. Backend verifies server-to-server via `GET /api/v1/transactions/?order_id=`. Wallet is credited only if status is `"success"` and amount matches.
- Idempotency & Concurrency: DB unique constraint on `ref_id` in `LedgerEntry` prevents duplicate credit. Topup order row lock ensures state transitions (`pending` -> `completed`).
- Reconciliation: arq worker runs `reconcile_inpay_topups` cron every minute checking pending orders older than 2 minutes against inPAY.
- Polling: `GET /api/v1/wallet/topup/:order_id` provides authoritative DB status for frontend polling on return.

