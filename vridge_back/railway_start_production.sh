#!/bin/bash
# Railway Production Start Script with CORS fix

echo "Starting Railway Production Server with CORS fix..."

# Set environment variables for production
export DJANGO_SETTINGS_MODULE=config.settings.railway
export PYTHONUNBUFFERED=1
export DJANGO_DEBUG=False

# Ensure CORS is properly configured
export CORS_ALLOW_ALL_ORIGINS=False
export CORS_ALLOW_CREDENTIALS=True

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create cache table if needed
echo "Setting up cache..."
python manage.py createcachetable 2>/dev/null || true

# Start Gunicorn with proper configuration
echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${WEB_CONCURRENCY:-2} \
    --worker-class sync \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --timeout 120 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s' \
    --forwarded-allow-ips="*" \
    --proxy-protocol \
    --proxy-allow-from="*"