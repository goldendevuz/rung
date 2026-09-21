mkdir -p /root/backups/rung-d1
cd /root/backups/rung-d1
docker ps -a --format 'table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}' > inventory-before.txt
docker ps -q > running-ids.txt
docker inspect --format '{{.Name}} {{.HostConfig.RestartPolicy.Name}}' $(docker ps -aq) > restart-policies.txt
docker volume ls > volumes.txt
docker network ls > networks.txt
docker system df > system-df.txt
free -m > free.txt
swapon --show > swapon.txt
cat restart-policies.txt
