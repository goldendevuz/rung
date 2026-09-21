#!/bin/bash
mkdir -p /home/kai/projects/rung/docs/screenshots/d1/routes
docker run --rm --network host \
  -v /home/kai/projects/rung/scripts:/scripts:ro \
  -v /home/kai/projects/rung/docs/screenshots/d1/routes:/shots \
  mcr.microsoft.com/playwright:v1.46.0-jammy \
  bash -c "mkdir -p /tmp/pw && cd /tmp/pw && npm init -y -q 2>/dev/null && npm install @playwright/test@1.46.0 --no-package-lock -q && cp /scripts/screenshot_routes.js . && node screenshot_routes.js"
