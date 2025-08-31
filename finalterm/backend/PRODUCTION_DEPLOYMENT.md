# Production Deployment Guide

## Critical Security Requirements

### 1. Environment Variables (MUST BE SET)

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random

# Host Configuration
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-vercel-app.vercel.app

# CORS and CSRF (Must match your frontend domain)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://your-vercel-app.vercel.app
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://your-vercel-app.vercel.app

# Database (Use your production database URL)
DATABASE_URL=postgresql://username:password@host:port/database_name

# Redis (For WebSocket support)
REDIS_URL=redis://username:password@host:port
```

### 2. Security Features Enabled in Production

- ✅ HTTPS redirect enforced
- ✅ Security headers (HSTS, XSS protection, etc.)
- ✅ Secure cookies (HTTPS only)
- ✅ CSRF protection
- ✅ CORS restrictions
- ✅ Host validation
- ✅ Production logging

### 3. Vercel Deployment Checklist

- [ ] Set all environment variables in Vercel dashboard
- [ ] Configure build command: `pip install -r requirements.txt`
- [ ] Set output directory: `staticfiles`
- [ ] Configure Python version (3.10+)
- [ ] Set `PYTHONPATH` to project root
- [ ] Configure `vercel.json` for Django routing

### 4. Database Setup

- Use PostgreSQL or MySQL (not SQLite for production)
- Set up connection pooling
- Configure backups
- Monitor performance

### 5. Redis Setup (for WebSockets)

- Use managed Redis service (Redis Cloud, AWS ElastiCache)
- Configure authentication
- Set up monitoring

### 6. Static Files

- Configure `STATIC_ROOT` and `STATIC_URL`
- Use CDN for better performance
- Enable compression

### 7. Monitoring and Logging

- Set up error tracking (Sentry)
- Configure application monitoring
- Set up log aggregation
- Monitor security events

## Current Security Status

✅ **Good:**
- DEBUG defaults to False
- SECRET_KEY validation
- Production security headers
- HTTPS enforcement
- Secure cookie settings

⚠️ **Requires Configuration:**
- Environment variables must be set
- Database connection
- Redis connection
- CORS origins
- CSRF trusted origins

❌ **Not Production Ready Until:**
- All environment variables are configured
- Database is migrated and tested
- Static files are collected
- SSL certificate is configured
- Monitoring is set up
