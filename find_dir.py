import subprocess

cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-i', '/home/kai/.ssh/hetzner_key', 'root@188.245.70.100', 'docker inspect rung-backend_prod-1 --format "{{ index .Config.Labels \\"com.docker.compose.project.working_dir\\" }}"']
res = subprocess.run(cmd, capture_output=True, text=True)
print("DIR:", res.stdout)
