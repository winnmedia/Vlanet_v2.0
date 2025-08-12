# Railway Deployment Guide

## Overview
This guide provides comprehensive instructions for deploying the VideoPlanet backend to Railway, including troubleshooting common issues and monitoring procedures.

## Pre-Deployment Checklist

### 1. Environment Variables
Ensure the following environment variables are set in Railway:

**Required:**
- `DATABASE_URL` - PostgreSQL connection string (automatically set by Railway)
- `SECRET_KEY` - Django secret key (generate a secure one)

**Optional but Recommended:**
- `REDIS_URL` - Redis connection string for caching
- `DEBUG` - Set to `False` for production
- `RAILWAY_ENVIRONMENT` - Set to `production`
- `EMAIL_HOST_USER` - Email service username
- `EMAIL_HOST_PASSWORD` - Email service password

### 2. Pre-Deployment Validation
Run the validation script before deploying:

```bash
cd vridge_back
./scripts/pre_deploy_check.sh
```

This will check:
- Python syntax errors
- Missing dependencies
- Django configuration
- Database connectivity
- Static files setup

## Deployment Process

### 1. Code Preparation
```bash
# Ensure all changes are committed
git status

# Run local tests
python manage.py test

# Validate deployment readiness
python scripts/validate_deployment.py
```

### 2. Push to Railway
```bash
# Add Railway remote (if not already added)
git remote add railway <your-railway-git-url>

# Push to Railway
git push railway main
```

### 3. Post-Deployment Verification
After Railway finishes deploying:

```bash
# Check deployment health
curl https://videoplanet.up.railway.app/api/system/health/

# Monitor for 5 minutes
python scripts/monitor_deployment.py --duration 300
```

## Common Issues and Solutions

### Issue 1: ModuleNotFoundError
**Error:** `ModuleNotFoundError: No module named 'module_name'`

**Solution:**
1. Check if the module is in `requirements.txt`
2. Verify import paths are absolute, not relative
3. Ensure `__init__.py` files exist in all packages

**Preventive Measure:** 
- Consolidated `video_analysis/urls.py` to avoid import errors
- Use absolute imports in production code

### Issue 2: Static Files Not Found
**Error:** `UserWarning: No directory at: /vridge_front/build/`

**Solution:**
1. Static files are now configured to check multiple paths
2. WhiteNoise handles static file serving
3. Frontend should be deployed separately to Vercel

**Configuration:**
```python
# Railway will check these paths in order:
1. /app/vridge_back/static
2. /app/vridge_front/build/static (if exists)
3. Railway-specific paths
```

### Issue 3: Database Connection Errors
**Error:** `OperationalError: could not connect to server`

**Solution:**
1. Verify `DATABASE_URL` is set correctly
2. Check PostgreSQL addon is provisioned
3. Connection pooling is disabled to prevent Railway timeouts

### Issue 4: Health Check Failures
**Error:** Railway health check returning 500

**Solution:**
1. Use the basic health check endpoint: `/api/system/health/?basic=true`
2. Configure Railway health check:
   - Path: `/api/system/health/`
   - Method: GET
   - Timeout: 30s

## Monitoring

### Health Check Endpoints
- `/api/system/health/` - Comprehensive health check
- `/api/system/health/?basic=true` - Basic health check (for Railway)
- `/api/system/health/ready/` - Readiness check
- `/api/system/health/live/` - Liveness check

### Continuous Monitoring
```bash
# Monitor for 1 hour with checks every minute
python scripts/monitor_deployment.py --duration 3600 --interval 60

# Single health check
python scripts/monitor_deployment.py --once
```

### Monitoring Metrics
The health check provides:
- Database connectivity status
- Cache availability
- Disk space usage
- Memory usage
- Configuration validation
- Static files status

## Rollback Procedure

If deployment fails or causes issues:

1. **Immediate Rollback:**
   ```bash
   # In Railway dashboard
   # Go to Deployments > Select previous working deployment > Rollback
   ```

2. **Local Fix:**
   ```bash
   # Fix the issue locally
   # Run validation
   python scripts/validate_deployment.py
   
   # Test thoroughly
   python manage.py test
   
   # Deploy fix
   git push railway main
   ```

## Best Practices

### 1. Always Validate Before Deploying
```bash
./scripts/pre_deploy_check.sh
```

### 2. Use Environment-Specific Settings
- Local: `config/settings_dev.py`
- Railway: `config/settings/railway.py`

### 3. Monitor After Deployment
```bash
python scripts/monitor_deployment.py --duration 600
```

### 4. Keep Dependencies Updated
```bash
pip list --outdated
pip-compile requirements.in
```

### 5. Document Changes
Update `MEMORY.md` with deployment-related decisions

## Troubleshooting Commands

```bash
# Check Django configuration
python manage.py check

# Show migration status
python manage.py showmigrations

# Collect static files
python manage.py collectstatic --noinput

# Test database connection
python -c "from django.db import connection; cursor = connection.cursor(); cursor.execute('SELECT 1')"

# Validate all imports
python scripts/validate_deployment.py
```

## Support

For deployment issues:
1. Check Railway logs in the dashboard
2. Run monitoring script: `python scripts/monitor_deployment.py --once`
3. Review this guide's troubleshooting section
4. Check `MEMORY.md` for previous solutions

## Version History

- **v1.0** (2025-08-13): Initial deployment guide
- Fixed ModuleNotFoundError in video_analysis
- Improved static file handling
- Added comprehensive health checks
- Created validation and monitoring scripts

---

Last Updated: 2025-08-13
Maintained by: Backend Lead