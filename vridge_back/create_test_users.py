#!/usr/bin/env python
"""
VideoPlanet    
: python create_test_users.py
"""

import os
import sys
import django

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_base')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

User = get_user_model()

def create_test_users():
    """  """
    
    test_users = [
        {
            'username': 'test@test.com',
            'email': 'test@test.com',
            'nickname': 'TestUser',
            'password': 'Test1234!@',
            'is_staff': False,
            'is_superuser': False
        },
        {
            'username': 'admin@test.com',
            'email': 'admin@test.com',
            'nickname': 'AdminUser',
            'password': 'Admin1234!@',
            'is_staff': True,
            'is_superuser': True
        },
        {
            'username': 'demo@test.com',
            'email': 'demo@test.com',
            'nickname': 'DemoUser',
            'password': 'Demo1234!@',
            'is_staff': False,
            'is_superuser': False
        }
    ]
    
    created_users = []
    
    with transaction.atomic():
        for user_data in test_users:
            username = user_data['username']
            
            #   
            if User.objects.filter(username=username).exists():
                print(f"   : {username}")
                user = User.objects.get(username=username)
                #  
                user.set_password(user_data['password'])
                user.save()
                created_users.append(user)
            else:
                #   
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password']
                )
                user.nickname = user_data['nickname']
                user.is_staff = user_data['is_staff']
                user.is_superuser = user_data['is_superuser']
                user.is_active = True
                
                #   
                if hasattr(user, 'email_verified'):
                    user.email_verified = True
                    user.email_verified_at = timezone.now()
                
                #   
                if hasattr(user, 'login_method'):
                    user.login_method = 'email'
                
                user.save()
                created_users.append(user)
                print(f"   : {username}")
    
    print("\n===    ===")
    for user in created_users:
        print(f"- : {user.email}")
        print(f"  : {user.nickname}")
        print(f"  : {'' if user.is_staff else ''}")
        print(f"  : {'' if user.is_active else ''}")
        print()
    
    return created_users

if __name__ == '__main__':
    print("VideoPlanet    ...")
    create_test_users()
    print("!")