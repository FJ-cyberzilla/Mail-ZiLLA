#!/bin/bash
# scripts/deploy_production.sh

set -e

echo "🚀 Starting production deployment..."

# Load environment variables
source /etc/environment

# Variables
APP_NAME="social-intel-app"
DOCKER_REGISTRY="registry.company.com"
VERSION=${1:-latest}
DEPLOY_DIR="/opt/$APP_NAME"
BACKUP_DIR="/backup/$APP_NAME"

# Create backup
echo "📦 Creating backup..."
mkdir -p $BACKUP_DIR
tar -czf "$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz" $DEPLOY_DIR 2>/dev/null || true

# Pull latest images
echo "🔗 Pulling latest images..."
docker pull $DOCKER_REGISTRY/$APP_NAME-api:$VERSION
docker pull $DOCKER_REGISTRY/$APP_NAME-worker:$VERSION
docker pull $DOCKER_REGISTRY/$APP_NAME-nginx:$VERSION

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose -f $DEPLOY_DIR/docker-compose.prod.yml down

# Run database migrations
echo "🗄️ Running database migrations..."
docker run --rm \
  -e DATABASE_URL=$DATABASE_URL \
  $DOCKER_REGISTRY/$APP_NAME-api:$VERSION \
  python manage.py migrate

# Start services
echo "🔧 Starting services..."
docker-compose -f $DEPLOY_DIR/docker-compose.prod.yml up -d

# Health check
echo "🏥 Performing health check..."
sleep 30
curl -f http://localhost:8080/health || {
    echo "❌ Health check failed"
    exit 1
}

# Run post-deployment tasks
echo "🔍 Running post-deployment tasks..."
docker run --rm \
  -e DATABASE_URL=$DATABASE_URL \
  $DOCKER_REGISTRY/$APP_NAME-api:$VERSION \
  python manage.py collectstatic --noinput

echo "✅ Deployment completed successfully!"
