# Architectural Decisions

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2 async, Alembic, asyncpg, PostgreSQL 16.
- **Frontend**: React, Vite, TanStack Query.
- **Bot**: aiogram.
- **Deployment**: Docker Compose, Caddy for reverse proxy and HTTPS.
- **S1 Fixes**:
  - `PAGE_SIZE` increased to 20 to accommodate prototype designs (14 items on the first page).
  - Typescript unused imports fixed to ensure strict builds in `npm run build`.
  - Smoke tests implemented via Playwright asserting network and visual logic (>=14 items on home).
  - Screenshots diffing automated via pixelmatch.
