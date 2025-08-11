#!/usr/bin/env python
import os
import sys
import django

# Django  
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.railway")
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, identify_hasher

User = get_user_model()

def check_user_issues():
    """   """
    
    print("=" * 80)
    print("    ")
    print("=" * 80)
    
    users = User.objects.all().order_by('-date_joined')[:20]
    
    problematic_users = []
    
    for user in users:
        print(f"\n[{user.username}]")
        print(f"  - ID: {user.id}")
        print(f"  - Email : {user.email if user.email else '()'}")
        print(f"  - Nickname: {getattr(user, 'nickname', 'N/A')}")
        print(f"  - Login Method: {getattr(user, 'login_method', 'N/A')}")
        print(f"  - Is Active: {user.is_active}")
        print(f"  - Has Usable Password: {user.has_usable_password()}")
        print(f"  - Date Joined: {user.date_joined}")
        
        #   
        if user.password:
            try:
                hasher = identify_hasher(user.password)
                print(f"  - Password Hasher: {hasher.__class__.__name__}")
            except:
                print(f"  - Password Hasher:    ()")
                problematic_users.append(user.username)
        else:
            print(f"  - Password: ()")
            problematic_users.append(user.username)
        
        # email   
        if user.username and '@' in user.username and not user.email:
            print(f"    : username   email  ")
            problematic_users.append(user.username)
    
    print("\n" + "=" * 80)
    print("    :")
    print("=" * 80)
    
    if problematic_users:
        for username in set(problematic_users):
            print(f"  - {username}")
            
        print("\n :")
        print("1. email   : username  ")
        print("2.    :  ")
        print("3. login_method   : 'email' ")
    else:
        print("     .")
    
    #      
    print("\n" + "=" * 80)
    print("    :")
    print("=" * 80)
    
    #    
    patterns = {
        "create_test_user.py": ["test@example.com"],
        "create_demo_accounts.py": ["demo1@videoplanet.com", "demo2@videoplanet.com", "demo3@videoplanet.com", "demo4@videoplanet.com", "demo5@videoplanet.com"],
        "create_test_login.py": ["test@example.com"],
        " ": ["admin@example.com", "demo@example.com"]
    }
    
    for script, emails in patterns.items():
        print(f"\n[{script}]")
        for email in emails:
            try:
                user = User.objects.get(username=email)
                print(f"   {email} - email : {user.email if user.email else '()'}")
            except User.DoesNotExist:
                print(f"   {email} -  ")

if __name__ == "__main__":
    check_user_issues()