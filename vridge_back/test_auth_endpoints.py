#!/usr/bin/env python3
"""
   
 Django  URL   
"""
import os
import sys
import django
import json

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_base')
django.setup()

from django.test import Client
from django.urls import reverse, resolve
from django.urls.exceptions import NoReverseMatch

def test_auth_endpoints():
    """  """
    client = Client()
    
    print("=" * 60)
    print("Authentication Endpoints Test")
    print("=" * 60)
    
    #   
    endpoints = [
        ('/api/auth/login/', 'POST', {'email': 'test@test.com', 'password': 'test123'}),
        ('/api/auth/signup/', 'POST', {'email': 'new@test.com', 'nickname': 'newuser', 'password': 'Test123!@#'}),
        ('/api/auth/refresh/', 'POST', {'refresh': 'dummy_token'}),
        ('/api/auth/check-email/', 'POST', {'email': 'test@test.com'}),
        ('/api/auth/check-nickname/', 'POST', {'nickname': 'testuser'}),
        ('/api/auth/me/', 'GET', None),
    ]
    
    for url, method, data in endpoints:
        print(f"\n Testing: {method} {url}")
        print("-" * 40)
        
        # URL  
        try:
            match = resolve(url)
            print(f" URL resolves to: {match.func.__module__}.{match.func.__name__ if hasattr(match.func, '__name__') else match.func.__class__.__name__}")
            print(f"   View class: {match.func.view_class if hasattr(match.func, 'view_class') else 'N/A'}")
            print(f"   URL name: {match.url_name}")
        except Exception as e:
            print(f" URL resolve failed: {e}")
            continue
        
        #   
        try:
            if method == 'POST':
                response = client.post(
                    url, 
                    data=json.dumps(data) if data else '{}',
                    content_type='application/json'
                )
            else:
                response = client.get(url)
                
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 404:
                print(f"     404 Not Found - URL not registered properly")
            elif response.status_code == 500:
                print(f"     500 Internal Server Error")
                if hasattr(response, 'content'):
                    content = response.content.decode('utf-8')[:200]
                    print(f"   Error preview: {content}")
            elif response.status_code in [200, 201]:
                print(f"    Success")
            else:
                print(f"   Response: {response.status_code}")
                if hasattr(response, 'content'):
                    try:
                        content = json.loads(response.content)
                        print(f"   Message: {content.get('message', 'N/A')}")
                    except:
                        pass
                        
        except Exception as e:
            print(f" Request failed: {e}")

def check_url_patterns():
    """URL  """
    from django.urls import get_resolver
    
    print("\n" + "=" * 60)
    print("Registered URL Patterns")
    print("=" * 60)
    
    resolver = get_resolver()
    auth_patterns = []
    
    for pattern in resolver.url_patterns:
        pattern_str = str(pattern.pattern)
        if 'auth' in pattern_str:
            auth_patterns.append((pattern_str, pattern))
    
    for pattern_str, pattern in auth_patterns:
        print(f"\n{pattern_str}")
        if hasattr(pattern, 'callback'):
            if hasattr(pattern.callback, 'view_class'):
                print(f"  → {pattern.callback.view_class}")
                # View   
                view_class = pattern.callback.view_class
                methods = [m for m in dir(view_class) if m in ['get', 'post', 'put', 'patch', 'delete']]
                print(f"  → Supported methods: {', '.join(methods)}")

def test_view_methods():
    """View   """
    print("\n" + "=" * 60)
    print("View Class Methods Check")
    print("=" * 60)
    
    try:
        from users.views_auth_fixed import ImprovedSignIn
        print("\n ImprovedSignIn class:")
        print(f"   Module: {ImprovedSignIn.__module__}")
        print(f"   Methods: {[m for m in dir(ImprovedSignIn) if not m.startswith('_')]}")
        
        # post   
        if hasattr(ImprovedSignIn, 'post'):
            print(f"    Has 'post' method")
        else:
            print(f"    Missing 'post' method")
            
    except ImportError as e:
        print(f" Cannot import ImprovedSignIn: {e}")
    
    try:
        from users.views_signup_safe import SafeSignIn, SafeSignUp
        print("\n SafeSignIn class:")
        if hasattr(SafeSignIn, 'post'):
            print(f"    Has 'post' method")
        
        print("\n SafeSignUp class:")
        if hasattr(SafeSignUp, 'post'):
            print(f"    Has 'post' method")
            
    except ImportError as e:
        print(f" Cannot import Safe views: {e}")

if __name__ == "__main__":
    test_view_methods()
    check_url_patterns()
    test_auth_endpoints()