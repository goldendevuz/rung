# Payments, Refund, Auth and Accounts

> Part of the Rung spec. Source of truth together with AGENTS.md. Section numbers below are historical; ignore the numbering.

## 6. Payments

### Telegram Stars (auto, in the bot)
- Packages (inline buttons): 5 -> 1 B, 25 -> 5 B, 50 -> 10 B, 100 -> 20 B, 250 -> 50 B, 500 -> 100 B, plus a custom amount (min 5 Stars).
- Flow: `bot.send_invoice(currency="XTR", provider_token="", prices=[LabeledPrice(...)])` -> `pre_checkout_query` answered immediately -> `successful_payment` -> bot calls backend internal endpoint with `telegram_payment_charge_id`, user id, stars amount. Backend credits B idempotently (UNIQUE charge id). Bot confirms with a button that opens the Web App.
- From the website: in Telegram context use an invoice link (`create_invoice_link` + `Telegram.WebApp.openInvoice`); in a normal browser show a deep link `https://t.me/rung_uz_bot?start=topup_<stars>`.

### Paynet (manual, in UZS)
- User creates a top-up request (amount in UZS -> shows B to be credited, plus payment instructions text from settings — do not hardcode card numbers, and attach a receipt image or transaction reference). Admin approves or rejects in the bot (and a minimal admin page). Approval credits B idempotently. All statuses are stored and shown in history.

### Refund (BETA, admin only)
- Admins are Telegram user IDs from env `ADMIN_TG_IDS` (initially `557407324`). Every admin action re-checks the ID and is written to `audit_log`.
- Rule: refund is allowed only if the user's current wallet balance >= the B credited by that payment (i.e. the B is unspent). Otherwise reject with a clear message showing the shortfall. Never create negative balances.
- Sequence: reserve/debit inside a DB transaction (ledger kind `refund_reversal`), call `bot.refund_star_payment(user_id, telegram_payment_charge_id)`, on success mark payment `refunded` and notify the user, on failure re-credit and mark `refund_failed` with the error. Design the payment status machine so that re-payment in another currency can be added later.

## 7. Auth and accounts

- Single account model. Identities table: (`google`, sub/email) and (`telegram`, telegram_id). One user can have both.
- Google OAuth (authlib) for web login. Creating a listing REQUIRES a linked Google identity (anti-spam, verified email).
- Telegram Mini App login: validate `initData` HMAC with the bot token, reject `auth_date` older than 24 h, then issue the normal session.
- Linking: Telegram-first user links Google via a one-time token -> open the OAuth link in the EXTERNAL browser (`Telegram.WebApp.openLink`), because Google blocks OAuth inside embedded webviews. Google-first user links Telegram via `https://t.me/rung_uz_bot?start=link_<one-time-token>`; the bot confirms and calls the backend.
- If the identity being linked already belongs to ANOTHER account, refuse with a clear message. No automatic merging in v1 (record a TODO for an admin merge tool in docs).
- Sessions: httpOnly, Secure (when HTTPS), SameSite=Lax cookies; short access token + rotating refresh token; CSRF protection for cookie-authenticated mutations.


### Dev-only login and temporary environments
- `DEV_AUTH=true` enables `POST /api/v1/auth/dev-login` (pick or create a fake user with google and/or telegram identity, optional admin flag). The app MUST refuse to start if `ENV=prod` and `DEV_AUTH=true`. It exists so that Google OAuth (which needs a stable public domain) does not block testing before rung.uz exists.
- Google OAuth redirect URIs cannot be a bare IP address. `http://localhost` works. A tunnel URL works only if you add that exact URL to the Google console. Real Telegram login (initData) works on any HTTPS URL.
