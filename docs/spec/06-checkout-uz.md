# Payments via Checkout.uz (UZS, automatic)

> Spec for the upcoming payment implementation slice. **No code yet.** All decisions
> recorded here are approved. Implementation is deferred.

## Overview

Rung will accept payments in Uzbek soum (UZS) through **Checkout.uz** — an Uzbek
payment aggregator that supports Uzcard, Humo, and Visa/Mastercard cards issued in
Uzbekistan. The flow is fully automated (no admin approval step, unlike the old
Paynet manual flow).

## Flags

| Flag | Default | Meaning |
|---|---|---|
| `PAYNET_ENABLED` | `false` | Old manual Paynet flow; keep behind flag, do not delete code |
| `STARS_ENABLED` | `false` | Telegram Stars flow; keep behind flag, do not delete code |
| `CHECKOUT_UZ_ENABLED` | `false` (add in impl slice) | Checkout.uz automatic flow |

## Flow (to be implemented)

1. User clicks "To'ldirish" (topup) on the website.
2. Frontend calls `POST /api/v1/payments/checkout-uz/create` with `{ amount_uzs, idempotency_key }`.
3. Backend creates a `Payment` record (`provider=checkout_uz`, `currency=UZS`, `status=pending`) and calls Checkout.uz API to create an invoice.
4. Backend returns the Checkout.uz payment URL.
5. Frontend redirects user to the payment page (or opens in a new tab).
6. Checkout.uz calls the backend webhook `POST /api/v1/payments/checkout-uz/webhook` with the result.
7. Backend verifies the HMAC signature, credits B to the user's wallet idempotently (`UNIQUE charge_id`), and updates the `Payment` record to `paid`.
8. Backend notifies the user in the bot.

## Money rules (same as all flows)
- Integer units only. 1 B = 1000 units. BIGINT. Balance never negative.
- Ledger is append-only. Every credit uses `kind=topup_checkout_uz`.
- `Idempotency-Key` required on the create endpoint.
- Webhook must be idempotent (replay-safe): if `charge_id` already exists and is `paid`, return 200 immediately.

## Env vars to add in impl slice

```
CHECKOUT_UZ_MERCHANT_ID=
CHECKOUT_UZ_SECRET_KEY=
CHECKOUT_UZ_WEBHOOK_SECRET=
CHECKOUT_UZ_ENABLED=false
```

## UZS ↔ B rate

`b_unit_uzs` setting (DB) and `B_UNIT_UZS` env var define the conversion rate.
Current default: 1 B = 1 000 UZS. Do not hardcode.

## UI copy

The `PAYMENT_PROVIDER_TEXT` env var (returned by `GET /api/v1/public-config`) contains
the payment provider line shown in the hero note and claim sheet.

- Before Checkout.uz is live: `"to'lov tez orada"`.
- After launch: `"Checkout.uz orqali UZS"` or similar.
- Never hardcode provider names in JSX.

## Not in scope for this spec
- Refund flow (same as Stars: admin-only, conditional, separate ledger entry).
- Currency other than UZS (international cards — future).
- Telegram Stars and Paynet flows: code stays, flags remain false until decided.
