#!/bin/bash
docker run --rm --network host \
  -v /home/kai/projects/rung/deploy/shots:/tmp/shots:ro \
  -v /home/kai/projects/rung/docs/screenshots/s1:/shots \
  mcr.microsoft.com/playwright:v1.46.0-jammy \
  bash -c "mkdir -p /tmp/pw && cd /tmp/pw && npm init -y -q 2>/dev/null && npm install @playwright/test@1.46.0 --no-package-lock -q && cp /tmp/shots/screenshot_tab.js . && cp /tmp/shots/mock_tab.html . && node screenshot_tab.js"
