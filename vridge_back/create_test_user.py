#!/usr/bin/env python3
import os
import sys
import django

# Django 
sys.path.insert(0, '/home/winnmedia/VideoPlanet/vridge_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')
django.setup()

from users.models import User
from django.contrib.auth.hashers import make_password

try:
    #   
    email = "ceo@winnmedia.co.kr"
    password = "Qwerasdf!234"
    
    #   
    user = User.objects.filter(username=email).first()
    if user:
        print(f"  : {email}")
        #  
        user.password = make_password(password)
        user.email_verified = True
        user.save()
        print(" .")
    else:
        #   
        user = User.objects.create(
            username=email,
            email=email,
            nickname="CEO",
            password=make_password(password),
            email_verified=True,
            is_active=True
        )
        print(f"  : {email}")
    
    print(f" :")
    print(f"- Username: {user.username}")
    print(f"- Email: {user.email}")
    print(f"- Nickname: {user.nickname}")
    print(f"- Email Verified: {user.email_verified}")
    print(f"- Is Active: {user.is_active}")
    
except Exception as e:
    print(f" : {e}")
    import traceback
    traceback.print_exc()