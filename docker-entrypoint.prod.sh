#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Survey360 Production Deployment...${NC}"

# Wait for PostgreSQL
echo -e "${YELLOW}Waiting for PostgreSQL...${NC}"
while ! nc -z db 5432; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo -e "${GREEN}PostgreSQL started${NC}"

# Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python manage.py migrate --noinput

# Create superuser if it doesn't exist (only in production setup)
echo -e "${YELLOW}Checking for superuser...${NC}"
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Creating production superuser...')
    User.objects.create_superuser('admin', 'admin@leadershipremedy.com', 'CHANGE_THIS_PASSWORD_IN_PRODUCTION')
    print('Production superuser created')
else:
    print('Superuser already exists')
" || echo -e "${RED}Error creating superuser${NC}"

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Start Gunicorn with production settings
echo -e "${GREEN}Starting Gunicorn server...${NC}"
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class sync \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --log-level info \
    --access-logfile /app/logs/gunicorn-access.log \
    --error-logfile /app/logs/gunicorn-error.log \
    --capture-output \
    principal360_survey.wsgi:application