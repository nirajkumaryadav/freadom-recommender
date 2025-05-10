#!/bin/bash
# Docker deployment script for Freadom Recommender
# This script builds and runs the Docker containers for the Freadom Recommender system

echo "=== Freadom Recommender Docker Deployment ==="
echo "Building Docker images..."

# Build API container
echo "Building API container..."
docker build -t freadom-api -f Dockerfile.api .

# Build Streamlit container
echo "Building Streamlit container..."
docker build -t freadom-streamlit -f Dockerfile.streamlit .

# Run the containers
echo "Starting containers..."
docker-compose up -d

echo "Deployment complete!"
echo "API is available at: http://localhost:5000"
echo "UI is available at: http://localhost:8501"
