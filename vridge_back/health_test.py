#!/usr/bin/env python3
"""
Railway   
"""
import os
import sys
import django
import time
import json

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
django.setup()

from django.test import Client
from django.db import connection

def test_health_endpoint():
    """  """
    print("=== Railway   ===")
    
    client = Client()
    
    # 1.   
    print("\n1.   (/api/health/)")
    try:
        response = client.get('/api/health/')
        print(f"    : {response.status_code}")
        print(f"   : {response.json()}")
        print(f"    " if response.status_code == 200 else "    ")
    except Exception as e:
        print(f"    : {str(e)}")
    
    # 2.   
    print("\n2.   (/api/health-full/)")
    try:
        response = client.get('/api/health-full/')
        print(f"    : {response.status_code}")
        data = response.json()
        print(f"   : {data.get('service')}")
        print(f"   : {data.get('status')}")
        print(f"   : {data.get('database')}")
        print(f"   : {data.get('environment')}")
        print(f"    " if response.status_code == 200 else "    ")
    except Exception as e:
        print(f"    : {str(e)}")
    
    # 3.   
    print("\n3.   ")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        print(f"      ")
    except Exception as e:
        print(f"      : {str(e)}")
    
    # 4.   
    print("\n4.    (10)")
    times = []
    for i in range(10):
        start = time.time()
        response = client.get('/api/health/')
        elapsed = (time.time() - start) * 1000  # ms
        times.append(elapsed)
        print(f"    {i+1}: {elapsed:.2f}ms")
    
    avg_time = sum(times) / len(times)
    print(f"     : {avg_time:.2f}ms")
    print(f"   {' ' if avg_time < 100 else ' '}")
    
    # 5.  
    print("\n5.   ")
    env_vars = {
        'SECRET_KEY': bool(os.environ.get('SECRET_KEY')),
        'DATABASE_URL': bool(os.environ.get('DATABASE_URL')),
        'PORT': os.environ.get('PORT', 'Not set'),
        'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set')
    }
    
    for var, value in env_vars.items():
        if isinstance(value, bool):
            print(f"   {var}: {' ' if value else ' '}")
        else:
            print(f"   {var}: {value}")
    
    print("\n===   ===")

if __name__ == '__main__':
    test_health_endpoint()