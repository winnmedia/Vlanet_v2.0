"""
JWT    
"""
import os
import sys
import django

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.abspath('.')))
django.setup()

from django.test import RequestFactory
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.utils import user_validator
import json

#  
test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU0ODk4NzU0LCJpYXQiOjE3NTQyOTM5NTQsImp0aSI6IjRkNzZhNmM5OGY5YTRkYzBiZDljNjk3MTQ4OGY5YmU0IiwidXNlcl9pZCI6MjR9.SlMhq6CtrrZAjnMwUIu7oNzASg7S7iC7LszFEQTgdoM"

# RequestFactory   
factory = RequestFactory()

print("=== JWT    ===\n")

# 1.  JWT  
print("1.  JWT  ")
jwt_auth = JWTAuthentication()

# Authorization  
request = factory.get('/api/users/me/', HTTP_AUTHORIZATION=f'Bearer {test_token}')
try:
    auth_result = jwt_auth.authenticate(request)
    if auth_result:
        user, token = auth_result
        print(f"  ! : {user.email}")
    else:
        print("  : authenticate() None ")
except Exception as e:
    print(f"  : {e}")

print("\n2. user_validator  ")

#   
@user_validator
def test_view(self, request):
    return {"user": request.user.email if hasattr(request, 'user') else None}

#  self 
class FakeView:
    pass

fake_view = FakeView()

# Authorization  
request2 = factory.get('/api/users/me/', HTTP_AUTHORIZATION=f'Bearer {test_token}')
request2.content_type = 'application/json'
# WSGIRequest user  
from django.contrib.auth.models import AnonymousUser
request2.user = AnonymousUser()

print("Authorization  :")
try:
    result = test_view(fake_view, request2)
    print(f": {result}")
except Exception as e:
    print(f": {e}")
    import traceback
    traceback.print_exc()

#  
print("\n :")
request3 = factory.get('/api/users/me/')
request3.COOKIES['vridge_session'] = test_token
request3.content_type = 'application/json'
request3.user = AnonymousUser()

try:
    result = test_view(fake_view, request3)
    print(f": {result}")
except Exception as e:
    print(f": {e}")

print("\n3.   ")
from rest_framework_simplejwt.tokens import AccessToken
try:
    token_obj = AccessToken(test_token)
    print(f"  ")
    print(f"   User ID: {token_obj['user_id']}")
    print(f"    : {token_obj['token_type']}")
    print(f"   : {token_obj['exp']}")
except Exception as e:
    print(f"   : {e}")

print("\n===   ===")