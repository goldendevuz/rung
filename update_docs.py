import os

decisions_path = '/home/kai/projects/rung/docs/DECISIONS.md'
agents_path = '/home/kai/projects/rung/AGENTS.md'
payments_spec = '/home/kai/projects/rung/docs/spec/02-payments-auth.md'

new_decisions = '''
## Payments (Checkout.uz) and Telegram Auth (Sep 21)
- STARS_ENABLED=false, PAYNET_ENABLED=false, GOOGLE_AUTH_ENABLED=false. All existing code for these stays behind flags.
- Payments: automatic UZS through Checkout.uz (specified in docs/spec/06-checkout-uz.md). The webhook carries no signature, so it is only a " check now\
