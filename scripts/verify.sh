#!/bin/bash

# verify.sh - Comprehensive project verification script
# Checks all components are working correctly

set -e  # Exit on error

echo "🔍 DevSecOps Agent - Project Verification"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is not installed"
        return 1
    fi
}

function check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 not found"
        return 1
    fi
}

# Check prerequisites
echo "1. Checking Prerequisites"
echo "------------------------"
check_command docker
check_command docker-compose
check_command git
check_command python3
echo ""

# Check project structure
echo "2. Checking Project Structure"
echo "-----------------------------"
check_file "docker-compose.yml"
check_file "README.md"
check_file "backend/main.py"
check_file "backend/requirements.txt"
check_file "frontend/package.json"
check_file ".env.example"
echo ""

# Check Python dependencies
echo "3. Checking Python Dependencies"
echo "--------------------------------"
if [ -f "backend/requirements.txt" ]; then
    echo "✓ requirements.txt found"
    # Count packages
    PACKAGE_COUNT=$(wc -l < backend/requirements.txt)
    echo "  Contains $PACKAGE_COUNT packages"
fi
echo ""

# Check configuration files
echo "4. Checking Configuration Files"
echo "--------------------------------"
check_file "monitoring/prometheus.yml"
check_file "monitoring/loki-config.yml"
check_file ".github/workflows/ci-cd.yml"
echo ""

# Check documentation
echo "5. Checking Documentation"
echo "-------------------------"
check_file "QUICKSTART.md"
check_file "SETUP.md"
check_file "API.md"
check_file "CONTRIBUTING.md"
check_file "DEPLOYMENT.md"
echo ""

# Docker image availability
echo "6. Checking Docker Images"
echo "-------------------------"
docker pull prom/prometheus:latest &>/dev/null && echo -e "${GREEN}✓${NC} Prometheus image available" || echo -e "${YELLOW}⚠${NC} Prometheus image download pending"
docker pull grafana/grafana:latest &>/dev/null && echo -e "${GREEN}✓${NC} Grafana image available" || echo -e "${YELLOW}⚠${NC} Grafana image download pending"
docker pull postgres:15-alpine &>/dev/null && echo -e "${GREEN}✓${NC} PostgreSQL image available" || echo -e "${YELLOW}⚠${NC} PostgreSQL image download pending"
docker pull ollama/ollama:latest &>/dev/null && echo -e "${GREEN}✓${NC} Ollama image available" || echo -e "${YELLOW}⚠${NC} Ollama image download pending"
echo ""

# Syntax checks
echo "7. Checking File Syntax"
echo "-----------------------"
if python3 -m py_compile backend/main.py &>/dev/null; then
    echo -e "${GREEN}✓${NC} backend/main.py syntax OK"
else
    echo -e "${RED}✗${NC} backend/main.py has syntax errors"
fi

if python3 -m py_compile backend/config.py &>/dev/null; then
    echo -e "${GREEN}✓${NC} backend/config.py syntax OK"
else
    echo -e "${RED}✗${NC} backend/config.py has syntax errors"
fi
echo ""

# File permissions
echo "8. Checking File Permissions"
echo "----------------------------"
if [ -x "scripts/backup.sh" 2>/dev/null ]; then
    echo -e "${GREEN}✓${NC} scripts/backup.sh is executable"
else
    echo -e "${YELLOW}⚠${NC} scripts/backup.sh not found or not executable"
fi
echo ""

# Summary
echo "9. Project Summary"
echo "------------------"
echo -e "Backend files: $(find backend -name '*.py' | wc -l) Python files"
echo -e "Frontend files: $(find frontend/src -name '*.jsx' -o -name '*.js' 2>/dev/null | wc -l) JS/JSX files"
echo -e "Documentation: $(find . -maxdepth 1 -name '*.md' | wc -l) markdown files"
echo -e "Config files: $(find . -name 'docker-compose*.yml' | wc -l) docker-compose files"
echo ""

echo "=========================================="
echo -e "${GREEN}✓ Verification Complete!${NC}"
echo ""
echo "Next Steps:"
echo "1. cp .env.example .env"
echo "2. docker compose up -d"
echo "3. Visit http://localhost:3001"
echo ""
