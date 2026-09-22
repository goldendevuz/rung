import subprocess

sql_cmd = """
TRUNCATE TABLE users, listings, boards, board_entries, listing_stats_daily RESTART IDENTITY CASCADE;
"""

cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-i', '/home/kai/.ssh/hetzner_key', 'root@188.245.70.100', f'docker exec rung-postgres_prod-1 psql -U rung -d rung -c "{sql_cmd}"']
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
if res.stderr:
    print("STDERR:\n", res.stderr)
