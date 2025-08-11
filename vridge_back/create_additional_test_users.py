import os
import sys
import django

# Django  
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.railway")
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def create_test_users():
    """   """
    test_users = [
        {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "nickname": ""
        },
        {
            "email": "admin@example.com",
            "password": "adminpass123",
            "first_name": "Admin",
            "last_name": "User",
            "nickname": "",
            "is_staff": True,
            "is_superuser": True
        },
        {
            "email": "demo@example.com",
            "password": "demopass123",
            "first_name": "Demo",
            "last_name": "User",
            "nickname": ""
        }
    ]
    
    created_users = []
    
    for user_data in test_users:
        email = user_data["email"]
        password = user_data["password"]
        
        try:
            with transaction.atomic():
                #   
                if User.objects.filter(email=email).exists():
                    print(f"\n {email}  .")
                    user = User.objects.get(email=email)
                    user.set_password(password)
                    user.first_name = user_data.get("first_name", "")
                    user.last_name = user_data.get("last_name", "")
                    user.nickname = user_data.get("nickname", "")
                    if user_data.get("is_staff"):
                        user.is_staff = True
                    if user_data.get("is_superuser"):
                        user.is_superuser = True
                    user.save()
                    print(f" .")
                else:
                    #   
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        first_name=user_data.get("first_name", ""),
                        last_name=user_data.get("last_name", ""),
                        is_active=True,
                        is_staff=user_data.get("is_staff", False),
                        is_superuser=user_data.get("is_superuser", False)
                    )
                    user.nickname = user_data.get("nickname", "")
                    user.save()
                    print(f"\n   : {email}")
                
                created_users.append({
                    "email": email,
                    "password": password,
                    "nickname": user_data.get("nickname", ""),
                    "is_admin": user_data.get("is_superuser", False)
                })
                
        except Exception as e:
            print(f" {email}    : {e}")
    
    return created_users

if __name__ == "__main__":
    users = create_test_users()
    
    print("\n" + "="*50)
    print("  ")
    print("="*50)
    
    for user in users:
        print(f"\n: {user['email']}")
        print(f": {user['password']}")
        print(f": {user['nickname']}")
        if user['is_admin']:
            print("( )")
    
    print("\n" + "="*50)