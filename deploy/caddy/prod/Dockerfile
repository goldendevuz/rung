FROM node:20-alpine AS builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --legacy-peer-deps
COPY frontend/ ./
ENV NODE_OPTIONS=--max-old-space-size=1024
RUN npm run build

FROM caddy:2-alpine
COPY deploy/caddy/prod/Caddyfile /etc/caddy/Caddyfile
COPY --from=builder /app/dist /srv/www
