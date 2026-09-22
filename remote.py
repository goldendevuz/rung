import subprocess
cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-i', '/home/kai/.ssh/hetzner_key', 'root@188.245.70.100', 'cd /opt/rung && git log -1 --oneline && git status && docker compose -f docker-compose.yml ps && docker compose -f docker-compose.yml images']
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print('STDERR:', res.stderr)
