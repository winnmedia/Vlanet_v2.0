#!/usr/bin/env python3
import os
import sys
import django

# Django 
sys.path.insert(0, '/home/winnmedia/VideoPlanet/vridge_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')
django.setup()

from django.core.cache import cache
from users.models import User

try:
    #    
    user = User.objects.filter(username="ceo@winnmedia.co.kr").first()
    if user:
        cache_key = f"project_list_{user.id}"
        cache.delete(cache_key)
        print(f" '{cache_key}' .")
        
        #    
        cache.delete("all_projects")
        print("   .")
    else:
        print("   .")
        
except Exception as e:
    print(f" : {e}")
    import traceback
    traceback.print_exc()