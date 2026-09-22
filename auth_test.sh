cd /home/kai/projects/rung
START_RESP=$(curl -s -X POST http://localhost:8000/api/v1/auth/telegram/start)
echo "Start response: $START_RESP"
TOKEN=$(echo $START_RESP | grep -o '"token":"[^"]*' | cut -d'"' -f4)
echo "Token: $TOKEN"
echo "=== 2. Poll (Before Confirmation) ==="
curl -s -i "http://localhost:8000/api/v1/auth/telegram/poll?token=$TOKEN" | grep HTTP
echo "=== 3. Simulate Bot Login ==="
docker compose exec -T redis redis-cli SET "auth:tg:$TOKEN" "confirmed:1234567"
echo "=== 4. Poll (After Confirmation) ==="
curl -s -i "http://localhost:8000/api/v1/auth/telegram/poll?token=$TOKEN" -c cookie.txt | grep -E "HTTP|set-cookie"
echo "=== 5. Get Me (With Cookie) ==="
curl -s -i http://localhost:8000/api/v1/auth/me -b cookie.txt | head -n 1
curl -s http://localhost:8000/api/v1/auth/me -b cookie.txt
echo -e "\n=== 6. Get Me (Without Cookie) ==="
curl -s -i http://localhost:8000/api/v1/auth/me | head -n 1
echo "=== 7. Logout ==="
curl -s -i -X POST http://localhost:8000/api/v1/auth/logout -b cookie.txt -c cookie2.txt | grep -i 'set-cookie'
