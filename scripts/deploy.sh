#!/bin/bash

DOCKER_USERNAME="rckay"

echo "🔨 Building and pushing Docker images..."
echo "Docker Hub username: $DOCKER_USERNAME"
echo ""

# Build and push API
echo "Building API image..."
docker build -t $DOCKER_USERNAME/social-api:latest ./backend
if [ $? -ne 0 ]; then
    echo "API build failed"
    exit 1
fi

echo "Pushing API image..."
docker push $DOCKER_USERNAME/social-api:latest
if [ $? -ne 0 ]; then
    echo "API push failed. Run 'docker login' first."
    exit 1
fi

# Build and push Web
echo "Building Web image..."
docker build -t $DOCKER_USERNAME/social-web:latest ./frontend
if [ $? -ne 0 ]; then
    echo "Web build failed"
    exit 1
fi

echo "Pushing Web image..."
docker push $DOCKER_USERNAME/social-web:latest
if [ $? -ne 0 ]; then
    echo "Web push failed"
    exit 1
fi