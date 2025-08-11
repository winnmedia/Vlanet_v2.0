# Railway CLI Commands Reference Guide

## Installation & Setup

### Install Railway CLI
```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (PowerShell)
iwr -useb https://railway.app/install.ps1 | iex
```

### Authentication
```bash
# Login to Railway
railway login

# Check current user
railway whoami

# Logout
railway logout
```

## Project Management

### Link Project
```bash
# Link to existing project
railway link

# Link to specific project
railway link [project-id]

# Unlink project
railway unlink
```

### Project Info
```bash
# Show project details
railway status

# List all projects
railway list
```

## Deployment Commands

### Deploy
```bash
# Deploy current directory
railway up

# Deploy with detached mode
railway up --detach

# Deploy specific service
railway up --service backend
```

### Rollback
```bash
# List deployments
railway deployments

# Rollback to previous deployment
railway down
```

## Environment Variables

### View Variables
```bash
# List all variables
railway variables

# List as JSON
railway variables --json

# Get specific variable
railway variables get SECRET_KEY
```

### Set Variables
```bash
# Set single variable
railway variables set KEY=value

# Set multiple variables
railway variables set KEY1=value1 KEY2=value2

# Set from .env file
railway variables set < .env
```

### Delete Variables
```bash
# Delete single variable
railway variables delete KEY

# Delete multiple variables
railway variables delete KEY1 KEY2
```

## Logs & Monitoring

### View Logs
```bash
# Show recent logs
railway logs

# Show last N lines
railway logs --lines 100

# Follow logs (tail -f)
railway logs --tail

# Filter logs
railway logs --filter "ERROR"
```

## Database Operations

### Connect to Database
```bash
# Open database shell
railway connect postgres

# Run SQL command
railway run --service postgres psql -c "SELECT COUNT(*) FROM users_user;"
```

### Database Backups
```bash
# Create backup
railway run pg_dump $DATABASE_URL > backup.sql

# Restore backup
railway run psql $DATABASE_URL < backup.sql
```

## Run Commands in Railway Environment

### Execute Commands
```bash
# Run Python script
railway run python manage.py migrate

# Run shell command
railway run echo $DATABASE_URL

# Run with specific service
railway run --service backend python manage.py shell
```

### Django Management
```bash
# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Collect static files
railway run python manage.py collectstatic --noinput

# Shell access
railway run python manage.py shell

# Database shell
railway run python manage.py dbshell
```

## Service Management

### List Services
```bash
# Show all services
railway services
```

### Restart Service
```bash
# Restart specific service
railway restart backend

# Restart all services
railway restart
```

## Troubleshooting Commands

### Check Status
```bash
# Service health
railway run curl http://localhost:$PORT/api/health/

# Database connection
railway run python -c "import os; print(os.environ.get('DATABASE_URL'))"

# Redis connection
railway run python -c "import os; print(os.environ.get('REDIS_URL'))"
```

### Debug Commands
```bash
# Check Django settings
railway run python -c "from django.conf import settings; print(settings.DEBUG)"

# List installed packages
railway run pip list

# Check Python version
railway run python --version

# Check disk usage
railway run df -h

# Check memory usage
railway run free -m
```

## Common Fix Commands

### Fix 500 Errors
```bash
# Check for migration issues
railway run python manage.py showmigrations

# Force migrate with fake initial
railway run python manage.py migrate --fake-initial

# Check for missing tables
railway run python manage.py dbshell
# Then run: \dt
```

### Fix CORS Issues
```bash
# Set CORS origins
railway variables set CORS_ALLOWED_ORIGINS="https://vlanet.net,https://www.vlanet.net"

# Set allowed hosts
railway variables set ALLOWED_HOSTS="videoplanet.up.railway.app,vlanet.net,www.vlanet.net"
```

### Fix Static Files
```bash
# Collect static files
railway run python manage.py collectstatic --noinput

# Check static files directory
railway run ls -la staticfiles/
```

## Quick Diagnostic Commands

### Full System Check
```bash
# Run all checks
railway run python manage.py check --deploy

# Check specific app
railway run python manage.py check users
```

### Test Endpoints
```bash
# Health check
railway run curl -I http://localhost:$PORT/api/health/

# Test with authentication
railway run curl -X POST http://localhost:$PORT/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

## Emergency Commands

### Force Restart
```bash
# Redeploy latest commit
railway up --detach

# Cancel current deployment
railway cancel
```

### Reset Database (DANGEROUS!)
```bash
# Drop all tables
railway run python manage.py dbshell
# Then: DROP SCHEMA public CASCADE; CREATE SCHEMA public;

# Recreate tables
railway run python manage.py migrate
```

## Best Practices

1. **Always backup before major changes**
   ```bash
   railway run pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql
   ```

2. **Check logs after deployment**
   ```bash
   railway logs --lines 100
   ```

3. **Verify environment variables**
   ```bash
   railway variables --json | jq '.'
   ```

4. **Test locally first**
   ```bash
   railway run --local python manage.py test
   ```

5. **Monitor after changes**
   ```bash
   railway logs --tail
   ```

## Useful Aliases

Add to your shell profile (`.bashrc` or `.zshrc`):

```bash
alias rw='railway'
alias rwup='railway up --detach'
alias rwlogs='railway logs --tail'
alias rwvars='railway variables'
alias rwrun='railway run'
alias rwmigrate='railway run python manage.py migrate'
alias rwshell='railway run python manage.py shell'
```

## Support & Resources

- Railway Documentation: https://docs.railway.app
- Railway Status: https://status.railway.app
- Railway Discord: https://discord.gg/railway
- Support Email: support@railway.app