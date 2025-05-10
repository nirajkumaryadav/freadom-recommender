# Simplified Docker deployment script for Freadom Recommender (Windows PowerShell)

Write-Host "=== Freadom Recommender Simplified Docker Deployment ==="

# Use the simple docker-compose file
Write-Host "Starting containers with simplified configuration..."
docker-compose -f docker-compose.simple.yml up -d

Write-Host "Deployment complete!"
Write-Host "API is available at: http://localhost:5000"
Write-Host "Simplified UI is available at: http://localhost:8501"
