#!/usr/bin/env python
"""    -    """
import os
import sys
import django
import json
from datetime import datetime

# Django 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_base')
django.setup()

#      
os.environ['HTTP_HOST'] = 'localhost:8000'
os.environ['HTTP_REFERER'] = 'http://localhost:3000'

from video_planning.views import generate_stories_from_planning_view
from django.test import RequestFactory
from users.models import User
import requests

print("=" * 80)
print("   ")
print("=" * 80)

# Django RequestFactory     
factory = RequestFactory()

#   (  )
try:
    test_user = User.objects.first()
    if not test_user:
        print("   ...")
        test_user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
except Exception as e:
    print(f"  : {e}")
    test_user = None

#  
test_scenarios = [
    {
        'name': '  -  ',
        'data': {
            'planning_text': '   5 ',
            'tone': '',
            'genre': '',
            'concept': '',
            'target': '',
            'purpose': '',
            'duration': '5',
            'story_framework': 'classic'
        }
    },
    {
        'name': '  -  ',
        'data': {
            'planning_text': '     ',
            'tone': '',
            'genre': '',
            'concept': '',
            'target': '20-30',
            'purpose': '',
            'duration': '3',
            'story_framework': 'pixar'
        }
    },
    {
        'name': '  - ',
        'data': {
            'planning_text': '    ',
            'tone': '',
            'genre': '',
            'concept': '',
            'target': '',
            'purpose': '',
            'duration': '10',
            'story_framework': 'documentary'
        }
    },
    {
        'name': '   -  ',
        'data': {
            'planning_text': '     ',
            'tone': ' ',
            'genre': '',
            'concept': ' ',
            'target': '20-40',
            'purpose': '',
            'duration': '5',
            'story_framework': 'hook_immersion'
        }
    }
]

# API   
print("\n API    :")
api_url = "http://localhost:8000/api/planning/generate-stories/"

headers = {
    'Content-Type': 'application/json',
    'Referer': 'http://localhost:3000',
    'Origin': 'http://localhost:3000'
}

for scenario in test_scenarios[:1]:  #   
    print(f"\n[{scenario['name']}]")
    
    try:
        # POST 
        response = requests.post(
            api_url,
            json=scenario['data'],
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'stories' in result:
                print(f" ! {len(result['stories'])}  ")
                for i, story in enumerate(result['stories'], 1):
                    print(f"   {i}: {story.get('title', 'N/A')}")
            else:
                print(f"  : {result}")
        else:
            print(f" API : {response.status_code}")
            print(f": {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("     .")
        print("   :")
        print("python manage.py runserver")
    except Exception as e:
        print(f" : {str(e)}")

#  
print("\n" + "="*80)
print("   ")
print("="*80)

print("\n 403   :")
print("1. Google Cloud Console API   ")
print("   - API restrictions: None  Generative Language API ")
print("   - Application restrictions: None")
print("2.  API   ( )")
print("3. .env  ")
print("4. Railway  ")

print("\n      :")
print("- tone: , , ,  , ")
print("- genre: , , , , , , ")
print("- story_framework: classic, hook_immersion, pixar, deductive, inductive, documentary")
print("- development_level: minimal, light, balanced, detailed")
print("- aspectRatio: 16:9, 9:16, 1:1, 4:3, 21:9")
print("- platform: YouTube, Instagram, TikTok, TV, ")
print("- colorTone: , , , , ")
print("- editingStyle:  , , , , ")
print("- musicStyle: , , , , ")

print("\n       ,")
print("       .")
print("="*80)