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
