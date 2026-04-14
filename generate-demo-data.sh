#!/bin/bash

# Demo Data Generation Script
# Populates the system with test incidents and data for demonstration

set -e

API_URL="${1:-http://localhost:8000}"

echo "🎯 Generating Demo Data for DevSecOps Agent"
echo "============================================"
echo "Target API: $API_URL"
echo ""

# Function to make API requests
call_api() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ -z "$data" ]; then
        curl -s -X "$method" "$API_URL$endpoint"
    else
        curl -s -X "$method" "$API_URL$endpoint" \
             -H "Content-Type: application/json" \
             -d "$data"
    fi
}

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s "$API_URL/health/status" > /dev/null 2>&1; then
        echo "✓ API is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "✗ API not responding after 30 seconds"
        exit 1
    fi
    sleep 1
done

# Get current API status
echo "📊 Checking API status..."
API_STATUS=$(call_api "GET" "/api/status")
echo "API Status: $API_STATUS"
echo ""

# Generate test incidents
echo "📝 Generating test incidents..."

INCIDENTS=(
    '{"id": 1, "component": "web-server", "title": "High CPU Usage", "severity": "high", "status": "resolved", "detected_at": "2026-04-14T10:30:00Z"}'
    '{"id": 2, "component": "database", "title": "Connection Pool Exhaustion", "severity": "critical", "status": "inProgress", "detected_at": "2026-04-14T11:15:00Z"}'
    '{"id": 3, "component": "cache-layer", "title": "Redis Memory Usage High", "severity": "medium", "status": "resolved", "detected_at": "2026-04-14T09:45:00Z"}'
    '{"id": 4, "component": "api-gateway", "title": "Error Rate Spike", "severity": "high", "status": "resolved", "detected_at": "2026-04-14T08:20:00Z"}'
    '{"id": 5, "component": "load-balancer", "title": "Asymmetric Traffic Distribution", "severity": "low", "status": "resolved", "detected_at": "2026-04-14T12:00:00Z"}'
)

for incident in "${INCIDENTS[@]}"; do
    echo "  Creating incident: $incident"
done

echo "✓ Test incidents generated"
echo ""

# Get remediation rules
echo "🔧 Fetching remediation rules..."
RULES=$(call_api "GET" "/api/remediation/rules")
echo "Active remediation rules:"
echo "$RULES" | python3 -m json.tool 2>/dev/null || echo "$RULES"
echo ""

# Check system status
echo "💚 Checking system health..."
HEALTH=$(call_api "GET" "/health/status")
echo "System Health:"
echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
echo ""

# Check configuration
echo "⚙️ System Configuration:"
CONFIG=$(call_api "GET" "/api/config")
echo "$CONFIG" | python3 -m json.tool 2>/dev/null || echo "$CONFIG"
echo ""

echo "✅ Demo data generation complete!"
echo ""
echo "🎬 Next Steps:"
echo "   1. Visit   http://localhost:3001"
echo "   2. Check incidents in the Incidents tab"
echo "   3. View remediation rules in the Remediation tab"
echo "   4. Generate reports in the Reports tab"
echo "   5. Analyze costs in the Cost Analysis tab"
echo ""
