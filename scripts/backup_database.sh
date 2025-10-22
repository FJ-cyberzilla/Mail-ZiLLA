#!/bin/bash
# scripts/backup_database.sh

set -e

echo "💾 Starting database backup..."

# Configuration
BACKUP_DIR="/backup/database"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Ensure backup directory exists
mkdir -p $BACKUP_DIR

# PostgreSQL backup
echo "📊 Backing up PostgreSQL..."
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
  --format=custom \
  --verbose \
  --file="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump"

# Redis backup
echo "🔴 Backing up Redis..."
redis-cli --rdb "$BACKUP_DIR/redis_${TIMESTAMP}.rdb"

# Compress backups
echo "🗜️ Compressing backups..."
tar -czf "$BACKUP_DIR/backup_${TIMESTAMP}.tar.gz" \
  "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump" \
  "$BACKUP_DIR/redis_${TIMESTAMP}.rdb"

# Cleanup temporary files
rm "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump"
rm "$BACKUP_DIR/redis_${TIMESTAMP}.rdb"

# Clean old backups
echo "🧹 Cleaning old backups..."
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "✅ Backup completed: $BACKUP_DIR/backup_${TIMESTAMP}.tar.gz"
