#!/bin/bash
# scripts/monitor_services.sh

#!/bin/bash
# scripts/monitor_services.sh

set -e

echo "🔍 Starting service monitoring..."

# Configuration
ALERT_EMAIL="alerts@company.com"
LOG_FILE="/var/log/service-monitor.log"
SERVICES=("api" "worker" "redis" "postgres" "nginx")

# Function to check service health
check_service() {
    local service=$1
    
    case $service in
        "api")
            curl -f http://localhost:8000/health >/dev/null 2>&1
            ;;
        "worker")
            pgrep -f "celery worker" >/dev/null
            ;;
        "redis")
            redis-cli ping >/dev/null 2>&1
            ;;
        "postgres")
            pg_isready -h localhost -p 5432 >/dev/null 2>&1
            ;;
        "nginx")
            systemctl is-active --quiet nginx
            ;;
    esac
    
    return $?
}

# Function to send alert
send_alert() {
    local service=$1
    local message="ALERT: Service $service is down at $(date)"
    
    echo "$message" >> $LOG_FILE
    echo "$message" | mail -s "Service Alert: $service" $ALERT_EMAIL
    
    # Also send to Slack if configured
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$message\"}" \
            $SLACK_WEBHOOK >/dev/null 2>&1
    fi
}

# Function to restart service
restart_service() {
    local service=$1
    
    echo "🔄 Restarting service: $service"
    
    case $service in
        "api"|"worker")
            docker-compose -f /opt/social-intel-app/docker-compose.prod.yml restart $service
            ;;
        "redis"|"postgres")
            docker-compose -f /opt/social-intel-app/docker-compose.prod.yml restart $service
            ;;
        "nginx")
            systemctl restart nginx
            ;;
    esac
}

# Main monitoring loop
for service in "${SERVICES[@]}"; do
    if ! check_service $service; then
        echo "❌ Service $service is down"
        send_alert $service
        restart_service $service
        
        # Verify restart worked
        sleep 10
        if check_service $service; then
            echo "✅ Service $service recovered"
        else
            echo "🚨 CRITICAL: Service $service failed to recover"
        fi
    else
        echo "✅ Service $service is healthy"
    fi
done

# System resource monitoring
echo "📊 System resources:"
echo "CPU: $(top -bn1 | grep load | awk '{printf "%.2f\n", $(NF-2)}')"
echo "Memory: $(free -m | awk 'NR==2{printf "%.2f%%\n", $3*100/$2}')"
echo "Disk: $(df -h / | awk 'NR==2{print $5}')"

echo "✅ Monitoring completed at $(date)"
