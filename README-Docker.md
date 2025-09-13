# Survey360 Docker Setup

## Quick Start

1. **Build and start the containers:**
   ```bash
   docker compose up --build -d
   ```

2. **Access the application:**
   - Web Application: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin/
   - Default admin credentials: `admin` / `admin123`

3. **PostgreSQL Database:**
   - Host: localhost
   - Port: 5433 (external), 5432 (internal)
   - Database: survey360_db
   - Username: survey360_user
   - Password: survey360_password

## Container Services

### Database Container (PostgreSQL 15)
- **Container Name:** `survey360_db`
- **Image:** `postgres:15`
- **Port Mapping:** `5433:5432`
- **Volume:** `postgres_data` for persistent storage
- **Health Check:** Automatically checks database readiness

### Web Application Container (Django)
- **Container Name:** `survey360_web`
- **Built from:** Local Dockerfile
- **Port Mapping:** `8000:8000`
- **Volumes:** 
  - `static_volume` for static files
  - `media_volume` for media uploads

## Commands

### Start the application:
```bash
docker compose up -d
```

### Stop the application:
```bash
docker compose down
```

### View logs:
```bash
# All services
docker compose logs

# Specific service
docker compose logs web
docker compose logs db
```

### Rebuild containers:
```bash
docker compose up --build -d
```

### Reset everything (delete volumes):
```bash
docker compose down -v
docker compose up --build -d
```

### Access Django shell:
```bash
docker compose exec web python manage.py shell
```

### Run Django management commands:
```bash
# Create migrations
docker compose exec web python manage.py makemigrations

# Apply migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Collect static files
docker compose exec web python manage.py collectstatic
```

## Environment Configuration

The application uses `.env.docker` for environment variables:

- **DEBUG:** Set to `True` for development
- **SECRET_KEY:** Change for production use
- **Database settings:** Pre-configured for Docker containers
- **ALLOWED_HOSTS:** Includes localhost and container IPs

## File Structure

```
Survey360/
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Django app container definition
├── docker-entrypoint.sh        # Container startup script
├── .dockerignore              # Files to exclude from build
├── .env.docker                # Environment variables
└── requirements.txt           # Python dependencies
```

## Features

- **Automatic database setup:** PostgreSQL with persistent volumes
- **Auto-migration:** Runs database migrations on startup
- **Auto-superuser:** Creates admin user automatically
- **Static files:** Automatically collected and served
- **Health checks:** Database health monitoring
- **Development ready:** Pre-configured for local development

## Production Notes

For production deployment:
1. Change `DEBUG=False` in `.env.docker`
2. Update `SECRET_KEY` with a secure value
3. Configure proper email settings
4. Update `ALLOWED_HOSTS` with your domain
5. Consider using a reverse proxy (nginx)
6. Set up SSL/TLS certificates