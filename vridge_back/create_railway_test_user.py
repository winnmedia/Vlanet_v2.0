#!/usr/bin/env python3
"""
Railway     
"""
import os
import sys
import django

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from users.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone

def create_test_user():
    """  """
    try:
        #   
        User.objects.filter(username='test@videoplanet.com').delete()
        print("   ")
        
        #   
        user = User.objects.create(
            username='test@videoplanet.com',
            email='test@videoplanet.com',
            nickname='',
            is_active=True,
            email_verified=True,
            email_verified_at=timezone.now(),
            login_method='email'
        )
        
        #  
        user.set_password('test1234')
        user.save()
        
        print(f"   !")
        print(f"- : {user.username}")
        print(f"- : {user.email}")
        print(f"- : test1234")
        print(f"- : {user.is_active}")
        print(f"-  : {user.email_verified}")
        
        #    
        from django.db import connection
        print(f"\n :")
        print(f"- : {connection.vendor}")
        print(f"-  : {connection.settings_dict.get('NAME', 'N/A')}")
        
    except Exception as e:
        print(f" : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_user()