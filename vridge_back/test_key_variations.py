#!/usr/bin/env python
"""     """
import os
import sys
import django
import json
from datetime import datetime

# Django 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_base')
django.setup()

from video_planning.gemini_service import GeminiService

print("=" * 80)
print("VideoPlanet     ")
print("=" * 80)

#  
planning_text = """
       
"""

# GeminiService 
print("\n   ...")
try:
    service = GeminiService()
    print("  ")
except Exception as e:
    print(f"  : {str(e)}")
    sys.exit(1)

#  
test_scenarios = [
    {
        'name': '  ',
        'base_context': {
            'genre': '',
            'target': '20-30',
            'duration': '5',
            'story_framework': 'classic'
        },
        'variations': [
            {'tone': ''},
            {'tone': ''},
            {'tone': ''},
            {'tone': ' '}
        ]
    },
    {
        'name': '  ',
        'base_context': {
            'tone': '',
            'target': '20-30',
            'duration': '5',
            'story_framework': 'classic'
        },
        'variations': [
            {'genre': ''},
            {'genre': ''},
            {'genre': ''},
            {'genre': ''}
        ]
    },
    {
        'name': '  ',
        'base_context': {
            'tone': '',
            'genre': '',
            'target': '',
            'duration': '5'
        },
        'variations': [
            {'story_framework': 'classic'},
            {'story_framework': 'pixar'},
            {'story_framework': 'hook_immersion'},
            {'story_framework': 'documentary'}
        ]
    },
    {
        'name': '  ',
        'base_context': {
            'tone': '',
            'genre': '',
            'duration': '5',
            'story_framework': 'classic'
        },
        'variations': [
            {'target': ''},
            {'target': '10'},
            {'target': '20-30'},
            {'target': '40-50'}
        ]
    }
]

#  
all_results = {}

#   
for scenario in test_scenarios:
    print(f"\n{'='*60}")
    print(f" {scenario['name']}")
    print("="*60)
    
    scenario_results = []
    
    for variation in scenario['variations']:
        #  
        context = scenario['base_context'].copy()
        context.update(variation)
        
        #   
        changed_key = list(variation.keys())[0]
        changed_value = variation[changed_key]
        print(f"\n[{changed_key}: {changed_value}]")
        
        try:
            result = service.generate_stories_from_planning(planning_text, context)
            
            if result and 'stories' in result and len(result['stories']) > 0:
                stories = result['stories']
                
                #    
                first_story = stories[0]
                
                print(f"  ")
                print(f": {first_story.get('title', 'N/A')}")
                print(f": {first_story.get('stage_name', 'N/A')}")
                print(f": {first_story.get('summary', 'N/A')[:100]}...")
                
                #  
                content = f"{first_story.get('title', '')} {first_story.get('summary', '')} {first_story.get('key_content', '')}"
                
                #    
                reflection_keywords = {
                    '': ['', '', ''],
                    '': ['', '', ''],
                    '': ['', '', ''],
                    ' ': ['', '', ''],
                    '': ['', '', ''],
                    '': ['', '', ''],
                    '': ['', '', ''],
                    '': ['', '', ''],
                    'classic': ['', '', '', ''],
                    'pixar': ['', '', '', ''],
                    'hook_immersion': ['', '', '', ''],
                    'documentary': ['', '', '']
                }
                
                if changed_value in reflection_keywords:
                    keywords = reflection_keywords[changed_value]
                    reflected = any(kw in content for kw in keywords)
                    print(f" : {' ' if reflected else ' '}")
                
                scenario_results.append({
                    'setting': f"{changed_key}={changed_value}",
                    'title': first_story.get('title', 'N/A'),
                    'summary': first_story.get('summary', 'N/A')
                })
                
            else:
                print("  ")
                scenario_results.append({
                    'setting': f"{changed_key}={changed_value}",
                    'error': ' '
                })
                
        except Exception as e:
            if "403" in str(e):
                print(" 403 ")
            else:
                print(f" : {str(e)[:50]}...")
            scenario_results.append({
                'setting': f"{changed_key}={changed_value}",
                'error': str(e)[:100]
            })
    
    all_results[scenario['name']] = scenario_results

#  
print(f"\n{'='*80}")
print("   ")
print("="*80)

#    
for scenario_name, results in all_results.items():
    print(f"\n[{scenario_name}]")
    
    #    
    titles = [r['title'] for r in results if 'title' in r]
    unique_titles = set(titles)
    
    if titles:
        print(f"-  : {len(titles)}")
        print(f"-  : {len(unique_titles)}")
        print(f"- : {len(unique_titles)/len(titles)*100:.0f}%")
        
        #  
        print("-  :")
        for r in results:
            if 'title' in r:
                print(f"  • {r['setting']}: {r['title']}")
    else:
        print("-   ")

#  
token_usage = service.get_token_usage()
print(f"\n  :")
print(f"- : {token_usage['total']:,}")

#  
output_file = f"key_variations_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"\n  {output_file} .")

#  
print(f"\n{'='*80}")
print("  ")
print("="*80)

successful_tests = sum(1 for results in all_results.values() for r in results if 'title' in r)
total_tests = sum(len(results) for results in all_results.values())

if successful_tests > 0:
    print(f"\n : {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.0f}%)")
    print("       ")
    print("       ")
else:
    print("\n   ")
    print(" API    .")

if any("403" in str(r.get('error', '')) for results in all_results.values() for r in results):
    print("\n  403   :")
    print("1. Google AI Studio  API  ")
    print("2. .env  ")
    print("3.  ")

print("\n" + "="*80)