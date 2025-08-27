# 🚀 Deployment Guide

## 📋 Files Created

✅ **Dockerfile** - For local Docker development
✅ **docker-compose.yml** - Local development with SQLite + Redis + Static files
✅ **.dockerignore** - Exclude unnecessary files from Docker build
✅ **nginx.conf** - Nginx configuration for static files
✅ **render.yaml** - Render deployment configuration

## 🐳 Local Development with Docker

### Start Local Environment:
```bash
# Build and start all services (basic setup)
docker-compose up --build

# Or run with Nginx for better static file serving
docker-compose --profile production up --build

# Or run in background
docker-compose up -d --build

# View logs
docker-compose logs web

# Stop services
docker-compose down
```

### Access Your App:
- **Django App**: http://localhost:8000 (basic setup)
- **With Nginx**: http://localhost (better static files)
- **Redis**: localhost:6379

### Static Files in Docker:
- ✅ **Automatic collection**: `python manage.py collectstatic` runs on startup
- ✅ **Volume mounting**: Static files persist between container restarts
- ✅ **Nginx serving**: Optional Nginx for better performance
- ✅ **Media files**: Properly served and cached

## ☁️ Deploy to Render

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Create new account

### Step 2: Add PostgreSQL Service
1. Click "New +"
2. Select "PostgreSQL"
3. Name: "elearning-db"
4. Database: "elearning"
5. User: "elearning_user"
6. Click "Create Database"
7. Copy connection details

### Step 3: Add Redis Service
1. Click "New +"
2. Select "Redis"
3. Name: "elearning-redis"
4. Click "Create Redis"
5. Copy connection details

### Step 4: Deploy Django App
1. Click "New +"
2. Select "Web Service"
3. Connect your GitHub repo
4. Name: "elearning-app"
5. Environment: "Python 3"
6. Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
7. Start Command: `daphne -b 0.0.0.0 -p $PORT elearning_project.asgi:application`
8. Click "Create Web Service"

### Step 5: Set Environment Variables
In your web service settings, add:
```bash
DATABASE_URL=postgresql://elearning_user:password@host:port/elearning
REDIS_URL=redis://username:password@host:port
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=.onrender.com
```

### Step 6: Run Migrations
```bash
# In Render dashboard, go to your web service
# Click "Shell" and run:
python manage.py migrate
python manage.py createsuperuser
```

## 🔧 Environment Setup

### Local (Docker):
- **Database**: SQLite (built-in)
- **Redis**: Docker container
- **Server**: Daphne in Docker
- **Static Files**: Collected and served by Django/Nginx
- **Media Files**: Properly handled and cached

### Production (Render):
- **Database**: PostgreSQL (Render provides)
- **Redis**: Redis (Render provides)
- **Server**: Daphne (Render runs)
- **Static Files**: Collected during build, served by Render
- **Media Files**: Handled by Django

## 📝 Commands to Run

### Install Dependencies:
```bash
pip install psycopg2-binary dj-database-url gunicorn
pip freeze > requirements.txt
```

### Test Local Docker:
```bash
# Basic setup (Django serves static files)
docker-compose up --build

# With Nginx (better performance)
docker-compose --profile production up --build
```

### Deploy to Render:
```bash
git add .
git commit -m "Add deployment configuration with static files"
git push
# Render auto-deploys
```

## 🎯 What You Get

✅ **Local Development**: Docker with SQLite + Redis + Static files
✅ **Production Deployment**: Render with PostgreSQL + Redis
✅ **Multi-user Support**: No more SQLite limitations
✅ **Professional Hosting**: Bonus points for deployment
✅ **Static File Handling**: Proper CSS/JS serving in both environments
✅ **Easy Scaling**: Render handles everything

## 🚨 Important Notes

- **Don't use Docker on Render** - Render handles everything
- **Local Docker**: For development only
- **Static Files**: Automatically collected in Docker, manually in Render
- **Nginx**: Optional for local development (better performance)
- **Environment Variables**: Set in Render dashboard
- **Migrations**: Run after deployment

## 🆘 Troubleshooting

### Local Docker Issues:
```bash
# Clean rebuild
docker-compose down -v
docker-compose up --build

# Check logs
docker-compose logs web

# Static files not loading?
docker-compose exec web python manage.py collectstatic --noinput
```

### Static File Issues:
```bash
# Check if static files exist
docker-compose exec web ls -la staticfiles/

# Rebuild static files
docker-compose exec web python manage.py collectstatic --noinput --clear
```

### Render Issues:
- Check build logs in Render dashboard
- Verify environment variables
- Ensure requirements.txt is up to date
- Check service health status
- Verify static files are collected during build
