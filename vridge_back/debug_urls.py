#!/usr/bin/env python
"""
URL  
Django   URL    .
"""
import os
import sys
import django

# Django   
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_base')

# Django 
django.setup()

from django.urls import get_resolver
from django.conf import settings

def show_urls(urlpatterns=None, depth=0):
    """  URL  """
    if urlpatterns is None:
        urlpatterns = get_resolver().url_patterns
        
    for pattern in urlpatterns:
        print("  " * depth, end="")
        
        # URLPattern  URLResolver 
        if hasattr(pattern, 'pattern'):
            #   
            pattern_str = str(pattern.pattern)
            print(f"Pattern: {pattern_str}", end="")
            
            # View   
            if hasattr(pattern, 'callback'):
                view = pattern.callback
                if hasattr(view, 'view_class'):
                    view_name = f"{view.view_class.__module__}.{view.view_class.__name__}"
                else:
                    view_name = f"{view.__module__}.{view.__name__}" if hasattr(view, '__name__') else str(view)
                print(f" -> {view_name}", end="")
                
            #   
            if hasattr(pattern, 'name') and pattern.name:
                print(f" [name={pattern.name}]", end="")
                
            print()  # 
            
            #     
            if hasattr(pattern, 'url_patterns'):
                show_urls(pattern.url_patterns, depth + 1)

def find_auth_urls():
    """  URL  """
    print("\n=== Authentication URLs ===")
    resolver = get_resolver()
    
    for pattern in resolver.url_patterns:
        pattern_str = str(pattern.pattern)
        
        # auth  URL 
        if 'auth' in pattern_str.lower():
            print(f"\nPattern: {pattern_str}")
            
            if hasattr(pattern, 'callback'):
                view = pattern.callback
                if hasattr(view, 'view_class'):
                    print(f"  View Class: {view.view_class.__module__}.{view.view_class.__name__}")
                    print(f"  View Class Location: {view.view_class.__module__}")
                else:
                    print(f"  View: {view}")
                    
            if hasattr(pattern, 'name'):
                print(f"  Name: {pattern.name}")
                
def check_view_imports():
    """View    """
    print("\n=== Checking View Imports ===")
    
    try:
        from users.views_signup_safe import SafeSignUp, SafeSignIn
        print(" SafeSignUp imported successfully:", SafeSignUp)
        print(" SafeSignIn imported successfully:", SafeSignIn)
    except ImportError as e:
        print(" Failed to import SafeSignUp/SafeSignIn:", e)
        
    try:
        from rest_framework_simplejwt.views import TokenRefreshView
        print(" TokenRefreshView imported successfully:", TokenRefreshView)
    except ImportError as e:
        print(" Failed to import TokenRefreshView:", e)

def main():
    print("=" * 60)
    print("Django URL Pattern Debug")
    print("=" * 60)
    print(f"Settings Module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ROOT_URLCONF: {settings.ROOT_URLCONF}")
    print("=" * 60)
    
    # View  
    check_view_imports()
    
    #  URL 
    find_auth_urls()
    
    #  URL   ()
    print("\n=== All URL Patterns ===")
    show_urls()

if __name__ == "__main__":
    main()