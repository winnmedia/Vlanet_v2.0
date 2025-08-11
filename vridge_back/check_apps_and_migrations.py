#!/usr/bin/env python
"""Railway        """
import os
import sys
import django

# Django   
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

# Django 
django.setup()

from django.conf import settings
from django.apps import apps

print("=== Django Apps Configuration Check ===")
print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
print(f"DEBUG: {settings.DEBUG}")
print(f"SECRET_KEY exists: {bool(settings.SECRET_KEY)}")
print(f"\nINSTALLED_APPS ({len(settings.INSTALLED_APPS)} apps):")

# INSTALLED_APPS 
for app in settings.INSTALLED_APPS:
    print(f"  - {app}")

print("\n=== App Registry Check ===")
#    
loaded_apps = apps.get_app_configs()
print(f"Loaded apps ({len(loaded_apps)}):")
for app_config in loaded_apps:
    has_migrations = os.path.exists(os.path.join(app_config.path, 'migrations'))
    print(f"  - {app_config.label} ({app_config.name}) - has migrations: {has_migrations}")

print("\n=== Migration Status ===")
#   
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())

if plan:
    print(f"Pending migrations ({len(plan)}):")
    for migration, backwards in plan:
        print(f"  - {migration}")
else:
    print("All migrations are applied!")

#   
print("\n=== Checking Specific Apps ===")
for app_name in ['users', 'projects', 'feedbacks', 'video_planning']:
    try:
        app_config = apps.get_app_config(app_name)
        migrations_path = os.path.join(app_config.path, 'migrations')
        print(f"\n{app_name}:")
        print(f"  - Path: {app_config.path}")
        print(f"  - Migrations path exists: {os.path.exists(migrations_path)}")
        if os.path.exists(migrations_path):
            migration_files = [f for f in os.listdir(migrations_path) if f.endswith('.py') and f != '__init__.py']
            print(f"  - Migration files: {len(migration_files)}")
            for mf in sorted(migration_files)[:5]:  #  5 
                print(f"    - {mf}")
    except Exception as e:
        print(f"\n{app_name}: ERROR - {e}")

print("\n=== Database Tables Check ===")
#   
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename
    """)
    tables = cursor.fetchall()
    print(f"Database tables ({len(tables)}):")
    for table in tables:
        print(f"  - {table[0]}")