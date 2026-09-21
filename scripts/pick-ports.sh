#!/bin/bash
set -e

ENV_FILE=".env"
touch $ENV_FILE

# Function to check if a port is in use
is_port_in_use() {
    local port=$1
    if ss -ltn | grep -qE "(:$port\b)" || docker ps --format '{{.Ports}}' | grep -qE "(:$port->)"; then
        return 0
    else
        return 1
    fi
}

# Function to get a free port starting from a base port
get_free_port() {
    local base_port=$1
    local port=$base_port
    while is_port_in_use $port; do
        port=$((port + 1))
    done
    echo $port
}

# Ensure variable is set in .env with a free port
ensure_free_port() {
    local var_name=$1
    local default_port=$2

    # Read current value from .env
    local current_port=$(grep "^${var_name}=" $ENV_FILE | cut -d '=' -f2)

    if [ -n "$current_port" ] && ! is_port_in_use "$current_port"; then
        # Already set and free, keep it
        return
    fi

    local free_port=$(get_free_port $default_port)

    # Replace or append in .env
    if grep -q "^${var_name}=" $ENV_FILE; then
        sed -i "s/^${var_name}=.*/${var_name}=${free_port}/" $ENV_FILE
    else
        echo "${var_name}=${free_port}" >> $ENV_FILE
    fi
    echo "Assigned $var_name=$free_port"
}

ensure_free_port HTTP_PORT 80
ensure_free_port HTTPS_PORT 443
ensure_free_port FRONTEND_HOST_PORT 5173
ensure_free_port BACKEND_HOST_PORT 8000
ensure_free_port POSTGRES_HOST_PORT 5432
ensure_free_port REDIS_HOST_PORT 6379
