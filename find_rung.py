import subprocess

cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-i', '/home/kai/.ssh/hetzner_key', 'root@188.245.70.100', 'find / -type d -name "rung" -not -path "*/.local/*" -not -path "*/projects/*" -maxdepth 4 2>/dev/null']
res = subprocess.run(cmd, capture_output=True, text=True)
print("DIRS:", res.stdout)

cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-i', '/home/kai/.ssh/hetzner_key', 'root@188.245.70.100', 'docker ps --format "{{.Names}}"']
res = subprocess.run(cmd, capture_output=True, text=True)
print("CONTAINERS:", res.stdout)
