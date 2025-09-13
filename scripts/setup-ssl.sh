#!/bin/bash

# SSL Certificate Setup Script for Survey360
# This script helps you set up SSL certificates for production

set -e

DOMAIN="leadershipremedy.com"
SSL_DIR="./nginx/ssl"

echo "🔐 SSL Certificate Setup for Survey360"
echo "======================================"

# Check if running as root (needed for Let's Encrypt)
if [[ $EUID -eq 0 ]]; then
    echo "✅ Running as root"
else
    echo "⚠️  This script should be run as root for Let's Encrypt"
    echo "   You can run: sudo ./scripts/setup-ssl.sh"
fi

echo ""
echo "Choose SSL certificate option:"
echo "1. Let's Encrypt (Free, Automatic, Recommended for production)"
echo "2. Self-signed certificate (For testing only)"
echo "3. Upload your own certificates"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "📋 Setting up Let's Encrypt certificates..."
        echo "Prerequisites:"
        echo "- Domain $DOMAIN must point to this server"
        echo "- Port 80 must be accessible from internet"
        echo "- Email for notifications is required"
        echo ""
        read -p "Continue with Let's Encrypt? (y/n): " confirm
        
        if [[ $confirm == "y" || $confirm == "Y" ]]; then
            # Install certbot if not present
            if ! command -v certbot &> /dev/null; then
                echo "Installing certbot..."
                if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                    apt-get update && apt-get install -y certbot
                elif [[ "$OSTYPE" == "darwin"* ]]; then
                    brew install certbot
                else
                    echo "Please install certbot manually for your OS"
                    exit 1
                fi
            fi
            
            read -p "Enter email for Let's Encrypt notifications: " email
            
            # Stop nginx if running
            docker compose -f docker-compose.prod.yml stop nginx 2>/dev/null || true
            
            # Get certificate
            certbot certonly --standalone \
                --email $email \
                --agree-tos \
                --no-eff-email \
                -d $DOMAIN \
                -d www.$DOMAIN
            
            # Copy certificates to nginx directory
            cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $SSL_DIR/cert.pem
            cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $SSL_DIR/key.pem
            
            echo "✅ Let's Encrypt certificates installed"
            echo "📋 To auto-renew, add this to crontab:"
            echo "0 12 * * * /usr/bin/certbot renew --quiet && docker compose -f docker-compose.prod.yml restart nginx"
        fi
        ;;
        
    2)
        echo ""
        echo "🔧 Creating self-signed certificate for testing..."
        
        # Create self-signed certificate
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout $SSL_DIR/key.pem \
            -out $SSL_DIR/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
        
        echo "✅ Self-signed certificate created"
        echo "⚠️  Warning: Self-signed certificates are not trusted by browsers"
        ;;
        
    3)
        echo ""
        echo "📁 Upload your own certificates..."
        echo "Place your certificate files in $SSL_DIR/:"
        echo "- Certificate: $SSL_DIR/cert.pem"
        echo "- Private key: $SSL_DIR/key.pem"
        echo ""
        echo "Certificate file should include the full chain (certificate + intermediate certificates)"
        ;;
        
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Set proper permissions
chmod 644 $SSL_DIR/cert.pem 2>/dev/null || true
chmod 600 $SSL_DIR/key.pem 2>/dev/null || true

echo ""
echo "🎉 SSL setup complete!"
echo "You can now start the production environment with:"
echo "docker compose -f docker-compose.prod.yml up -d"