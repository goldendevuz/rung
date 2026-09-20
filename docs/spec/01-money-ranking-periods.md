# Money, Ranking, Periods

> Part of the Rung spec. Source of truth together with AGENTS.md. Section numbers below are historical; ignore the numbering.

## 3. Money rules (critical)

- Unit: 1 B = 1000 units, stored as BIGINT. NEVER floats. Use a `Money` helper. API returns integer `units` plus a display string with trailing zeros trimmed ("12", "12.4", "0.2").
- Approximate real values (configurable in the `settings` table, cached, editable by admin): 1 B ~ 1000 UZS (manual Paynet top-ups), 1 Telegram Star = 0.2 B (200 units).
- Bid prices are whole B. Wallet balances and history may be fractional (Stars top-ups).
- Every payment row stores provider (`telegram_stars`, `paynet_manual`, more later), currency (`XTR`, `UZS`), provider_amount, provider_charge_id (UNIQUE per provider), b_credited units, status, raw meta JSONB. The UI currently shows ONLY B amounts. Provider/currency details are hidden behind a feature flag `SHOW_PAYMENT_DETAILS` (default false) but must be stored from day one and returned to the owner by the API.
- Ledger: append-only double-record style table `ledger_entries` (user_id, delta_units, kind, ref_type, ref_id, balance_after, idempotency_key UNIQUE, created_at). A DB trigger must forbid UPDATE/DELETE on it. `wallets.balance_units` is a cached value updated in the same transaction under `SELECT ... FOR UPDATE`; a nightly reconcile job compares wallet vs SUM(ledger) and alerts on mismatch. Balance can never go negative (CHECK constraint).
- Every money-moving endpoint requires an `Idempotency-Key` header.

## 4. Ranking mechanics (formal)

- A Board = (period_type, period_key). Each period type is a SEPARATE market. A listing may hold one active entry per board.
- An Entry stores `paid_units` (whole B). Rank is DERIVED, never stored: order by `paid_units DESC, entered_at ASC`.
- Floor price = 1 B (setting). Minimum step = 1 B (setting).
- Append at the bottom (new last place): cost = floor (1 B).
- Claim a target rank k (1 <= k <= n): minimum cost = paid_units of the current holder at rank k + min step. The user may pay more (whole B). The new entry lands at `1 + COUNT(entries with paid_units >= paid)`; everyone below shifts down automatically because rank is derived.
- A listing that already has an active entry in that board can move up the same way: it pays the full new price, its old entry becomes `replaced` (soft), no refund or credit.
- Quote/claim protocol: `POST /boards/{id}/quote {listing_id, target_rank}` returns `{min_cost, resulting_rank, expires_in}`. `POST /boards/{id}/claim {listing_id, target_rank, max_pay}` with Idempotency-Key: inside ONE transaction lock the board row, recompute cost, if cost > max_pay return 409 with a fresh quote, otherwise charge the wallet (ledger kind `spend`), insert the entry, write audit log. Concurrency tests are mandatory (many parallel claims on the same rank must never double-sell a rank price or overdraw a wallet).
- The UI shows the resulting rank honestly ("you will land at #3").

## 5. Periods

- Types: `all_time`, `daily`, `weekly`, `monthly`, `seasonal`, `yearly`. Time zone `Asia/Tashkent`. Weekly = Mon–Sun. Seasonal = meteorological (Dec–Feb, Mar–May, Jun–Aug, Sep–Nov). Yearly = calendar year. `all_time` never rolls over.
- Boards are created lazily on first entry. A rollover cron job (arq, idempotent, safe to run twice) closes expired boards (status `closed`, standings frozen — entries are kept forever) and then handles auto-renew.
- New period starts empty; the first place costs floor (1 B).
- Auto-renew is a per-(listing, period_type) flag chosen by the owner. On rollover, for each flagged listing in previous final-rank order, try to charge the floor price from the owner's wallet and enter the new board (ledger kind `auto_renew`). If auto-renew is off or the balance is insufficient, the entry stays only in the closed board and appears in the owner's "Yakunlanganlar" (finished) section and publicly under "Oldingi natijalar" (previous results). NEVER use the word "archive/arxiv" in the UI. Nothing is ever deleted.
- The bot notifies owners: renewed, renewal failed (low balance), period ending soon.
- Tab visibility: a period tab is shown ONLY if the current board of that type has at least one active entry. This is computed live with SQL COUNT (Redis cache <= 15 s, invalidated on claim). No hardcoded or static tab lists or datasets. If nothing at all exists, show a friendly empty state with a call to action.

