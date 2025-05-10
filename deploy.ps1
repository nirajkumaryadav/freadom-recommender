# Docker deployment script for Freadom Recommender (Windows PowerShell)

Write-Host "=== Freadom Recommender Docker Deployment =="
Write-Host "Building Docker images..."

# Build API container
Write-Host "Building API container..."
docker build -t freadom-api -f Dockerfile.api .

# Build Streamlit container
Write-Host "Building Streamlit container..."
docker build -t freadom-streamlit -f Dockerfile.streamlit .

# Run the containers
Write-Host "Starting containers..."
docker-compose up -d

Write-Host "Deployment complete!"
Write-Host "API is available at: http://localhost:5000"
Write-Host "UI is available at: http://localhost:8501"
