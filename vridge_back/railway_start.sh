#!/bin/bash
# Railway startup script with proper error handling

echo "Starting Railway deployment..."

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput || echo "Migration failed, continuing..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Static collection failed, continuing..."

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 30 \
    --access-logfile - \
    --error-logfile - \
    --log-level info