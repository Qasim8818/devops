#!/bin/bash

# DevSecOps Agent - Complete Startup & Demo Script
# This script sets up and tests all system components

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 DevSecOps Agent - Complete System Setup"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print with color
info() {
  echo -e "${BLUE}ℹ ${1}${NC}"
}

success() {
  echo -e "${GREEN}✓ ${1}${NC}"
}

warning() {
  echo -e "${YELLOW}⚠ ${1}${NC}"
}

error() {
  echo -e "${RED}✗ ${1}${NC}"
}

# Check if Docker is installed
info "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    error "Docker is not installed. Please install Docker first."
    exit 1
fi
success "Docker is installed"

# Check if Docker Compose is installed
info "Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
success "Docker Compose is installed"

# Start Docker if not running
info "Ensuring Docker daemon is running..."
if ! docker ps > /dev/null 2>&1; then
    error "Docker daemon is not running. Please start Docker."
    exit 1
fi
success "Docker is running"

# Create required directories
info "Creating required directories..."
mkdir -p backend
mkdir -p frontend/src
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources
success "Directories created"

# Build images
info "Building Docker images (this may take a few minutes)..."
docker-compose build --no-cache

success "Docker images built successfully"

# Start services
info "Starting DevSecOps Agent services..."
docker-compose up -d

# Wait for services to be healthy
info "Waiting for services to be healthy..."
sleep 10

# Check service status
info "Checking service status..."

SERVICES=("prometheus" "grafana" "loki" "ollama" "devsecops-api" "devsecops-dashboard" "devsecops-db")

for service in "${SERVICES[@]}"; do
    if docker ps | grep -q "$service"; then
        success "$service is running"
    else
        warning "$service is not running yet (may still be starting)"
    fi
done

# Test API endpoint
info "Testing API connectivity..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        success "Backend API is responding"
        break
    fi
    if [ $i -eq 30 ]; then
        warning "Backend API not responding yet (it may be initializing)"
    fi
    sleep 2
done

echo ""
echo "🎉 DevSecOps Agent Started!"
echo ""
echo "📊 Service URLs:"
echo "   Dashboard: http://localhost:3001"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Grafana:   http://localhost:3000 (admin/admin)"
echo "   Prometheus: http://localhost:9090"
echo "   Ollama:    http://localhost:11434"
echo ""
echo "⚡ Quick Commands:"
echo "   View logs:     docker-compose logs -f backend"
echo "   Stop services: docker-compose down"
echo "   Remove data:   docker-compose down -v"
echo ""
echo "✅ System is ready! Opening dashboard..."
echo ""

# Give user time to read
sleep 2

# Open dashboard in browser if possible
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3001
elif command -v open &> /dev/null; then
    open http://localhost:3001
fi

echo "🔗 Access the dashboard at: http://localhost:3001"
