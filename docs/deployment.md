# Deployment Guide

**Airfeeld - Production Deployment**

This guide covers deploying Airfeeld to production with security and privacy best practices.

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- SQLite 3.35+ (or PostgreSQL 13+ for scaling)
- Reverse proxy (nginx/Caddy)
- TLS certificate
- 2GB RAM minimum
- 20GB storage minimum

## Environment Configuration

### Backend Environment Variables

Create `/backend/.env`:

```bash
# Application
APP_ENV=production
APP_DEBUG=false
APP_VERSION=1.0.0
SECRET_KEY=<generate-strong-random-key>

# Database
DATABASE_URL=sqlite:///data/airfeeld.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost/airfeeld

# Storage
PHOTO_STORAGE_PATH=../storage/photos
PHOTO_CACHE_PATH=../storage/cache

# Security
POW_DIFFICULTY=6
POW_ACCESSIBILITY_DIFFICULTY=4
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# CORS (adjust for your domain)
CORS_ORIGINS=https://airfeeld.com,https://www.airfeeld.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/airfeeld.log
```

### Frontend Environment Variables

Create `/frontend/.env.production`:

```bash
VITE_API_BASE_URL=https://api.airfeeld.com
VITE_APP_VERSION=1.0.0
```

## Backend Deployment

### 1. Install Dependencies

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Database Migrations

```bash
alembic upgrade head
```

### 3. Verify Database Encryption

If using SQLCipher for SQLite encryption:

```bash
# Install SQLCipher
# macOS: brew install sqlcipher
# Ubuntu: apt-get install sqlcipher

# Set encryption key in environment
export SQLITE_ENCRYPTION_KEY="your-encryption-key-here"

# Test connection
sqlcipher data/airfeeld.db "PRAGMA key='your-encryption-key-here'; SELECT 1;"
```

### 4. Production Server Setup

#### Option A: Uvicorn with Systemd

Create `/etc/systemd/system/airfeeld-api.service`:

```ini
[Unit]
Description=Airfeeld API Service
After=network.target

[Service]
Type=notify
User=airfeeld
Group=airfeeld
WorkingDirectory=/opt/airfeeld/backend
Environment="PATH=/opt/airfeeld/backend/venv/bin"
EnvironmentFile=/opt/airfeeld/backend/.env
ExecStart=/opt/airfeeld/backend/venv/bin/uvicorn src.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 4 \
    --log-config logging.yaml

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable airfeeld-api
sudo systemctl start airfeeld-api
sudo systemctl status airfeeld-api
```

#### Option B: Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 airfeeld && \
    chown -R airfeeld:airfeeld /app

USER airfeeld

# Run migrations and start server
CMD alembic upgrade head && \
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Build and run:

```bash
docker build -t airfeeld-api .
docker run -d \
    --name airfeeld-api \
    -p 127.0.0.1:8000:8000 \
    -v /opt/airfeeld/data:/app/data \
    -v /opt/airfeeld/storage:/app/storage \
    --env-file .env \
    --restart unless-stopped \
    airfeeld-api
```

## Frontend Deployment

### 1. Build Production Bundle

```bash
cd frontend
npm install
npm run build
```

Output: `dist/` directory

### 2. Deploy Static Files

#### Option A: nginx

```nginx
server {
    listen 443 ssl http2;
    server_name airfeeld.com www.airfeeld.com;
    
    ssl_certificate /etc/letsencrypt/live/airfeeld.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/airfeeld.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
    
    # Content Security Policy
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://api.airfeeld.com" always;
    
    root /opt/airfeeld/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Compression
    gzip on;
    gzip_types text/css application/javascript application/json image/svg+xml;
    gzip_min_length 1000;
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name airfeeld.com www.airfeeld.com;
    return 301 https://$server_name$request_uri;
}
```

#### Option B: Caddy (Automatic HTTPS)

`Caddyfile`:

```
airfeeld.com {
    root * /opt/airfeeld/frontend/dist
    encode gzip
    file_server
    
    # SPA fallback
    try_files {path} /index.html
    
    # API proxy
    handle_path /api/* {
        reverse_proxy localhost:8000
    }
    
    # Security headers
    header {
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "no-referrer"
        Permissions-Policy "geolocation=(), microphone=(), camera=()"
    }
}
```

## Database Maintenance

### Backup Strategy

```bash
#!/bin/bash
# /opt/airfeeld/scripts/backup.sh

BACKUP_DIR="/opt/airfeeld/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Stop API temporarily (optional)
# systemctl stop airfeeld-api

# SQLite backup
sqlite3 /opt/airfeeld/backend/data/airfeeld.db ".backup '$BACKUP_DIR/airfeeld_$DATE.db'"

# Compress
gzip "$BACKUP_DIR/airfeeld_$DATE.db"

# Start API
# systemctl start airfeeld-api

# Delete backups older than 30 days
find $BACKUP_DIR -name "airfeeld_*.db.gz" -mtime +30 -delete
```

Schedule with cron:

```cron
0 2 * * * /opt/airfeeld/scripts/backup.sh
```

### Audit Log Archival

```bash
# Archive logs older than 6 months to cold storage
# Run monthly
0 0 1 * * /opt/airfeeld/backend/venv/bin/python -m src.scripts.archive_audit_logs
```

## Monitoring

### Health Checks

```bash
# Add to cron or monitoring service
curl -f https://api.airfeeld.com/health || alert-team
```

### Log Rotation

`/etc/logrotate.d/airfeeld`:

```
/opt/airfeeld/backend/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 airfeeld airfeeld
    sharedscripts
    postrotate
        systemctl reload airfeeld-api
    endscript
}
```

## Security Checklist

- [ ] TLS certificate installed and auto-renewing
- [ ] Database encrypted at rest (SQLCipher or PostgreSQL encryption)
- [ ] Environment variables secured (not in git)
- [ ] File permissions: 600 for .env, 700 for data directory
- [ ] Rate limiting enabled
- [ ] OWASP security headers configured
- [ ] Regular backups automated
- [ ] Log rotation configured
- [ ] Firewall rules: only 80/443 exposed
- [ ] Non-root user for services
- [ ] System updates automated

## Performance Tuning

### Database Optimization

For SQLite:
```sql
-- Set cache size (in KB)
PRAGMA cache_size = -64000;

-- Enable WAL mode
PRAGMA journal_mode = WAL;

-- Optimize performance
PRAGMA synchronous = NORMAL;
```

### Uvicorn Workers

Rule of thumb: `workers = (2 * CPU_cores) + 1`

For 2 CPU cores: 5 workers
For 4 CPU cores: 9 workers

## Scaling Considerations

When to migrate to PostgreSQL:
- More than 100 concurrent users
- More than 100,000 game rounds
- Database file exceeds 2GB

When to add Redis:
- Rate limiting needs to scale horizontally
- Session management required
- Real-time features added

## Troubleshooting

### API Won't Start

```bash
# Check logs
journalctl -u airfeeld-api -n 50

# Test configuration
cd /opt/airfeeld/backend
source venv/bin/activate
python -m src.main
```

### Database Locked

```bash
# Check for stale connections
fuser data/airfeeld.db

# If using SQLite, consider PostgreSQL for high concurrency
```

### High Memory Usage

```bash
# Monitor
htop
# Or
docker stats airfeeld-api

# Reduce workers if needed
```

## Support

- Documentation: https://github.com/airfeeld/airfeeld/docs
- Issues: https://github.com/airfeeld/airfeeld/issues
- Security: security@airfeeld.com (PGP key available)
