import yaml

filepath = '/home/kai/projects/rung/docker-compose.yml'
with open(filepath, 'r', encoding='utf-8') as f:
    compose = yaml.safe_load(f)

if 'worker_prod' not in compose['services']:
    worker_prod = compose['services']['worker'].copy()
    worker_prod['profiles'] = ['prod']
    worker_prod['environment']['ENV'] = '${ENV:-prod}'
    worker_prod['environment']['REDIS_URL'] = '${REDIS_URL:-redis://redis_prod:6379/0}'
    worker_prod['depends_on'] = {
        'migrate_prod': {'condition': 'service_completed_successfully'},
        'redis_prod': {'condition': 'service_healthy'}
    }
    compose['services']['worker_prod'] = worker_prod

if 'bot_prod' not in compose['services']:
    bot_prod = compose['services']['bot'].copy()
    bot_prod['profiles'] = ['prod']
    bot_prod['environment']['ENV'] = '${ENV:-prod}'
    bot_prod['environment']['BACKEND_URL'] = 'http://backend_prod:8000'
    compose['services']['bot_prod'] = bot_prod

with open(filepath, 'w', encoding='utf-8') as f:
    yaml.dump(compose, f, sort_keys=False, default_flow_style=False)
