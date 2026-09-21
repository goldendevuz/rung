# Checkout.uz payment gateway (automatic UZS top-up)

> Part of the Rung spec. Source: the official docs at https://checkout.uz/api-docs (PDF copy provided by the owner). This file replaces the Stars and Paynet-manual payment flows for now: `STARS_ENABLED=false`, `PAYNET_ENABLED=false`, both kept behind flags. Implement it in the payment slice, not earlier.

## API summary (from the docs)
- Base URL `https://checkout.uz/api/v1`, every request `Authorization: Bearer <API key>`, optional IP whitelist configured in the cashier settings.
- `POST /create_payment` {amount (UZS, min 1000, max 10 000 000), description?, webhook_url?, return_url?} -> `payment` with `_id`, `_uuid`, `_url` (hosted payment page), `_amount`, `_status` (pending), `_pay_via` {click, payme}, `_lifeteme._second` (3600).
- `POST /status_payment` {id or uuid} -> `data` {id, amount, status (paid/...), created_at, paid_at}.
- `POST /get_fiscal` {order_id} (fiscal receipt data), `/get_balance`, `/get_history`, `/get_stats`, `/get_payment_methods`.
- `/pay_via_card` and `/confirm_card_payment` take raw card numbers and SMS codes. NEVER use them: card data must not touch our servers. Always redirect the user to the hosted `_url`.
- Webhook: POST to the cashier's webhook URL and/or the `webhook_url` given in `create_payment`, body `{webhook_type:"version_1_1", status:"success", event:"payment_confirmed", payment_system, shop_id, data:{order_id, amount, currency:"UZS", status:"paid", provider_details, perform_time}, timestamp}`. We must answer HTTP 200. Failed deliveries are NOT retried automatically.

## Configuration (server .env only, never in git, chat or logs)
`CHECKOUT_ENABLED=false`, `CHECKOUT_API_KEY`, `CHECKOUT_SHOP_ID`, `CHECKOUT_BASE_URL=https://checkout.uz/api/v1`, `CHECKOUT_WEBHOOK_SECRET_PATH` (random 32+ chars). The gateway keeps about 7.5% of income as its fee (informational): we credit the full B amount and absorb the fee.

## Money rules
Packages 5 000 / 10 000 / 25 000 / 50 000 / 100 000 UZS = 5 / 10 / 25 / 50 / 100 B, plus a custom amount in whole thousands within the gateway limits. B credited = UZS / 1000. Store provider=`checkout_uz`, currency=`UZS`, provider_amount, provider_charge_id (= invoice `_id`, UNIQUE per provider), b_credited, status, raw meta. The UI shows only B (payment details behind `SHOW_PAYMENT_DETAILS`).

## Flow
1. User picks an amount. Backend creates a local `payments` row (status `created`, idempotency key) and calls `create_payment` with `description` "Rung top-up <payment_uuid>", `webhook_url` = `PUBLIC_BASE_URL/api/v1/webhooks/checkout/<CHECKOUT_WEBHOOK_SECRET_PATH>`, `return_url` = `PUBLIC_BASE_URL/hamyon?paid=<payment_uuid>`.
2. Store `_id`, `_uuid`, `_url`, expiry (now + 3600 s), set status `pending`, redirect the user to `_url` (hosted page where they choose Click or Payme).
3. Crediting happens ONLY through `settle(payment)`: it calls `status_payment`, requires status `paid` AND amount equal to our stored expected amount, then credits B in one transaction (ledger kind `topup`, idempotency key `checkout:<invoice id>`), sets status `paid`, stores fiscal info when available (`get_fiscal`), and notifies the user through the bot.

## Webhook security (critical: the docs describe NO signature)
- Anyone can POST a fake webhook, so the webhook is a hint, never proof. The handler only extracts `data.order_id`, finds OUR payment with that provider id, and calls `settle()`, which verifies with `status_payment` using our API key. A forged webhook must never credit anything.
- The endpoint path contains the unguessable secret; wrong path = 404. Limit body size (64 KB), rate limit, log every delivery (without secrets), always answer 200 for well-formed requests (unknown order too) so nothing is leaked.
- Amount mismatch -> status `mismatch`, no credit, alert the admin.

## Missed webhooks and reconciliation
No automatic retries, so an arq cron runs every minute: for `pending` payments younger than 24 h call `settle()` (backoff 1/2/5/10 minutes, then every 10 minutes); mark `expired` after the invoice lifetime plus a grace period while still pending. The return page polls `GET /api/v1/payments/{uuid}`, which also calls `settle()` for pending payments (rate limited).

## Status machine
`created -> pending -> paid | expired | failed | mismatch`. Never move away from `paid`. All transitions audited.

## Refunds
The gateway API documents no refund call. Refunds are manual and admin only, and only when the credited B is unspent (ledger reversal), exactly as in the earlier refund rule.

## Telegram policy risk (unverified)
Telegram expects Stars for digital goods sold inside its apps, and B credits are digital goods. To stay safe: the payment page opens on the normal website; inside the Telegram Mini App the top-up button opens the EXTERNAL browser (`Telegram.WebApp.openLink`) and never an in-app payment form. Record this risk in docs/DECISIONS.md and re-evaluate if Telegram objects.

## Tests
Mock the gateway (respx): create/status/webhook. Required cases: forged webhook does not credit; wrong amount -> mismatch; duplicate webhook is idempotent; a missed webhook is credited by reconciliation; expired invoice; gateway timeout; user cannot settle someone else's payment. Live acceptance: one real 1 000 UZS payment on production, verified end to end (ledger row, B balance, bot message, fiscal data).
