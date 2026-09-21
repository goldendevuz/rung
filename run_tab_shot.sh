#!/bin/bash
docker run --rm --network host \
  -v /home/kai/projects/rung/deploy/shots/tab_shot.js:/tmp/tab_shot.js:ro \
  -v /home/kai/projects/rung/docs/screenshots/s1:/shots \
  mcr.microsoft.com/playwright:v1.46.0-jammy \
  bash -c "mkdir -p /tmp/pw && cd /tmp/pw && npm init -y -q 2>/dev/null && npm install @playwright/test@1.46.0 --no-package-lock -q && cp /tmp/tab_shot.js . && apt-get update && apt-get install -y scrot xvfb && xvfb-run -s '-screen 0 1024x768x24' node tab_shot.js"
