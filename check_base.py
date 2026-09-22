import subprocess

cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-i', '/home/kai/.ssh/hetzner_key', 'root@188.245.70.100', 'docker exec rung-backend_prod-1 cat /app/app/db/base.py']
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
if res.stderr:
    print("STDERR:\n", res.stderr)
