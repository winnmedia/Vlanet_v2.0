#!/usr/bin/env python
"""
   
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

def create_demo_accounts():
    """5   """
    print("=" * 50)
    print("   ")
    print("=" * 50)
    
    #   
    demo_accounts = [
        {
            "username": "demo1@videoplanet.com",
            "nickname": "",
            "password": "demo1234",
            "description": " "
        },
        {
            "username": "demo2@videoplanet.com", 
            "nickname": "",
            "password": "demo1234",
            "description": " "
        },
        {
            "username": "demo3@videoplanet.com",
            "nickname": "",
            "password": "demo1234",
            "description": " "
        },
        {
            "username": "demo4@videoplanet.com",
            "nickname": "",
            "password": "demo1234",
            "description": " "
        },
        {
            "username": "demo5@videoplanet.com",
            "nickname": "",
            "password": "demo1234",
            "description": " "
        }
    ]
    
    created_accounts = []
    
    for account in demo_accounts:
        try:
            #   
            if User.objects.filter(username=account["username"]).exists():
                print(f"    : {account['username']}")
                user = User.objects.get(username=account["username"])
                #  
                user.password = make_password(account["password"])
                user.save()
                print(f"    .")
            else:
                #   
                user = User.objects.create(
                    username=account["username"],
                    nickname=account["nickname"],
                    password=make_password(account["password"]),
                    login_method="email",
                    email=account["username"]  # username  
                )
                print(f"   : {account['username']}")
            
            created_accounts.append({
                "email": account["username"],
                "password": account["password"],
                "nickname": account["nickname"],
                "description": account["description"]
            })
            
        except Exception as e:
            print(f"    ({account['username']}): {e}")
    
    #  
    print("\n" + "=" * 50)
    print("   ")
    print("=" * 50)
    print("\n    :\n")
    
    for i, account in enumerate(created_accounts, 1):
        print(f"{i}. {account['nickname']} - {account['description']}")
        print(f"   : {account['email']}")
        print(f"   : {account['password']}")
        print()
    
    #    
    with open("DEMO_ACCOUNTS.md", "w", encoding="utf-8") as f:
        f.write("# VideoPlanet   \n\n")
        f.write("      .\n\n")
        f.write("##   \n\n")
        
        for i, account in enumerate(created_accounts, 1):
            f.write(f"### {i}. {account['nickname']}\n")
            f.write(f"- ****: {account['description']}\n")
            f.write(f"- ****: `{account['email']}`\n")
            f.write(f"- ****: `{account['password']}`\n\n")
        
        f.write("## \n\n")
        f.write("-   /  .\n")
        f.write("-     .\n")
        f.write("-     .\n")
    
    print("   DEMO_ACCOUNTS.md  .")

if __name__ == "__main__":
    create_demo_accounts()