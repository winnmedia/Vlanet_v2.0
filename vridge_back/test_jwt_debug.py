#!/usr/bin/env python3
"""
JWT    
2025  Django SimpleJWT  
"""

import os
import sys
import django
import json
from datetime import datetime

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_base')
sys.path.insert(0, '/home/winnmedia/VideoPlanet/vridge_back')
django.setup()

from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings

User = get_user_model()

def print_section(title):
    """  """
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_jwt_settings():
    """JWT  """
    print_section("1. JWT  ")
    
    print("\n[SimpleJWT ]")
    jwt_settings = settings.SIMPLE_JWT
    for key, value in jwt_settings.items():
        print(f"  - {key}: {value}")
    
    print("\n[REST Framework ]")
    rf_settings = settings.REST_FRAMEWORK
    print(f"  - Authentication Classes: {rf_settings.get('DEFAULT_AUTHENTICATION_CLASSES', 'Not set')}")
    
    print("\n[SECRET_KEY ]")
    print(f"  - SECRET_KEY : {'Yes' if settings.SECRET_KEY else 'No'}")
    print(f"  - SECRET_KEY : {len(settings.SECRET_KEY) if settings.SECRET_KEY else 0}")

def test_user_authentication():
    """  """
    print_section("2.   ")
    
    test_email = "ceo@winnmedia.co.kr"
    test_password = "test_password_123"  #    
    
    print(f"\n[ : {test_email}]")
    
    #   
    user = User.objects.filter(username=test_email).first()
    if not user:
        user = User.objects.filter(email=test_email).first()
    
    if user:
        print(f"    : ID={user.id}, username={user.username}")
        print(f"    - Email: {user.email}")
        print(f"    - Active: {user.is_active}")
        print(f"    - Email Verified: {user.email_verified}")
        print(f"    - Login Method: {user.login_method}")
        
        #   ()
        print(f"\n[ ]")
        print(f"  -  : {'Yes' if user.password else 'No'}")
        if user.password:
            print(f"  -   : {user.password[:20]}...")
        
        return user
    else:
        print(f"      : {test_email}")
        return None

def test_token_generation(user):
    """  """
    print_section("3. JWT   ")
    
    if not user:
        print("       ")
        return None, None
    
    try:
        # RefreshToken 
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        print(f"\n[  ]")
        print(f"  - Refresh Token: {str(refresh)[:50]}...")
        print(f"  - Access Token: {str(access_token)[:50]}...")
        
        #   
        print(f"\n[Access Token ]")
        for key, value in access_token.payload.items():
            if key in ['exp', 'iat']:
                value = datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
            print(f"    - {key}: {value}")
        
        return str(refresh), str(access_token)
        
    except Exception as e:
        print(f"     : {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_token_validation(access_token):
    """  """
    print_section("4. JWT   ")
    
    if not access_token:
        print("     ")
        return
    
    try:
        # AccessToken  
        print("\n[AccessToken  ]")
        token = AccessToken(access_token)
        print(f"    ")
        print(f"    - User ID: {token.get('user_id')}")
        print(f"    - Token Type: {token.get('token_type')}")
        
        #  
        user_id = token.get('user_id')
        if user_id:
            user = User.objects.filter(id=user_id).first()
            if user:
                print(f"    - User Found: {user.username}")
            else:
                print(f"     User ID {user_id}   ")
        
    except TokenError as e:
        print(f"     : {e}")
    except Exception as e:
        print(f"     : {e}")
        import traceback
        traceback.print_exc()

def test_jwt_authentication(access_token):
    """JWTAuthentication  """
    print_section("5. JWTAuthentication  ")
    
    if not access_token:
        print("     ")
        return
    
    #  request  
    class FakeRequest:
        def __init__(self, token):
            self.META = {
                'HTTP_AUTHORIZATION': f'Bearer {token}'
            }
            self.COOKIES = {}
    
    request = FakeRequest(access_token)
    
    try:
        # JWTAuthentication  
        jwt_auth = JWTAuthentication()
        
        print("\n[ ]")
        result = jwt_auth.authenticate(request)
        
        if result:
            user, validated_token = result
            print(f"    ")
            print(f"    - User: {user.username}")
            print(f"    - User ID: {user.id}")
            print(f"    - Token Valid: Yes")
        else:
            print(f"    : None ")
            
    except InvalidToken as e:
        print(f"     : {e}")
    except Exception as e:
        print(f"    : {e}")
        import traceback
        traceback.print_exc()

def check_migration_issues():
    """   """
    print_section("6.    ")
    
    from django.db import connection
    
    print("\n[User   ]")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users_user'
            ORDER BY ordinal_position
            LIMIT 10
        """)
        columns = cursor.fetchall()
        for col_name, data_type in columns:
            print(f"  - {col_name}: {data_type}")
    
    print("\n[   ]")
    required_fields = ['id', 'username', 'email', 'password', 'is_active']
    user = User.objects.first()
    if user:
        for field in required_fields:
            has_field = hasattr(user, field)
            print(f"  - {field}: {'' if has_field else ''}")

def provide_solutions():
    """   """
    print_section("7.   ")
    
    print("""
[ JWT     ]

1. SECRET_KEY 
   →  : echo $SECRET_KEY
   → settings.py    

2.  
   → ACCESS_TOKEN_LIFETIME  
   →    

3.  
   → ALGORITHM   (: HS256)
   →     

4. User   
   → python manage.py makemigrations
   → python manage.py migrate

5.    
   →  : "Authorization: Bearer <token>"
   →   

6. CORS  
   → CORS_ALLOW_HEADERS 'authorization'  
   → CORS_ALLOW_CREDENTIALS = True 

7.   
   → CorsMiddleware CommonMiddleware   

[  ]
1.      
2.   authenticate() 
3.   API  
4.       
""")

def main():
    """  """
    print("\n" + "="*60)
    print("  JWT    ")
    print("   :", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    # 1. JWT  
    test_jwt_settings()
    
    # 2.   
    user = test_user_authentication()
    
    # 3.   
    refresh_token, access_token = test_token_generation(user)
    
    # 4.   
    test_token_validation(access_token)
    
    # 5. JWTAuthentication  
    test_jwt_authentication(access_token)
    
    # 6.  
    check_migration_issues()
    
    # 7.   
    provide_solutions()
    
    print("\n" + "="*60)
    print("   ")
    print("="*60)

if __name__ == "__main__":
    main()