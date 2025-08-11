#!/usr/bin/env python3
"""
VideoPlanet       
 /     
"""

import os
import sys
import json
from urllib.parse import urlparse
import django

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.test.client import Client

class DeploymentChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.successes = []
        
    def check_environment_variables(self):
        """  """
        print("\n  ...")
        
        required_vars = {
            'SECRET_KEY': '  Django  ',
            'DATABASE_URL': 'PostgreSQL   ',
        }
        
        optional_vars = {
            'REDIS_URL': 'Redis    ',
            'GOOGLE_API_KEY': 'Google Gemini API ',
            'HUGGINGFACE_API_KEY': 'Hugging Face API ',
            'SENDGRID_API_KEY': '   SendGrid API ',
            'AWS_ACCESS_KEY_ID': 'AWS S3  ',
            'AWS_SECRET_ACCESS_KEY': 'AWS S3  ',
            'AWS_STORAGE_BUCKET_NAME': 'AWS S3  ',
            'SENTRY_DSN': '   Sentry DSN',
        }
        
        #   
        for var, description in required_vars.items():
            if os.environ.get(var):
                self.successes.append(f" {var}: {description} - ")
            else:
                self.errors.append(f" {var}: {description} - !")
        
        #   
        for var, description in optional_vars.items():
            if os.environ.get(var):
                self.successes.append(f" {var}: {description} - ")
            else:
                self.warnings.append(f"  {var}: {description} -  ()")
    
    def check_database_connection(self):
        """  """
        print("\n   ...")
        
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.successes.append("   ")
        except Exception as e:
            self.errors.append(f"   : {str(e)}")
    
    def check_migrations(self):
        """  """
        print("\n   ...")
        
        try:
            from django.core.management import call_command
            from io import StringIO
            
            out = StringIO()
            call_command('showmigrations', '--plan', stdout=out)
            output = out.getvalue()
            
            if '[X]' in output and '[ ]' not in output:
                self.successes.append("   ")
            else:
                unmigrated = output.count('[ ]')
                self.warnings.append(f"     {unmigrated} ")
        except Exception as e:
            self.errors.append(f"   : {str(e)}")
    
    def check_static_files(self):
        """   """
        print("\n    ...")
        
        if hasattr(settings, 'STATIC_ROOT'):
            self.successes.append(f" STATIC_ROOT : {settings.STATIC_ROOT}")
        else:
            self.errors.append(" STATIC_ROOT  ")
        
        if hasattr(settings, 'STATICFILES_STORAGE'):
            if 'whitenoise' in settings.STATICFILES_STORAGE.lower():
                self.successes.append(" WhiteNoise     ")
            else:
                self.warnings.append("  WhiteNoise  ")
    
    def check_media_files(self):
        """   """
        print("\n    ...")
        
        if hasattr(settings, 'MEDIA_ROOT'):
            self.successes.append(f" MEDIA_ROOT : {settings.MEDIA_ROOT}")
            
            #    
            if os.path.exists(settings.MEDIA_ROOT):
                self.successes.append("   ")
            else:
                self.warnings.append("      ( )")
        else:
            self.errors.append(" MEDIA_ROOT  ")
        
        # AWS S3  
        if os.environ.get('AWS_ACCESS_KEY_ID'):
            self.successes.append(" AWS S3  ")
        else:
            self.warnings.append("  AWS S3  -   ")
    
    def check_cors_settings(self):
        """CORS  """
        print("\n CORS  ...")
        
        if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
            origins = settings.CORS_ALLOWED_ORIGINS
            self.successes.append(f" CORS   {len(origins)} ")
            
            #   
            important_domains = ['https://vlanet.net', 'https://www.vlanet.net']
            for domain in important_domains:
                if domain in origins:
                    self.successes.append(f"   {domain} ")
                else:
                    self.errors.append(f"   {domain} !")
        else:
            self.errors.append(" CORS_ALLOWED_ORIGINS  ")
        
        if hasattr(settings, 'CORS_ALLOW_CREDENTIALS'):
            if settings.CORS_ALLOW_CREDENTIALS:
                self.successes.append(" CORS    ")
            else:
                self.warnings.append("  CORS    ")
    
    def check_security_settings(self):
        """  """
        print("\n   ...")
        
        # DEBUG 
        if not settings.DEBUG:
            self.successes.append(" DEBUG  ")
        else:
            self.errors.append(" DEBUG   !")
        
        # ALLOWED_HOSTS
        if settings.ALLOWED_HOSTS:
            self.successes.append(f" ALLOWED_HOSTS : {len(settings.ALLOWED_HOSTS)}")
        else:
            self.errors.append(" ALLOWED_HOSTS !")
        
        # SECURE_SSL_REDIRECT
        if hasattr(settings, 'SECURE_SSL_REDIRECT') and settings.SECURE_SSL_REDIRECT:
            self.successes.append(" HTTPS   ")
        else:
            self.warnings.append("  HTTPS   ")
        
        # CSRF 
        if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
            self.successes.append(f" CSRF   {len(settings.CSRF_TRUSTED_ORIGINS)} ")
    
    def check_cache_settings(self):
        """  """
        print("\n   ...")
        
        if os.environ.get('REDIS_URL'):
            self.successes.append(" Redis  ")
        else:
            self.warnings.append("  Redis  -   ")
            
            #   
            try:
                from django.core.cache import cache
                cache.set('test_key', 'test_value', 1)
                if cache.get('test_key') == 'test_value':
                    self.successes.append("    ")
                else:
                    self.errors.append("    ")
            except Exception as e:
                self.errors.append(f"   : {str(e)}")
    
    def check_websocket_settings(self):
        """  """
        print("\n   ...")
        
        if 'channels' in settings.INSTALLED_APPS:
            self.successes.append(" Django Channels ")
            
            if hasattr(settings, 'CHANNEL_LAYERS'):
                backend = settings.CHANNEL_LAYERS.get('default', {}).get('BACKEND', '')
                if 'redis' in backend.lower():
                    self.successes.append(" Redis     ")
                elif 'inmemory' in backend.lower():
                    self.warnings.append("  InMemory     (  )")
                else:
                    self.warnings.append(f"      : {backend}")
        else:
            self.warnings.append("  Django Channels  -  ")
    
    def check_logging_settings(self):
        """  """
        print("\n   ...")
        
        if hasattr(settings, 'LOGGING'):
            self.successes.append("   ")
            
            # Sentry 
            if os.environ.get('SENTRY_DSN'):
                self.successes.append(" Sentry   ")
            else:
                self.warnings.append("  Sentry  -   ")
        else:
            self.warnings.append("    ")
    
    def check_api_endpoints(self):
        """ API  """
        print("\n API  ...")
        
        client = Client()
        
        # Health check
        try:
            response = client.get('/api/health/')
            if response.status_code == 200:
                self.successes.append(" Health check  ")
            else:
                self.errors.append(f" Health check : {response.status_code}")
        except Exception as e:
            self.errors.append(f" Health check  : {str(e)}")
    
    def run_all_checks(self):
        """  """
        print("=" * 80)
        print(" VideoPlanet    ")
        print("=" * 80)
        
        self.check_environment_variables()
        self.check_database_connection()
        self.check_migrations()
        self.check_static_files()
        self.check_media_files()
        self.check_cors_settings()
        self.check_security_settings()
        self.check_cache_settings()
        self.check_websocket_settings()
        self.check_logging_settings()
        self.check_api_endpoints()
        
        #  
        print("\n" + "=" * 80)
        print("   ")
        print("=" * 80)
        
        print(f"\n : {len(self.successes)}")
        for success in self.successes:
            print(f"  {success}")
        
        if self.warnings:
            print(f"\n  : {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.errors:
            print(f"\n : {len(self.errors)}")
            for error in self.errors:
                print(f"  {error}")
        
        #  
        print("\n" + "=" * 80)
        if not self.errors:
            print("   !    .")
        else:
            print("      .")
            print("       .")
        
        return len(self.errors) == 0

if __name__ == "__main__":
    checker = DeploymentChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)