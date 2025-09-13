#!/bin/bash

# Database Backup Script for Survey360
# This script creates automated backups of the PostgreSQL database

set -e

# Configuration
DB_NAME="survey360_production"
DB_USER="survey360_user-production"
DB_HOST="db"
BACKUP_DIR="/backups"
RETENTION_DAYS=${POSTGRES_BACKUP_RETENTION_DAYS:-7}

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Generate backup filename with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/survey360_backup_$TIMESTAMP.sql"

echo "🗄️  Starting database backup..."
echo "Database: $DB_NAME"
echo "Backup file: $BACKUP_FILE"

# Create the backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME --no-password > $BACKUP_FILE

# Compress the backup
gzip $BACKUP_FILE
BACKUP_FILE="${BACKUP_FILE}.gz"

# Verify backup was created
if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✅ Backup created successfully: $BACKUP_FILE ($BACKUP_SIZE)"
else
    echo "❌ Backup failed!"
    exit 1
fi

# Clean up old backups (keep only last N days)
echo "🧹 Cleaning up old backups (keeping last $RETENTION_DAYS days)..."
find $BACKUP_DIR -name "survey360_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

# List current backups
echo "📋 Current backups:"
ls -lah $BACKUP_DIR/survey360_backup_*.sql.gz 2>/dev/null || echo "No backups found"

echo "🎉 Backup process completed!"