# Survey360 Production Deployment Guide

## 🚀 Production Deployment Steps

### Prerequisites

1. **Server Requirements**
   - Ubuntu 20.04+ or CentOS 8+ server
   - Minimum 2GB RAM, 20GB disk space
   - Docker and Docker Compose installed
   - Domain name pointing to your server
   - Port 80 and 443 open in firewall

2. **Domain Setup**
   - Update DNS records to point to your server IP
   - Configure both `yourdomain.com` and `www.yourdomain.com`

### Step 1: Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Logout and login again to apply docker group
```

### Step 2: Deploy Application

```bash
# Clone repository
git clone <your-repo-url> survey360
cd survey360

# Create required directories
mkdir -p logs backups nginx/ssl

# Configure production environment
cp .env.production .env.production.local
```

### Step 3: Configure Environment Variables

Edit `.env.production.local`:

```bash
# CRITICAL: Change these values for production
SECRET_KEY=GENERATE_A_NEW_64_CHARACTER_SECRET_KEY
DB_PASSWORD=GENERATE_A_SECURE_DATABASE_PASSWORD
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Update email settings
EMAIL_HOST_USER=your-email@yourdomain.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Update domain
DEFAULT_DOMAIN=https://yourdomain.com
```

### Step 4: Set Up SSL Certificates

```bash
# Option 1: Let's Encrypt (Recommended)
sudo ./scripts/setup-ssl.sh

# Option 2: Upload your own certificates
# Place cert.pem and key.pem in nginx/ssl/
```

### Step 5: Deploy Production Environment

```bash
# Start production services
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

### Step 6: Initial Setup

```bash
# Create admin user (if not created automatically)
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Test the application
curl -k https://yourdomain.com/admin/
```

## 🔧 Production Management

### Daily Operations

```bash
# Check system health
./scripts/monitor.sh

# View logs
docker compose -f docker-compose.prod.yml logs web --tail=50

# Restart services
docker compose -f docker-compose.prod.yml restart web
```

### Database Backup

```bash
# Manual backup
docker compose -f docker-compose.prod.yml run --rm backup

# Set up automated backups (add to crontab)
0 2 * * * cd /path/to/survey360 && docker compose -f docker-compose.prod.yml run --rm backup
```

### Updates and Maintenance

```bash
# Update application
git pull origin main
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d

# Database migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
```

## 🛡️ Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong database password
- [ ] Set up SSL certificates
- [ ] Configure firewall (UFW/iptables)
- [ ] Set up fail2ban for brute force protection
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity

## 📊 Monitoring

### Health Checks

```bash
# Automated monitoring
./scripts/monitor.sh

# Check individual services
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs nginx
```

### Log Files

- **Application logs**: `logs/gunicorn-*.log`
- **Nginx logs**: `logs/nginx/`
- **Docker logs**: `docker compose logs`

### Performance Monitoring

```bash
# Resource usage
docker stats

# Database performance
docker compose -f docker-compose.prod.yml exec db psql -U survey360_user-production -d survey360_production -c "SELECT * FROM pg_stat_activity;"
```

## 🔄 Backup and Recovery

### Automated Backups

```bash
# Set up daily backups
echo "0 2 * * * cd /path/to/survey360 && docker compose -f docker-compose.prod.yml run --rm backup" | crontab -
```

### Manual Backup

```bash
docker compose -f docker-compose.prod.yml run --rm backup
```

### Restore from Backup

```bash
./scripts/restore.sh
```

## 🚨 Troubleshooting

### Common Issues

1. **SSL Certificate Issues**
   ```bash
   # Check certificate
   openssl x509 -in nginx/ssl/cert.pem -text -noout
   
   # Renew Let's Encrypt
   sudo certbot renew
   ```

2. **Database Connection Issues**
   ```bash
   # Check database status
   docker compose -f docker-compose.prod.yml exec db pg_isready
   
   # Check database logs
   docker compose -f docker-compose.prod.yml logs db
   ```

3. **Application Errors**
   ```bash
   # Check application logs
   docker compose -f docker-compose.prod.yml logs web
   
   # Django shell access
   docker compose -f docker-compose.prod.yml exec web python manage.py shell
   ```

### Emergency Procedures

1. **Service Down**
   ```bash
   # Restart all services
   docker compose -f docker-compose.prod.yml restart
   
   # Check system resources
   df -h
   free -h
   ```

2. **Database Recovery**
   ```bash
   # Restore from latest backup
   ./scripts/restore.sh
   ```

## 📈 Scaling

### Horizontal Scaling

- Use load balancer (HAProxy/nginx)
- Deploy multiple web containers
- External database service (AWS RDS, etc.)

### Vertical Scaling

```yaml
# Increase resources in docker-compose.prod.yml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

## 🔐 Security Best Practices

1. **Server Hardening**
   - Disable root SSH login
   - Use SSH keys instead of passwords
   - Configure fail2ban
   - Regular security updates

2. **Application Security**
   - Strong SECRET_KEY
   - HTTPS only
   - Regular dependency updates
   - Monitor security advisories

3. **Database Security**
   - Strong passwords
   - Network isolation
   - Regular backups
   - Encryption at rest

## 📞 Support

For issues:
1. Check logs first
2. Run health check script
3. Check documentation
4. Contact system administrator

---

**Remember**: Always test in staging environment before production deployment!