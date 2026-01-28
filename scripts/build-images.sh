#!/bin/bash
# Build Docker images for Sentinel ML

set -e

echo "🐳 Building Sentinel Docker images..."
echo ""

# Ensure we're in project root
cd "$(dirname "$0")/.."

# Build inference API image
echo "Building inference API image..."
docker build -f infra/Dockerfile.inference -t sentinel-inference:latest .
echo "✅ sentinel-inference:latest built"

# Build consumer image
echo ""
echo "Building consumer image..."
docker build -f infra/Dockerfile.consumer -t sentinel-consumer:latest .
echo "✅ sentinel-consumer:latest built"

# Tag for Minikube (if running)
if minikube status &gt; /dev/null 2&gt;&1; then
    echo ""
    echo "📦 Loading images into Minikube..."
    minikube image load sentinel-inference:latest
    minikube image load sentinel-consumer:latest
    echo "✅ Images loaded into Minikube"
fi

echo ""
echo "✅ All images built successfully!"
echo ""
echo "Images:"
echo "  - sentinel-inference:latest"
echo "  - sentinel-consumer:latest"
