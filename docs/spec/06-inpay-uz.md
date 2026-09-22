# SLICE S4 — inPAY.uz automatic UZS top-up

Read docs/spec/06-inpay-uz.md (new — replaces the Checkout.uz spec) completely before starting. Do not work from memory.

SLICE S4 — inPAY.uz automatic UZS top-up. Do ONLY this. Start now, ask me only about real blockers.

## 1. Backend

a) `POST /api/v1/wallet/topup` — body `{b_amount}` (whole B). Validate min 1 B. Server converts to UZS (`b_amount * B_UNIT_UZS`), calls inPAY `GET /authorization/` (cache the bearer token in Redis with its ~24h TTL, refresh on expiry/401) then `POST /create/` with our `callback_url` and `return_url`. Store a pending top-up row keyed by inPAY's `order_id` (unique constraint on `order_id`, this is the idempotency key). Return `{pay_url, order_id}`.

b) `POST /api/v1/payments/inpay/callback` — receives inPAY's webhook `{amount, status, order_id, transaction_id, created_at}`. This payload is NOT trusted on its own (no signature). On receipt: look up the pending top-up by `order_id`; if found, call `GET /api/v1/transactions/?order_id=` ourselves against inPAY; only if that call's own `status == "success"` and `amount` matches the expected UZS amount, credit the wallet (append-only ledger row, `b_amount = amount / B_UNIT_UZS`) and mark the top-up row `completed`. Always respond `HTTP 200` to the webhook itself regardless of outcome (inPAY retries on non-200). A DB-level unique constraint on `order_id` in the ledger must make a double-credit impossible even if this handler somehow runs twice.

c) Reconciliation job (arq, every 1 minute): find top-up rows still `pending` for more than ~2 minutes, call `GET /transactions/?order_id=` for each, apply the same credit-only-after-server-check logic as (b). This covers a webhook that never arrives.

d) `GET /api/v1/wallet/topup/:order_id` — our own endpoint the frontend polls after redirect back from `return_url`; returns the top-up row's current status (`pending`/`completed`/`failed`) from OUR database, not from inPAY's return-URL query params.

e) `merchant_id`/`merchant_token` read from env, never logged, never returned in any API response.

## 2. Frontend

- Wallet page: pick a B amount (whole B, e.g. quick-pick chips + custom input), "To'ldirish" button calls `/wallet/topup`, redirects the browser to `pay_url`.
- On return (`return_url` back on our site): show a "Tekshirilyapti..." spinner state, poll `GET /api/v1/wallet/topup/:order_id` every ~2s until `completed` or `failed`, then show the result and the updated wallet balance. Never read `status`/`amount` from the return URL's own query params as the source of truth — only our polled endpoint.
- Update `GET /api/v1/public-config`'s payment-provider text now that a real gateway is live (drop the "to'lov tez orada" placeholder — say something like "avtomatik to'lov: Click, Payme").

## 3. Config

Add to `.env.example` (secrets empty): `INPAY_MERCHANT_ID`, `INPAY_MERCHANT_TOKEN`, `INPAY_CALLBACK_URL=https://rung.shats.uz/api/v1/payments/inpay/callback`, `INPAY_RETURN_URL=https://rung.shats.uz/hamyon`.

Tell me explicitly: in the inPAY dashboard, is IP whitelist mode currently `strict`, `optional`, or `disabled` for this kassa? If not `strict`, set it to `strict` with the VPS IP (188.245.70.100) and confirm.

## SECURITY — do not skip

- The `/create/` and `/authorization/` calls always go server-to-server (backend → inPAY). `merchant_token` never reaches the browser or the bot, in any response, log line, or error message.
- Never call `/api/v1/cardsystem/*` anywhere in this codebase — hosted checkout (`pay_url`) only.
- The webhook handler must not credit anything without the follow-up `GET /transactions/?order_id=` check succeeding first — this is the whole point of this slice, verify it actually works this way in the code, not just in the spec doc.
- **The `merchant_id`/`merchant_token` currently in `.env` — were these values ever pasted into a chat, a doc, or a screenshot that left your machine (including the inPAY dashboard's own example code snippets, which some accounts auto-fill with real credentials)? If there's any doubt, rotate the merchant_token in the inPAY dashboard before wiring it in, the same way the Checkout.uz key was rotated. Tell me which you did.**

## ACCEPTANCE GATE (real evidence, against the live public URL)

- `curl -i -X POST https://rung.shats.uz/api/v1/wallet/topup -d '{"b_amount":1}' ...` → raw response with `pay_url`/`order_id`.
- Complete one real 1 B top-up yourself end to end (you can do this — it's just a payment, use the smallest real amount or inPAY's test mode if one exists) and paste: the webhook payload your server actually received, the raw `GET /transactions/?order_id=` response your server made to verify it, and the wallet balance before/after with the ledger row.
- Prove idempotency: replay the same webhook payload a second time (curl it at your own callback endpoint yourself) and show the wallet balance did NOT change the second time.
- Confirm and paste the current IP whitelist mode for the kassa.
- `grep -rn "merchant_token\|INPAY_MERCHANT_TOKEN" backend/ bot/` → should show it only read from env, never hardcoded, never in a response model.

Finish with a REPORT: exact commands and real output, what I must configure myself (dashboard settings), known gaps. Do not write "done" for anything not shown with real output.
