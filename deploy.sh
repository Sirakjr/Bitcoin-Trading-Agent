#!/bin/bash

# Bitcoin Trading Agent Deployment Script
set -e

echo "🚀 Deploying Bitcoin Trading Agent..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy env.example to .env and configure it."
    exit 1
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t bitcoin-trading-agent:latest .

# Stop existing container if running
echo "🛑 Stopping existing container..."
docker stop bitcoin-trading-agent 2>/dev/null || true
docker rm bitcoin-trading-agent 2>/dev/null || true

# Run the new container
echo "▶️ Starting new container..."
docker run -d \
    --name bitcoin-trading-agent \
    --restart unless-stopped \
    --env-file .env \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/logs:/app/logs" \
    bitcoin-trading-agent:latest

# Wait a moment for container to start
sleep 5

# Check container status
echo "📊 Container status:"
docker ps --filter name=bitcoin-trading-agent

echo "✅ Deployment complete!"
echo "📝 View logs with: docker logs -f bitcoin-trading-agent"
echo "🛑 Stop with: docker stop bitcoin-trading-agent"
