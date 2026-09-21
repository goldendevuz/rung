cd /root/projects/rung
echo "=== HOSTNAME & DATE ==="
hostname; date -u
echo "=== CADDY CREATION/START TIME ==="
docker inspect rung-caddy-1 --format 'created={{.Created}} started={{.State.StartedAt}}'
echo "=== CADDY LOGS ==="
docker logs rung-caddy-1 --tail 25
echo "=== CADDYFILE CONTENT ==="
docker exec rung-caddy-1 head -14 /etc/caddy/Caddyfile
echo "=== INTERNAL ROUTING TESTS ==="
CIP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' rung-caddy-1)
for p in / /healthz /api/v1/boards/tabs; do
  echo "== $p"
  curl -si -H 'Host: rung.shats.uz' http://$CIP$p | head -12
done
echo "=== DOCKER PS ==="
docker compose --profile prod ps -a
echo "=== DOCKER MEMORY LIMITS ==="
docker inspect -f '{{.Name}} {{.HostConfig.Memory}}' $(docker ps -q)
echo "=== CLOUDFLARED LOGS ==="
docker logs rung-cloudflared-1 --tail 15 | grep -i "registered\|error"
echo "=== BOT LOGS ==="
docker logs rung-bot_prod-1 --tail 10
echo "=== PUBLIC URL TEST ==="
curl -s -o /dev/null -w "%{http_code}\n" https://rung.shats.uz/
