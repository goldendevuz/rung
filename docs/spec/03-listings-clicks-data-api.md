# Listings, Clicks and Stats, Data Model, API

> Part of the Rung spec. Source of truth together with AGENTS.md. Section numbers below are historical; ignore the numbering.

## 8. Listings and moderation

- Fields: name (<=60), tagline (<=90), description (<=600, plain text), url (https only, normalized, unique), category (seeded list: AI & Agents, SaaS, Marketing, Dev Tools, Education, Fintech, E-commerce, Games, Mobile, Productivity, Design, Other), logo (server-side fetched favicon/og image OR upload validated and re-encoded to WebP 512px), slug, owner, status (`active`, `hidden`, soft-deleted).
- URL metadata auto-fetch (title, description, icon) MUST be SSRF-safe: resolve DNS, block private/loopback/link-local/metadata IPs, limit redirects, size and time.
- Publishing is instant. Admins can hide a listing with a reason (owner is notified). Domain/keyword blocklist. "Report" button for users. Hiding does not auto-refund; admin decides manually.

## 9. Clicks and verified statistics

- All outbound clicks go through `/go/{slug}` (server-side 302 to the product URL with `utm_source=rung`). The outbound link in the UI is rendered `rel="noopener sponsored"`.
- Store every click as a raw append-only `click_events` row with a verdict (`human`, `suspect`, `bot`); never discard raw data so rules can be re-run.
- Bot filtering layers with a score: user-agent list and empty UA; datacenter/hosting ASN via GeoLite2 (optional file, degrade gracefully); signed short-lived click token issued when the page renders (missing/invalid token = suspect); CSS-hidden honeypot link; per-IP/visitor rate limits; a lightweight JS "human signal" (pointer/scroll/touch) sent with the click.
- Visitor identity: first-party cookie `visitor_id` (UUID, 1 year) plus fallback `hash(ip/24 + UA + daily salt)`.
- Metrics per listing: raw clicks (internal only), verified clicks, UNIQUE VISITORS (distinct visitor_id among verified clicks) as the headline number, returning visitors, repeat clicks (same visitor within 24 h is stored but not counted). Public UI shows unique verified visitors only. Owners see a dashboard with the funnel raw -> verified -> unique.
- Processing: `/go` responds immediately, pushes the event to a Redis stream, the worker classifies and writes to Postgres, then rolls up into `listing_stats_daily`. Dashboards read the rollups only.

## 10. Data model (minimum)

`users, identities, refresh_tokens, categories, listings, boards, board_entries, wallets, ledger_entries, payments, topup_requests, refunds, settings, click_events, listing_stats_daily, reports, blocklist, notifications, audit_log`.

Conventions: BIGINT identity PK plus public UUID; `created_at`, `updated_at`; ALL business tables are SOFT-DELETE (`deleted_at`, `deleted_by`, `delete_reason`). No hard deletes anywhere in application code (add a test that greps the codebase for `DELETE FROM` and `.delete(` outside migrations/tests). Timestamps in UTC; period boundaries computed in `Asia/Tashkent`. Sensible indexes, including a partial index on active entries `(board_id, paid_units DESC, entered_at)`.

## 11. API (prefix `/api/v1`, OpenAPI documented)

auth (google, telegram webapp, link, logout, refresh), me, listings (CRUD, metadata fetch, my listings), categories, boards (`/boards/tabs` for live tab counts, `/boards/{type}/current`, previous results), quote, claim, auto-renew settings, wallet, ledger history, payments (history, stars invoice link, paynet requests), stats (listing owner dashboard, public), `/go/{slug}`, reports, admin (moderation, payments, refunds, top-ups, settings, audit) protected by admin allowlist, internal (`/internal/*` for the bot, token-protected, not exposed by Caddy). Cursor pagination everywhere. Consistent error format with machine-readable codes (all user-facing text is translated in the frontend).

