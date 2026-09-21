import yaml

with open('docker-compose.yml', 'r') as f:
    data = yaml.safe_load(f)

# Postgres limits
data['services']['postgres_prod']['mem_limit'] = '256m'
data['services']['postgres_prod']['memswap_limit'] = '256m'
data['services']['postgres_prod']['command'] = 'postgres -c shared_buffers=64MB -c max_connections=20'

# Redis limits
data['services']['redis_prod']['mem_limit'] = '64m'
data['services']['redis_prod']['memswap_limit'] = '64m'
data['services']['redis_prod']['command'] = 'redis-server --maxmemory 48mb --maxmemory-policy noeviction'

# Backend limits
data['services']['backend_prod']['mem_limit'] = '256m'
data['services']['backend_prod']['memswap_limit'] = '256m'
if 'environment' in data['services']['backend_prod']:
    data['services']['backend_prod']['environment']['WORKERS'] = '1'
    data['services']['backend_prod']['environment']['WEB_CONCURRENCY'] = '1'

# Worker limits
data['services']['worker_prod']['mem_limit'] = '192m'
data['services']['worker_prod']['memswap_limit'] = '192m'

# Bot limits
data['services']['bot_prod']['mem_limit'] = '256m'
data['services']['bot_prod']['memswap_limit'] = '256m'

# Caddy limits and changes
data['services']['caddy']['mem_limit'] = '64m'
data['services']['caddy']['memswap_limit'] = '64m'
if 'image' in data['services']['caddy']:
    del data['services']['caddy']['image']
data['services']['caddy']['build'] = {
    'context': '.',
    'dockerfile': 'deploy/caddy/prod/Dockerfile'
}
if 'volumes' in data['services']['caddy']:
    data['services']['caddy']['volumes'] = [
        v for v in data['services']['caddy']['volumes']
        if not v.startswith('./deploy/caddy') and not v.startswith('./frontend')
    ]
data['services']['caddy']['healthcheck'] = {
    'test': ['CMD-SHELL', 'wget -qO- http://127.0.0.1:80/healthz || exit 1'],
    'interval': '15s',
    'timeout': '5s',
    'retries': 5,
    'start_period': '10s'
}

# Cloudflared limits
data['services']['cloudflared']['mem_limit'] = '64m'
data['services']['cloudflared']['memswap_limit'] = '64m'

with open('docker-compose.yml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
