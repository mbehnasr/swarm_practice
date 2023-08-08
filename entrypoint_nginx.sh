#!/bin/bash

# Function to check if a service is ready
# Usage: wait_for_service <hostname> <port>
wait_for_service() {
  local host="$1"
  local port="$2"
  local max_attempts=30
  local attempt=0
  local wait_interval=2

  while ! nc -z "$host" "$port" >/dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge "$max_attempts" ]; then
      echo "Service $host:$port did not become available after $((max_attempts * wait_interval)) seconds. Exiting..."
      exit 1
    fi
    echo "Waiting for $host:$port to be ready... (Attempt $attempt of $max_attempts)"
    sleep "$wait_interval"
  done
}

# Wait for required services to be ready
wait_for_service account 8000
wait_for_service shop 8000
wait_for_service order 8000

# Start Nginx
echo "All required services are ready. Starting Nginx..."
exec nginx -g "daemon off;"
while true ; do
  echo "fuckme"
  sleep 10s
done
