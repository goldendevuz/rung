import subprocess

cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-i', '/home/kai/.ssh/hetzner_key', 'root@188.245.70.100', 'rm /root/projects/rung/backend/app/db/migrations/versions/1ac49fab3453_add_public_id.py && cd /root/projects/rung && docker compose --profile prod build && docker compose --profile prod up -d']
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
if res.stderr:
    print("STDERR:\n", res.stderr)
