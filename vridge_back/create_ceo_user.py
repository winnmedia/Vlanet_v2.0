#!/usr/bin/env python3
import os
import sys
import django

# Django 
sys.path.insert(0, '/home/winnmedia/VideoPlanet/vridge_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

#    
email = "ceo@winnmedia.co.kr"
password = "Qwerasdf!234"

try:
    user = User.objects.get(username=email)
    print(f"  : {user.username}")
    user.set_password(password)
    user.is_active = True
    user.save()
    print("  ")
except User.DoesNotExist:
    user = User.objects.create(
        username=email,
        email=email,
        nickname="CEO",
        is_active=True
    )
    user.set_password(password)
    user.save()
    print(f"   : {user.username}")

#  
print(f"\n :")
print(f"ID: {user.id}")
print(f"Username: {user.username}")
print(f"Email: {user.email}")
print(f"Active: {user.is_active}")
print(f"Password check: {user.check_password(password)}")

#   
print("\n  :")
for u in User.objects.all():
    print(f"- {u.username} (ID: {u.id}, Active: {u.is_active})")