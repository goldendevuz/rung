import subprocess

cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-i', '/home/kai/.ssh/hetzner_key', 'root@188.245.70.100', 'hostname; pwd; cd /root/projects/rung && git log -1 --oneline && git status && docker compose -f docker-compose.yml --profile prod ps && docker compose -f docker-compose.yml --profile prod images']
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
