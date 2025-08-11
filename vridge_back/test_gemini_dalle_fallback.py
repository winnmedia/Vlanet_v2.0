#!/usr/bin/env python
"""Gemini   DALL-E  """
import os
import sys
import django

# Django 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_base')
django.setup()

from video_planning.gemini_service import GeminiService
import logging

#  
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 80)
print("Gemini API   DALL-E  ")
print("=" * 80)

# GeminiService 
print("\n1.  ...")
try:
    service = GeminiService()
    print(" GeminiService  ")
    
    # DALL-E   
    if service.image_service_available:
        print(" DALL-E   ")
    else:
        print(" DALL-E    (OPENAI_API_KEY  )")
        print("   .env  OPENAI_API_KEY :")
        print("   OPENAI_API_KEY=your-openai-api-key-here")
    
except Exception as e:
    print(f"  : {str(e)}")
    sys.exit(1)

#  
print("\n2.   ...")

#   
shot_data = {
    'shot_number': 1,
    'shot_type': '',
    'camera_movement': '',
    'duration': 3,
    'description': '    ',
    'planning_options': {
        'tone': '',
        'genre': '',
        'concept': ''
    }
}

try:
    #  Gemini     
    original_model = service.model
    service.model = None  # Gemini   
    
    print("\n3. Gemini    DALL-E  ...")
    
    result = service.generate_storyboards_from_shot(shot_data)
    
    if 'storyboards' in result:
        print("\n   !")
        
        # Gemini  
        if result.get('gemini_error'):
            print(f"  Gemini  : {result['gemini_error'][:100]}...")
            print("   ")
        
        #   
        for i, frame in enumerate(result['storyboards']):
            print(f"\n[ {i+1}]")
            print(f": {frame.get('title', 'N/A')}")
            print(f": {frame.get('description_kr', 'N/A')}")
            
            #  
            if frame.get('image_url'):
                if frame.get('model_used') == 'dall-e':
                    print(" DALL-E  ")
                elif frame.get('is_placeholder'):
                    print("    ")
                else:
                    print("  ")
            else:
                print("   ")
    else:
        print("   ")
        if 'error' in result:
            print(f": {result['error']}")
    
    #  
    service.model = original_model
    
except Exception as e:
    print(f"    : {str(e)}")
    import traceback
    traceback.print_exc()

#   
print("\n\n4.    (Gemini + DALL-E)...")

try:
    result = service.generate_storyboards_from_shot(shot_data)
    
    if 'storyboards' in result and not result.get('gemini_error'):
        print(" Gemini  ")
        
        for i, frame in enumerate(result['storyboards']):
            if frame.get('image_url'):
                model_used = frame.get('model_used', 'unknown')
                print(f"  {i+1}: {model_used}  ")
    else:
        print("  Gemini  ")
        
except Exception as e:
    print(f"   : {str(e)}")

print("\n" + "=" * 80)
print(" ")
print("=" * 80)

#  
if not service.image_service_available:
    print("\n DALL-E :")
    print("1. OpenAI API  : https://platform.openai.com/api-keys")
    print("2. .env  :")
    print("   OPENAI_API_KEY=sk-...")
    print("3.  ")