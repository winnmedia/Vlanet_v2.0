#!/usr/bin/env python
"""API    """
import os
import sys
import django

# Django 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_base')
django.setup()

from django.conf import settings

print("=" * 50)
print("API   ")
print("=" * 50)

# Gemini API  
google_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY')
if google_key:
    print(f" GOOGLE_API_KEY: {google_key[:10]}...{google_key[-4:]}")
else:
    print(" GOOGLE_API_KEY:  ")

# EXAONE API  
exaone_key = getattr(settings, 'EXAONE_API_KEY', None) or os.environ.get('EXAONE_API_KEY')
if exaone_key and exaone_key != 'your_exaone_api_key_here':
    print(f" EXAONE_API_KEY: {exaone_key[:10]}...{exaone_key[-4:]}")
else:
    print(" EXAONE_API_KEY:    ")

print("\n   :")
print(f"- Gemini : {' ' if google_key else ' '}")
print(f"- EXAONE : {' ' if exaone_key and exaone_key != 'your_exaone_api_key_here' else ' '}")

if exaone_key and exaone_key != 'your_exaone_api_key_here':
    print("\n   : EXAONE() + Gemini()")
else:
    print("\n  Gemini  :   Gemini ")