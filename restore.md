# Restore Plan

Run the following command to restore the containers in the exact reverse order they were listed before stopping:
```bash
docker start $(tac /root/backups/rung-d1/running-ids.txt | tr '\n' ' ')
```

To revert the restart policy for the three DB/Celery containers:
```bash
docker update --restart=always 8cf3d378cc58 6eea9afd7045 7d2d3f8a145f
```

The following three containers were also stopped (no rm) and can be started manually:
- telegram-bot-api
- warp
- cloudflared-7aiwow9kshv0prxfjtuhjaor-100623505429

### Exploit-Server and Qoraqozon Restoration
To restore the cron jobs for the exploit-server watchdog, qoraqozon healthcheck_alert, and qoraqozon backup_db:
```bash
crontab /root/backups/rung-d1/crontab-before.txt
```

To restart the exploit-server containers:
```bash
docker start 3dc86fe95456 aa208a68d377 8dcc13c65b89 57dff2ed6f79
```
