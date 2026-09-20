First read AGENTS.md, docs/STATE.md, docs/DECISIONS.md and docs/prompts/S1.md.

S1 FIX — S1 is NOT accepted. Do ONLY the fixes below, in order, and show REAL command output for each item (not summaries). Do not add features. Do not move or delete the existing s1 tag; when I accept, you will create s1-final.

0. THE UI IS NOT VISIBLE. Opening http://localhost in the browser still shows the old S0 hello page ("Rung / Bir pog'ona yuqoriga.") instead of the ported prototype UI, although the curl status checks return 200 (a hello page also returns 200). Find the root cause (stale image, wrong entry point/App component, Vite/Caddy caching, wrong volume, build not rebuilt, routing mounting the old component) and fix it. Prove it: `curl -s http://localhost/ | head -30`, `docker compose logs frontend --tail 30`, and PNG screenshots of `/`, `/kunlik`, `/kategoriyalar`, `/qoshish` taken by Playwright (reuse `make shots`), which I will open. The home page must show the topbar, period tabs, category bar, hero claim card and the ranked list with real data from the API.

1. Commit and push ALL backend work (migrations, routes, money.py, periods.py, seed, tests). Show `git status --short | wc -l` = 0 and `git log --oneline | head`.

2. Reference capture (S1 step 1 was skipped): capture the prototype into docs/design/reference/ (viewports 1440x900, 1024x768, 768x1024, 390x844; dark and light; every route and state listed in docs/prompts/S1.md), and write docs/design/reference/INDEX.md and docs/design/TOKENS.md. Show `ls docs/design/reference | wc -l` and the head of INDEX.md.

3. Remove every hardcoded demo number from the frontend, for example "2 145" in frontend/src/components/Topbar.tsx. Live stats come only from /api/v1/stats/public and stay hidden unless SHOW_LIVE_STATS=true. Show `grep -rnE "2 145|37 onlayn|24,0" frontend/src backend/app` returning nothing.

4. Make the tests runnable in the backend container: add dev dependencies (pytest, pytest-asyncio, httpx) through a dev requirements file or a Docker build target; tests run against a real test Postgres database. Show `docker compose exec -T backend python -m pytest -q` with the FULL summary. Tests must cover: rank derivation with ties, tab visibility (empty period hidden), quote math (holder + 1 B), pagination, category filter, search, period boundaries with a frozen clock (Asia/Tashkent), seasonal mapping.

5. Show `curl -s http://localhost/openapi.json | python3 -c "import sys,json; print('\n'.join(sorted(json.load(sys.stdin)['paths'])))"` (GET /boards/{id}/quote must exist), `ls backend/app/db/migrations/versions`, and the seed command run twice (idempotent), with the output.

6. VISUAL DIFF (S1 step 5.3): with SEED_DEMO=true and reduced motion, capture the app for the same viewports, themes, routes and states as the reference into docs/screenshots/s1/, and write docs/screenshots/s1/DIFF.md with a pixelmatch mismatch percentage per screen. Mask countdowns, live counters, the wallet card and computed dates with `data-shot-mask` and list the masks. Target under 3%. List every screen above 3% with the cause and fix every fixable one. Do not hide any.

7. Rebuild everything so the running containers match the source: `docker compose --profile dev up -d --build`, then show `docker compose --profile dev ps -a` (all healthy, migrate Exited 0, bot on the current image) and the curl status loop from docs/prompts/S1.md step 5.2.

8. Update docs/STATE.md and docs/DECISIONS.md, commit, push.

Finish with a short REPORT of real outputs. Do NOT write "done" if any item failed; write which item failed and why.
