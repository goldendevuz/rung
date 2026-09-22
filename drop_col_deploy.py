import subprocess

cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-i', '/home/kai/.ssh/hetzner_key', 'root@188.245.70.100', 'docker exec rung-postgres_prod-1 psql -U rung -d rung -c "ALTER TABLE listings DROP COLUMN IF EXISTS public_id CASCADE; UPDATE alembic_version SET version_num=\'0002\';" && cd /root/projects/rung && docker compose --profile prod up -d']
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
if res.stderr:
    print("STDERR:\n", res.stderr)
