# Rung State

**Current Slice**: S1
**Status**: Accepted

## Components
- Backend (FastAPI, SQLAlchemy, PostgreSQL, asyncpg): Stable
- Frontend (React, Vite, TanStack Query): Build and Tests Passing
- Bot (aiogram): Stub

## Done
- S0: Skeleton and Docker configuration
- S1: Backend logic, category names/counts, money math fixes, pagination, stats, visual diffs and tests. Finalized UI details.

## Routes
- **(a) Static content**: `/haqida`, `/qoidalar`, `/kirish` (text present in prod, populated from prototype)
  - Screenshots: `haqida.png`, `qoidalar.png`, `kirish.png`
- **(b) Data-driven**: `/`, `/kunlik`, `/kategoriyalar`, `/p/<slug>` (404 for non-existing)
  - Empty states show friendly Uzbek messages (e.g., "Hali yopilgan kunlik reyting yo'q" for `/kunlik`, "Hali kategoriyalar qo'shilmagan" for `/kategoriyalar`).
  - Screenshots: `home.png`, `kunlik.png`, `kategoriyalar.png`, `listing-404.png`, `404.png`
- **(c) Planned for later slices**: `/qoshish` and auth buttons in `/kirish`
  - Visibly disabled with short note "Tez orada".
  - Screenshots: `qoshish.png`, `kirish.png`
