#!/bin/bash
echo "Starting Social Media App..."

set -a
source .env.prod
set +a

# Build and start
docker compose -f docker-compose.prod.yml up -d --build

echo "App started!"
echo "API: http://$(curl -s ifconfig.me):8000"
echo "Web: http://$(curl -s ifconfig.me):3000"
echo "Health: http://$(curl -s ifconfig.me)/health"