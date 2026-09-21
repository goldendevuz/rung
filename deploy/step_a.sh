#!/bin/bash
ssh -o StrictHostKeyChecking=no -i /home/kai/.ssh/hetzner_key root@188.245.70.100 << 'EOF'
echo '--- watchdog.sh ---'
cat /root/projects/exploit-server/scripts/watchdog.sh 2>/dev/null || echo 'Missing'
echo '--- healthcheck_alert.sh ---'
cat /root/projects/qoraqozon/scripts/healthcheck_alert.sh 2>/dev/null || echo 'Missing'
echo '--- backup_db.sh ---'
cat /root/projects/qoraqozon/scripts/backup_db.sh 2>/dev/null || echo 'Missing'
echo '--- crons ---'
ls -la /etc/cron.d /etc/cron.hourly /etc/cron.daily 2>/dev/null
echo '--- timers ---'
systemctl list-timers --all --no-pager | head -25
echo '--- backup directory ---'
ls -la /root/backups 2>/dev/null || ls -la /root/projects/qoraqozon/backups 2>/dev/null || echo "No backup dir found"
EOF
