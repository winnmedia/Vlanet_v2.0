#!/usr/bin/env python
"""Hugging Face EXAONE API  """
import os
import sys
import django
import requests

# Django 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_base')
django.setup()

from django.conf import settings

# API  
hf_api_key = getattr(settings, 'HUGGINGFACE_API_KEY', None) or os.environ.get('HUGGINGFACE_API_KEY')

print("=" * 60)
print("Hugging Face EXAONE API ")
print("=" * 60)

if not hf_api_key or hf_api_key == 'your_huggingface_api_key_here':
    print(" Hugging Face API   .")
    print("\n API   :")
    print("1. https://huggingface.co/ ")
    print("2.   ")
    print("3.     → Settings")
    print("4. Access Tokens  ")
    print("5. 'New token' ")
    print("6. Token name: VideoPlanet")
    print("7. Token type: Read ( )")
    print("8.   ")
    print("\n .env  :")
    print("HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxx")
    sys.exit(1)

print(f" API  : {hf_api_key[:10]}...{hf_api_key[-4:]}")

#  
model_id = "LGAI-EXAONE/EXAONE-4.0-32B"
api_url = f"https://api-inference.huggingface.co/models/{model_id}"

print(f"\n  : {model_id}")

#   
headers = {
    "Authorization": f"Bearer {hf_api_key}",
    "Content-Type": "application/json"
}

# EXAONE  
prompt = "[|system|]  AI .[|endofturn|]\n[|user|].   .[|endofturn|]\n[|assistant|]"

data = {
    "inputs": prompt,
    "parameters": {
        "temperature": 0.7,
        "max_new_tokens": 150,
        "top_p": 0.9,
        "do_sample": True,
        "return_full_text": False
    }
}

print("\n API  ...")

try:
    response = requests.post(api_url, headers=headers, json=data, timeout=30)
    
    print(f"\n  : {response.status_code}")
    
    if response.status_code == 503:
        print("\n⏳   .    .")
        print("   (     20-30   )")
        
    elif response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get('generated_text', '')
            print(f"\n API  !")
            print(f": {generated_text}")
        else:
            print(f"\n     : {result}")
            
    else:
        print(f"\n API : {response.text}")
        
        if response.status_code == 401:
            print("\n API   .  .")
        elif response.status_code == 429:
            print("\n API   .")
        
except requests.exceptions.Timeout:
    print("\n    (30)")
    print("        .")
    
except Exception as e:
    print(f"\n  : {str(e)}")

print("\n" + "=" * 60)
print(" ")
print("=" * 60)

#   
print("\n   ...")
try:
    from video_planning.huggingface_exaone_service import HuggingFaceExaoneService
    
    service = HuggingFaceExaoneService()
    if service.available:
        print(" HuggingFaceExaoneService  ")
        
        #    
        test_result = service.generate_stories_from_planning(
            "      ",
            {"genre": "", "tone": ""}
        )
        
        if test_result:
            print("    ")
        else:
            print("     ")
    else:
        print(" HuggingFaceExaoneService   (API  )")
        
except Exception as e:
    print(f"   : {str(e)}")

print("\n API   VideoPlanet    HF EXAONE .")