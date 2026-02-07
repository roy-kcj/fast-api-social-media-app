#!/bin/bash
echo "Starting Social Media App..."

# Pull latest images
docker compose -f docker-compose.prod.yml --env-file .env.prod pull

# Start containers
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

echo "App started!"
echo "API: http://${PUBLIC_IP}:8000"
echo "Web: http://${PUBLIC_IP}:3000"
echo "Health: http://${PUBLIC_IP}/health"
echo "API Docs: http://${PUBLIC_IP}:8000/docs"
echo "Run './scripts/logs.sh' to view logs"