cd /root/projects/rung
export NODE_OPTIONS=--max-old-space-size=1024
for svc in backend_prod worker_prod bot_prod caddy; do
  mem=$(awk '/MemAvailable/ {print $2}' /proc/meminfo)
  if [ "$mem" -lt 1000000 ]; then
    echo "MemAvailable too low ($mem), stopping"
    exit 1
  fi
  echo "Building $svc..."
  docker compose --profile prod build $svc
done
docker compose --profile prod up -d --no-deps --force-recreate caddy backend_prod worker_prod bot_prod
