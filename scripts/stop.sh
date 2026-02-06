#!/bin/bash
echo "Stopping Social Media App..."
docker compose -f docker-compose.prod.yml down
echo "App stopped!"