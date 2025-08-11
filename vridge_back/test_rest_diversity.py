#!/usr/bin/env python
"""REST API    - 403  """
import os
import sys
import django
import json
from datetime import datetime

# Django 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_base')
django.setup()

from video_planning.gemini_service_rest import GeminiServiceREST

print("=" * 80)
print("VideoPlanet REST API  ")
print("=" * 80)

#   
test_options = {
    'tone': ['', '', '', ' ', ''],
    'genre': ['', '', '', '', ''],
    'story_framework': ['classic', 'hook_immersion', 'pixar', 'deductive', 'inductive', 'documentary']
}

#  
planning_text = """
      3   .
AI         ,
   .
"""

# REST  
print("\n REST   ...")
try:
    service = GeminiServiceREST()
    print(" GeminiServiceREST  ")
except Exception as e:
    print(f"   : {str(e)}")
    sys.exit(1)

#  
print("\n  :")
response = service.generate_content(" '' ", temperature=0.7)
if response:
    print(f" : {response[:100]}...")
else:
    print(" ")

#  
results = {}
success_count = 0
total_tests = 0

# 1.  
print(f"\n{'='*60}")
print(" (tone)  ")
print("="*60)

for tone in test_options['tone']:
    print(f"\n[{tone}]  :")
    context = {
        'tone': tone,
        'genre': '',
        'concept': ' ',
        'target': '20-30',
        'purpose': ' ',
        'duration': '3',
        'story_framework': 'classic'
    }
    
    total_tests += 1
    
    try:
        result = service.generate_stories_from_planning(planning_text, context)
        
        if result and 'stories' in result:
            stories = result['stories']
            print(f" ! {len(stories)}  ")
            
            #    
            if stories:
                first = stories[0]
                print(f"  : {first.get('title', 'N/A')}")
                print(f"  : {first.get('summary', 'N/A')[:80]}...")
            
            results[f'tone_{tone}'] = {
                'success': True,
                'story_count': len(stories),
                'titles': [s.get('title', 'N/A') for s in stories]
            }
            success_count += 1
        else:
            print("   ")
            results[f'tone_{tone}'] = {'success': False}
            
    except Exception as e:
        print(f" : {str(e)[:100]}...")
        results[f'tone_{tone}'] = {'success': False, 'error': str(e)}

# 2.  
print(f"\n{'='*60}")
print("   ")
print("="*60)

for framework in test_options['story_framework']:
    print(f"\n[{framework}] :")
    context = {
        'tone': '',
        'genre': '/',
        'concept': '',
        'target': '20-30 ',
        'purpose': '  ',
        'duration': '3',
        'story_framework': framework
    }
    
    total_tests += 1
    
    try:
        result = service.generate_stories_from_planning(planning_text, context)
        
        if result and 'stories' in result:
            stories = result['stories']
            print(f" ! {len(stories)} ")
            
            #   
            stages = [s.get('stage_name', '') for s in stories]
            print(f"  : {' → '.join(stages)}")
            
            results[f'framework_{framework}'] = {
                'success': True,
                'story_count': len(stories),
                'stages': stages
            }
            success_count += 1
        else:
            print(" ")
            results[f'framework_{framework}'] = {'success': False}
            
    except Exception as e:
        print(f" : {str(e)[:50]}...")
        results[f'framework_{framework}'] = {'success': False, 'error': str(e)}

# 3.  
print(f"\n{'='*60}")
print("   ")
print("="*60)

combo_tests = [
    {
        'name': '  ',
        'context': {
            'tone': '',
            'genre': '',
            'story_framework': 'pixar',
            'target': '10',
            'duration': '5'
        }
    },
    {
        'name': ' ',
        'context': {
            'tone': '',
            'genre': '',
            'story_framework': 'documentary',
            'target': '',
            'duration': '10'
        }
    }
]

for combo in combo_tests:
    print(f"\n[{combo['name']}]:")
    total_tests += 1
    
    try:
        result = service.generate_stories_from_planning(planning_text, combo['context'])
        
        if result and 'stories' in result:
            print(f" ! {len(result['stories'])} ")
            success_count += 1
        else:
            print(" ")
            
    except Exception as e:
        print(f" : {str(e)[:50]}...")

#  
print(f"\n{'='*80}")
print("  ")
print("="*80)

print(f"\n : {total_tests}")
print(f": {success_count} ({success_count/total_tests*100:.1f}%)")

#  
token_usage = service.get_token_usage()
print(f"\n  :")
print(f"- : {token_usage['total']:,}")
print(f"- : {token_usage['prompt']:,}")
print(f"- : {token_usage['response']:,}")

#  
output_file = f"rest_api_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'test_summary': {
            'total_tests': total_tests,
            'success_count': success_count,
            'success_rate': success_count/total_tests if total_tests > 0 else 0
        },
        'results': results,
        'token_usage': token_usage
    }, f, ensure_ascii=False, indent=2)

print(f"\n  {output_file} .")

print("\n REST API  403    !")
print("="*80)