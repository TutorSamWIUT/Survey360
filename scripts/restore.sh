#!/bin/bash

# Database Restore Script for Survey360
# This script restores the PostgreSQL database from a backup

set -e

# Configuration
DB_NAME="survey360_production"
DB_USER="survey360_user-production"
DB_HOST="db"
BACKUP_DIR="/backups"

echo "🔄 Database Restore for Survey360"
echo "================================="

# List available backups
echo "Available backups:"
ls -lah $BACKUP_DIR/survey360_backup_*.sql.gz 2>/dev/null || {
    echo "❌ No backup files found in $BACKUP_DIR"
    exit 1
}

echo ""
read -p "Enter the backup filename (without path): " BACKUP_FILENAME

BACKUP_FILE="$BACKUP_DIR/$BACKUP_FILENAME"

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo ""
echo "⚠️  WARNING: This will replace all data in the database!"
echo "Database: $DB_NAME"
echo "Backup file: $BACKUP_FILE"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Restore cancelled"
    exit 1
fi

echo "🗄️  Starting database restore..."

# Stop the web application
echo "Stopping web application..."
docker compose -f docker-compose.prod.yml stop web

# Drop and recreate database
echo "Recreating database..."
docker compose -f docker-compose.prod.yml exec -T db psql -U $DB_USER -c "DROP DATABASE IF EXISTS $DB_NAME;"
docker compose -f docker-compose.prod.yml exec -T db psql -U $DB_USER -c "CREATE DATABASE $DB_NAME;"

# Restore from backup
echo "Restoring backup..."
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c $BACKUP_FILE | docker compose -f docker-compose.prod.yml exec -T db psql -U $DB_USER -d $DB_NAME
else
    cat $BACKUP_FILE | docker compose -f docker-compose.prod.yml exec -T db psql -U $DB_USER -d $DB_NAME
fi

# Start the web application
echo "Starting web application..."
docker compose -f docker-compose.prod.yml start web

echo "✅ Database restore completed successfully!"
echo "🔍 You may want to check the application logs:"
echo "docker compose -f docker-compose.prod.yml logs web"