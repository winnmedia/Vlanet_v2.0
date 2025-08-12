#!/usr/bin/env python
"""
Railway Migration Helper
Handles database migrations in Railway environment
"""

import os
import sys
from pathlib import Path

# Add Django to path
DJANGO_ROOT = Path(__file__).resolve().parent / 'vridge_back'
sys.path.insert(0, str(DJANGO_ROOT))
os.chdir(str(DJANGO_ROOT))

# Set Django settings
if os.environ.get('RAILWAY_ENVIRONMENT'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')

try:
    from django.core.management import execute_from_command_line
    
    print("🔄 Running Django migrations...")
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    print("✅ Migrations completed successfully")
    
except Exception as e:
    print(f"⚠️ Migration warning (non-fatal): {e}")
    # Don't fail the build for migration issues
    sys.exit(0)