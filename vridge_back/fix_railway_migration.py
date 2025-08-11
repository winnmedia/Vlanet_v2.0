#!/usr/bin/env python3
"""
Railway      
"""
import os
import sys
import django

# Django 
sys.path.insert(0, '/home/winnmedia/VideoPlanet/vridge_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection

print(" Railway    ")
print("="*50)

#    
with connection.cursor() as cursor:
    #   
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'video_planning'
        ORDER BY ordinal_position;
    """)
    columns = cursor.fetchall()
    
    print("\n video_planning  :")
    for col in columns:
        print(f"  - {col[0]}")
    
    # color_tone    
    color_tone_exists = any('color_tone' in col for col in columns)
    print(f"\ncolor_tone  : {color_tone_exists}")

#   
print("\n  :")
execute_from_command_line(['manage.py', 'showmigrations', 'video_planning'])

#    
print("\n:")
print("1.  ")
print("2.  fake  (   )")
print("3.   ")
print("4. ")

# Railway   1 
if os.environ.get('RAILWAY_ENVIRONMENT'):
    print("\nRailway  .   ...")
    execute_from_command_line(['manage.py', 'migrate', 'video_planning'])
    print("  !")