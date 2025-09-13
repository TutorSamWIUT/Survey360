#!/bin/bash

# Monitoring Script for Survey360
# This script checks the health of all services

set -e

echo "🔍 Survey360 Production Health Check"
echo "===================================="

# Check if Docker Compose is running
if ! docker compose -f docker-compose.prod.yml ps >/dev/null 2>&1; then
    echo "❌ Docker Compose not running or not found"
    exit 1
fi

# Check individual services
services=("db" "web" "nginx")
all_healthy=true

for service in "${services[@]}"; do
    echo -n "Checking $service... "
    
    # Check if container is running
    if docker compose -f docker-compose.prod.yml ps $service | grep -q "Up"; then
        echo "✅ Running"
        
        # Additional health checks
        case $service in
            "db")
                if docker compose -f docker-compose.prod.yml exec -T db pg_isready -U survey360_user-production >/dev/null 2>&1; then
                    echo "  📊 Database responding"
                else
                    echo "  ⚠️  Database not responding"
                    all_healthy=false
                fi
                ;;
            "web")
                if curl -s -f http://localhost/admin/ >/dev/null 2>&1; then
                    echo "  🌐 Web application responding"
                else
                    echo "  ⚠️  Web application not responding"
                    all_healthy=false
                fi
                ;;
            "nginx")
                if curl -s -f http://localhost/health/ >/dev/null 2>&1; then
                    echo "  🔗 Nginx responding"
                else
                    echo "  ⚠️  Nginx not responding"
                    all_healthy=false
                fi
                ;;
        esac
    else
        echo "❌ Not running"
        all_healthy=false
    fi
done

echo ""

# Check disk space
echo "💾 Disk Usage:"
df -h | grep -E "/$|/var"

echo ""

# Check memory usage
echo "🧠 Memory Usage:"
free -h

echo ""

# Check recent logs for errors
echo "📋 Recent Error Logs:"
docker compose -f docker-compose.prod.yml logs --tail=10 web 2>&1 | grep -i error || echo "No recent errors found"

echo ""

# SSL certificate expiry check
if [ -f "./nginx/ssl/cert.pem" ]; then
    echo "🔐 SSL Certificate:"
    expiry_date=$(openssl x509 -in ./nginx/ssl/cert.pem -noout -enddate | cut -d= -f2)
    expiry_timestamp=$(date -d "$expiry_date" +%s 2>/dev/null || echo "0")
    current_timestamp=$(date +%s)
    days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
    
    if [ $days_until_expiry -gt 30 ]; then
        echo "  ✅ Valid until $expiry_date ($days_until_expiry days)"
    elif [ $days_until_expiry -gt 0 ]; then
        echo "  ⚠️  Expires soon: $expiry_date ($days_until_expiry days)"
    else
        echo "  ❌ Expired: $expiry_date"
        all_healthy=false
    fi
else
    echo "🔐 SSL Certificate: Not found"
fi

echo ""

# Overall status
if [ "$all_healthy" = true ]; then
    echo "🎉 All services are healthy!"
    exit 0
else
    echo "⚠️  Some services need attention"
    exit 1
fi