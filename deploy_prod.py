import subprocess

cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-i', '/home/kai/.ssh/hetzner_key', 'root@188.245.70.100', 'cd /root/projects/rung && docker compose -f docker-compose.yml --profile prod up -d --build backend_prod worker_prod migrate_prod && docker compose -f docker-compose.yml --profile prod ps']
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
if res.stderr:
    print("STDERR:\n", res.stderr)
