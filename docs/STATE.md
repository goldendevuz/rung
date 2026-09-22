# Rung State

**Current Slice**: S4 (inPAY.uz automatic UZS top-up)
**Status**: In Progress / Verification

## Components
- Backend (FastAPI, SQLAlchemy, PostgreSQL, asyncpg): Stable, S4 endpoints added (`/wallet/topup`, `/payments/inpay/callback`, `/wallet/topup/{order_id}`, arq reconciliation)
- Frontend (React, Vite, TanStack Query): Wallet page (`/hamyon`, `/wallet`) implemented with polling, amount chips, Topbar balance link
- Bot (aiogram): Stable

## Done
- S0: Skeleton and Docker configuration
- S1: Backend logic, category names/counts, money math fixes, pagination, stats, visual diffs and tests.
- S4: inPAY.uz integration:
  - Database models `TopupOrder` and `LedgerEntry` with unique `order_id` / `ref_id`.
  - InPAY service with Redis-cached Bearer token (~23h TTL) and 401 retry.
  - Endpoints: `POST /api/v1/wallet/topup`, `POST /api/v1/payments/inpay/callback`, `GET /api/v1/wallet/topup/{order_id}`.
  - Arq reconciliation worker running every 1 minute.
  - Frontend `/hamyon` page with quick-select B amounts, return polling, and balance display.
- Listing Logo Upload & Auto-Fetch:
  - `logo_url` column added to `listings` table with Alembic migration `cccc00000001_add_logo_url_to_listings`.
  - Backend `POST /api/v1/uploads/logo` with Pillow 512px WebP re-encoding and safe static file serving.
  - Public channel Telegram avatar auto-fetch on creation/sync if custom logo is not uploaded.
  - `PATCH /api/v1/users/me/listings/{id}` for updating channel logo, name, and description.
  - `AddListingModal.tsx` now has a dedicated, modern image upload input with preview, change, and remove controls.
  - `ListingRow.tsx`, `Listing.tsx`, and `Profile.tsx` updated to render logos with smooth fallback to gradient initials.


