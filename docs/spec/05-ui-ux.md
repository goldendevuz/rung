# UI/UX Specification

> Part of the Rung spec. Source of truth together with AGENTS.md. Section numbers below are historical; ignore the numbering.

## 13. UI/UX specification

Quality benchmark: outbid.lol feels polished and effortless. Treat it ONLY as a benchmark for quality. Do NOT copy its markup, class names, copy, colors, icons, proportions or component structure. Rung must be recognizably its own product.

Identity — "the ladder":
- A vertical rung rail on the left of the list: each rank sits on a rung marker; the top ranks glow. Rows have stepped tints that fade with rank (top 10), not a single flat highlight.
- Dark theme by default with an accessible light theme. Tokens (CSS variables): bg `#0D1015`, surface `#141920`, surface-2 `#1A212B`, border `#252E3A`, text `#E9EEF5`, muted `#8B97A8`, primary (signal lime) `#B8F03C` with dark foreground, accent (violet) `#7C6CFF`, success `#3DDC97`, warn `#FFB84D`, danger `#FF5D6C`. Derive a light palette where the primary is darkened to pass WCAG AA.
- Typography: Manrope for UI and headings, JetBrains Mono (tabular numerals) for prices and ranks. Self-host fonts.
- Microcopy in Uzbek, warm and confident (examples: "Bir pog'ona yuqoriga", "#3 o'rinni egallash — 14 B", "Hamyon", "To'ldirish", "E'lon qo'shish", "Yakunlanganlar", "Oldingi natijalar").

Screens and behavior:
- Home: header (logo, period tabs as a segmented control with live counts — only non-empty periods, wallet chip showing "12.4 B", avatar/login), category chips, ranked list. Row: rank on the rung, logo, name + tagline, category, verified unique visitors, time entered, price pill. Hover/focus reveals a "Claim #k — X B" action; on mobile, tapping a row action opens a bottom sheet with the quote (cost, resulting rank, balance after) and a confirm button with haptic feedback.
- Rank changes animate with framer-motion layout animations; a displaced row briefly flashes and slides down. Respect `prefers-reduced-motion`.
- Listing page `/p/:slug`: hero, description, verified stats, ranks per period, outbound button.
- Add listing wizard: paste URL -> auto-fetch -> edit -> save -> "buy a spot" step with multi-select periods showing a live quote for each and a total.
- Wallet: balance, top-up (Stars / Paynet), full history with filters, pending Paynet requests. Payment history shows B amounts only unless `SHOW_PAYMENT_DETAILS` is on.
- Profile: linked accounts (Google/Telegram), my listings, auto-renew toggles per period, "Yakunlanganlar", language, theme.
- Admin pages (minimal but real): moderation queue, payments/refunds, top-ups, settings.
- Everywhere: skeleton loaders, optimistic updates where safe, useful empty and error states, toasts, keyboard accessibility, focus rings, 44px touch targets, safe-area insets, Telegram integration (theme params, BackButton, MainButton, viewport), Lighthouse >= 90 on mobile for the home page.
- i18n: i18next with `uz` (only language until v1 is complete), `en`, `ru` files present with keys; no hardcoded strings in components.

