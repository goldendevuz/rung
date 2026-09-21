FROM node:20-alpine AS builder
ARG VITE_PUBLIC_BASE_URL=https://rung.uz
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --legacy-peer-deps
COPY frontend/ ./
ENV NODE_OPTIONS=--max-old-space-size=1024
ENV VITE_PUBLIC_BASE_URL=$VITE_PUBLIC_BASE_URL
RUN npm run build

FROM caddy:2-alpine
COPY deploy/caddy/prod/Caddyfile /etc/caddy/Caddyfile
COPY --from=builder /app/dist /srv/www
