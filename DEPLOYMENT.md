# Deployment Guide

This guide covers deployment options for Airfeeld.

---

## 🎯 Quick Deploy (Fly.io)

Fly.io is recommended for MVP deployment:
- ✅ Free tier available
- ✅ Supports SQLite databases
- ✅ Uses renewable energy
- ✅ Global CDN
- ✅ Easy scaling

### Prerequisites
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login to Fly.io
flyctl auth login
```

### Deploy Backend

1. Create `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/data

# Run migrations and start server
CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8080
```

2. Create `backend/fly.toml`:
```toml
app = "airfeeld-backend"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8080"
  PYTHONPATH = "/app"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

[mounts]
  source = "airfeeld_data"
  destination = "/app/data"
```

3. Deploy:
```bash
cd backend
flyctl launch
flyctl deploy
```

### Deploy Frontend

1. Build frontend:
```bash
cd frontend
npm run build
# Creates dist/ directory
```

2. Create `frontend/Dockerfile`:
```dockerfile
FROM nginx:alpine

# Copy built files
COPY dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

3. Create `frontend/nginx.conf`:
```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass https://airfeeld-backend.fly.dev;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. Deploy:
```bash
cd frontend
flyctl launch
flyctl deploy
```

---

## 🔧 Alternative: Docker Compose

For local or VPS deployment.

### docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - DATABASE_URL=sqlite+aiosqlite:///./data/airfeeld.db
    volumes:
      - ./backend/data:/app/data
      - ./storage:/app/storage
    command: sh -c "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

### Deploy
```bash
docker-compose up -d
```

---

## 🌐 Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./data/airfeeld.db

# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

# Storage
PHOTO_STORAGE_PATH=./storage/photos
MAX_PHOTO_SIZE=10485760  # 10MB

# Security
RATE_LIMIT_PER_IP=60
RATE_LIMIT_WINDOW=60
POW_DIFFICULTY=4
```

### Frontend (.env)
```bash
VITE_API_URL=https://airfeeld-backend.fly.dev
```

---

## 📊 Health Monitoring

### Endpoint
```bash
curl https://your-backend-url.fly.dev/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected"
}
```

### Fly.io Monitoring
```bash
flyctl status
flyctl logs
flyctl metrics
```

---

## 🔒 Security Checklist

Before production deployment:

- [ ] Change default database path
- [ ] Set up HTTPS (handled by Fly.io)
- [ ] Configure CORS for production domain
- [ ] Set up database backups
- [ ] Configure log retention
- [ ] Review rate limits
- [ ] Test PoW difficulty for production load
- [ ] Enable security headers (CSP, HSTS)
- [ ] Review photo storage limits
- [ ] Set up monitoring alerts

---

## 🚀 Performance Optimization

### Backend
- [ ] Enable gzip compression
- [ ] Add API response caching
- [ ] Optimize database indexes
- [ ] Use connection pooling
- [ ] Implement CDN for photos

### Frontend
- [ ] Enable code splitting
- [ ] Lazy load components
- [ ] Optimize images (WebP)
- [ ] Enable service worker
- [ ] Use production build

---

## 📈 Scaling

### Database
- SQLite works up to ~100K requests/day
- For larger scale, migrate to PostgreSQL
- Use `alembic` for schema migrations

### Horizontal Scaling
1. Deploy multiple backend instances
2. Use load balancer (Fly.io handles this)
3. Move photos to object storage (S3, Cloudflare R2)
4. Use Redis for session management

---

## 🐛 Troubleshooting

### Database Issues
```bash
# Check database exists
ls -l backend/data/airfeeld.db

# Run migrations
cd backend
PYTHONPATH=$PWD alembic upgrade head

# Check migration status
alembic current
```

### Backend Not Starting
```bash
# Check logs
flyctl logs

# SSH into container
flyctl ssh console

# Check database connection
python -c "from src.database import get_database; print('OK')"
```

### Frontend Build Issues
```bash
# Clear cache
rm -rf node_modules dist
npm install
npm run build
```

---

## 📝 Maintenance

### Database Backups
```bash
# Local
cp backend/data/airfeeld.db backend/data/airfeeld_backup_$(date +%Y%m%d).db

# Fly.io
flyctl volumes list
flyctl volumes snapshot create <volume-id>
```

### Updates
```bash
# Backend
cd backend
git pull
flyctl deploy

# Frontend
cd frontend
git pull
npm run build
flyctl deploy
```

---

## 🎓 Further Reading

- [Fly.io Documentation](https://fly.io/docs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)
- [SQLite Performance](https://www.sqlite.org/speed.html)

---

**Last Updated**: 2026-02-01
