cd /home/kai/projects/rung
docker run --rm --network host -v \C:\/deploy/audit/find_scroll.mjs:/tmp/pw/find_scroll.mjs mcr.microsoft.com/playwright:v1.46.0-jammy bash -c 'mkdir -p /tmp/pw && cd /tmp/pw && npm init -y -q 2>/dev/null && npm install playwright@1.46.0 -q && node find_scroll.mjs'
