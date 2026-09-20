First read AGENTS.md, docs/STATE.md, docs/DECISIONS.md and docs/spec/04-bot-and-engineering.md.

D1 (v2) — FREE PORTS, PROD PROFILE, DEMO MODE AND FIRST DEPLOY through a CLOUDFLARE TUNNEL. Do the steps in order, show REAL output for each, and STOP where a step says STOP. Never print, log, echo or commit any secret (bot tokens, tunnel token, passwords). I will put BOT_TOKEN and TUNNEL_TOKEN into the server's .env myself; you only prepare the file with empty placeholders and tell me the exact commands.

Target: my Hetzner Ubuntu server, SSH: `ssh -i /home/kai/.ssh/hetzner_key root@188.245.70.100`, project directory /root/projects/rung, public hostname https://rung.shats.uz (later rung.uz). HTTPS and DNS come from a Cloudflare Tunnel: NO DNS A record, NO Let's Encrypt, NO inbound ports. Coolify is NOT used, but the server's hostname suggests it may be installed: leave it and everything else already on the server completely untouched. Google OAuth is not implemented yet (slice S2); this deploy verifies containers, routing, the tunnel and the bot.

SERVER AUTHORIZATION: you may run any command over SSH that I explicitly give you. For commands you decide on yourself: start with read-only inspection, never stop, remove or modify existing containers, volumes, files, or firewall rules that are not ours, and ask me first before anything destructive or irreversible (rm -rf, docker system prune, firewall changes, killing processes).

1. FREE-PORT POLICY (dev)
No host port is hardcoded. Container-internal ports stay fixed; every HOST port comes from an env variable, and `scripts/pick-ports.sh` finds free ports (checks `ss -ltn` and ports published by running containers) and writes them into .env: HTTP_PORT, HTTPS_PORT, FRONTEND_HOST_PORT, BACKEND_HOST_PORT, POSTGRES_HOST_PORT, REDIS_HOST_PORT, all bound to 127.0.0.1 in dev. `make up` runs pick-ports first (keeping values already set and still free). The Vite dev server (5173) is never published in prod. Prove it: occupy ports 80 and 5173 with `python3 -m http.server`, run `make up`, show the chosen ports and that the site opens on the chosen HTTP_PORT, then release the ports. The prod profile publishes NO host ports at all (an optional 127.0.0.1 debug port behind an env variable is fine).

2. PROD PROFILE WITH THE TUNNEL
- Caddy in prod listens only on internal port 80, plain HTTP (`auto_https off`), serves the static frontend build with `try_files {path} /index.html`, proxies `/api/*` to backend. The compose service is named `caddy`.
- Add a `cloudflared` service to the prod profile: image cloudflare/cloudflared:latest, `command: tunnel --no-autoupdate run`, environment `TUNNEL_TOKEN=${TUNNEL_TOKEN}`, restart unless-stopped, same compose network as caddy, depends_on caddy. (The cloudflared image has no shell; skip its healthcheck or use `cloudflared tunnel ready` if metrics are enabled.)
- Cloudflare terminates HTTPS. Make the backend honour forwarded headers (uvicorn `--proxy-headers`, trusted only from the internal network) so the app sees https for redirects and Secure cookies. Session cookies Secure, SameSite=Lax.
- All hostnames only from env (PUBLIC_BASE_URL=https://rung.shats.uz, WEBAPP_URL, CORS_ORIGINS, cookie domain) so moving to rung.uz is an env change plus a 301.
- `restart: unless-stopped`, healthchecks on every long-running service (except cloudflared), json-file log rotation, migrations as the one-shot `migrate` service before backend, ENV=prod, DEV_AUTH=false (the app must refuse to start otherwise). DB and Redis not published.

3. DEMO MODE (prod must show NO demo data)
- In prod SEED_DEMO=false: the site shows the real empty state and real zero statistics. Never write fake listings, entries or clicks into the production database.
- Add a TEMPORARY "Demo" button in the UI, visible only when SHOW_DEMO_BUTTON=true (I will set it on rung.shats.uz). Pressing it enables "Demo rejim" (persisted in localStorage): the frontend sends `X-Rung-Demo: 1` and the backend serves built-in in-memory fixtures (the prototype's 14 paid + 2 free channels, same response shape) READ-ONLY, with no database writes, and a visible banner "Demo ma'lumotlar, haqiqiy emas" plus a button to leave demo mode. All mutating actions are disabled in demo mode. Real endpoints without the header are unaffected. Document that this button and the fixtures are to be removed before public launch, and add a `make` check that fails if SHOW_DEMO_BUTTON=true when ENV=prod and PUBLIC_BASE_URL is the final domain.

4. DEPENDENCY VULNERABILITIES
GitHub Dependabot reported 9 vulnerabilities (1 critical, 1 high, 7 moderate). Run `npm audit` in frontend and `pip-audit` for backend and bot, upgrade everything critical and high (moderate where safe), rebuild, run `make smoke` and the backend tests, and show before/after counts.

5. BOT TOKENS
- Local development uses my beta bot @rung_beta_bot: the bot reads `BOT_TOKEN_DEV` when ENV=dev (falling back to BOT_TOKEN), so local and server never poll with the same token. The server (ENV=prod) uses BOT_TOKEN (@rung_uz_bot). BOT_USERNAME is per environment. Add both variables to .env.example (empty). If the token is missing the bot stays idle and healthy.

6. SERVER INSPECTION (read-only), then STOP
Connect over SSH and run: `cat /etc/os-release`, `uname -a`, `df -h`, `free -m`, `docker --version`, `docker compose version`, `docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}'`, `ss -ltnp`, `ufw status verbose`, `ls -la /root/projects`, and whether Coolify/Traefik/nginx/Caddy exist. Report the findings. Confirm that we need no inbound ports (the tunnel connects outbound) and that our stack will not clash with anything. STOP and wait for my confirmation.

7. GET THE CODE (after my confirmation)
`cd rung` failed because the directory does not exist yet. The repo git@github.com:goldendevuz/rung.git is private: on the server generate a read-only deploy key (`ssh-keygen -t ed25519 -f ~/.ssh/rung_deploy -N ""`), print ONLY the public key and tell me to add it in GitHub -> repo Settings -> Deploy keys (read-only). After I confirm, clone into /root/projects/rung using `GIT_SSH_COMMAND='ssh -i ~/.ssh/rung_deploy -o IdentitiesOnly=yes'` and configure the repo to use that key for later pulls. No Coolify.

8. PRODUCTION .env (on the server only)
Create /root/projects/rung/.env: ENV=prod, TZ=Asia/Tashkent, DEV_AUTH=false, SEED_DEMO=false, SHOW_DEMO_BUTTON=true, STARS_ENABLED=true, PUBLIC_BASE_URL=https://rung.shats.uz, WEBAPP_URL=https://rung.shats.uz, generate SECRET_KEY, INTERNAL_API_TOKEN and POSTGRES_PASSWORD there with `openssl rand`. Leave BOT_TOKEN and TUNNEL_TOKEN EMPTY and tell me the exact commands to fill them myself (`nano /root/projects/rung/.env`; chmod 600). After I say they are filled, verify they are non-empty WITHOUT printing values (for example `awk -F= '/^(BOT_TOKEN|TUNNEL_TOKEN)=/{print $1, ($2==""?"EMPTY":"set")}' .env`).

9. START AND CLOUDFLARE HOSTNAME
Start the prod profile. Show `docker compose --profile prod ps -a` and the cloudflared log line proving the tunnel connected (never print the token). Then tell me exactly what to configure in the Cloudflare dashboard (Zero Trust -> Networks -> Tunnels -> my tunnel -> Public Hostname): subdomain `rung`, domain `shats.uz`, Service type HTTP, URL `caddy:80` (the caddy service inside the compose network, no extra port). STOP until I confirm it is saved.

10. VERIFY
`curl -s -o /dev/null -w "%{http_code}\n"` on https://rung.shats.uz for /, /kunlik, /kategoriyalar, /qoshish, /haqida, /qoidalar, /kirish, /login, /api/v1/boards/tabs, /healthz; confirm the home page shows the REAL empty state (0 listings) and that Demo mode works and is read-only and leaves the database unchanged (show a row count before and after). `make smoke` against the public URL passing. Playwright screenshots of the public URL (desktop and mobile) into docs/screenshots/d1/. The server bot log shows getMe and polling for @rung_uz_bot.

11. BACKUPS
Nightly `pg_dump` (cron or compose job) into /root/backups with 7-day retention, plus a documented and TESTED restore into a scratch database. Show the test output.

12. DOCS
Write docs/DEPLOY.md: update (git pull, rebuild, migrate), rollback, restore, logs, changing ports, the tunnel setup, the exact Google OAuth client setup (authorized JavaScript origin https://rung.shats.uz, redirect URI https://rung.shats.uz/api/v1/auth/google/callback, consent screen authorized domain shats.uz), Resend domain verification notes, and the checklist for moving to rung.uz. Update docs/STATE.md and docs/DECISIONS.md, commit, push, tag d1.

Finish with a REPORT with real outputs. Do NOT write "done" if any item failed; write which item failed and why.
