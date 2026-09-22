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
- Live Analytics & DataFast Public Dashboard:
  - DataFast tracking script active in `frontend/index.html`.
  - Topbar `.live` badge dynamically rendered with pulsing green indicator, active visitor counts, daily visit metrics, and direct link to public DataFast dashboard (`https://datafa.st/share/6ab279beba28fc830cd8714b`).
  - `/statistika` route added with live metric summary cards and embedded DataFast analytics dashboard.
  - Prototype footer integrated in `Layout.tsx` with links to Qoidalar, Savol-javob, Shartlar, Maxfiylik, and Jonli statistika.
- Batch Fixes, UX Compacting & DataFast Payment API:
  - Item 1: Empty-slot placeholders (#3 through #10) added to ranked list with "Bu yerni egallang ->" CTA linking to `/qoshish`.
  - Item 2: "Boshqa" category restored in `/qoshish` with dynamic category fetching and live card preview.
  - Item 3: "Invalid Date" safe formatting guard applied across all date displays.
  - Item 4: Click count tracking via `/api/v1/go/{id}` and `/go/{id}` fully operational with daily metrics.
  - Item 5: Sensitive channel usernames and direct URLs hidden on hover, routed through redirect endpoints.
  - Item 6: Wallet balance verified (500 B - 1 B channel deduction = 499 B) with complete ledger audit.
  - Item 7: Wallet checkout description updated with complete payment options: Karta, Click, Payme, Paynet, Alif, AnorBank, Visa/MC.
  - Item 8: Responsive mobile navigation drawer implemented with hamburger button.
  - Item 9: Footer updated with verified active platform links.
  - Item 10: Site density compacted by ~10% (container max-width 960px, refined padding and font scales).
  - Item 11: Demo button removed from production topbar.
  - Item 12: DataFast payment revenue tracking implemented via `POST https://datafa.st/api/v1/payments` with server-side cookie capture (`datafast_visitor_id`), UZS->USD attribution conversion, post-verification triggers in webhook and worker, and fault-tolerant fail-safe error handling.
