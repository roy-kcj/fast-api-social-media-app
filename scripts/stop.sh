#!/bin/bash
echo "Stopping Social Media App..."
docker compose -f docker-compose.prod.yml --env-file .env.prod down
echo "App stopped!"