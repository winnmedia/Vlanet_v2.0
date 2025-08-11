#!/usr/bin/env python
import os
import sys
import django

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import get_resolver
from django.conf import settings

def show_urls(urlpatterns=None, prefix=''):
    if urlpatterns is None:
        urlpatterns = get_resolver().url_patterns
        
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            # Include URL 
            show_urls(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            #  URL 
            if hasattr(pattern, 'pattern'):
                url = prefix + str(pattern.pattern)
                if 'feedback' in url or 'upload' in url:
                    print(f"{url} -> {pattern.callback}")

print("=== Feedback/Upload  URL  ===\n")
show_urls()
print("\n===  API URL  ===")
print(f"BASE URL: {settings.DEBUG and 'http://localhost:8000' or 'https://videoplanet.up.railway.app'}")
print("API Prefix: /api/")
print("\n :")
print("- /api/projects/{project_id}/feedback/upload/ ->   ")
print("- /api/feedbacks/{project_id} ->  /")
print("- /api/feedbacks/messages/{message_id}/ ->   /")