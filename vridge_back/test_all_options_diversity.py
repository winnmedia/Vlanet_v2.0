#!/usr/bin/env python
"""     """
import os
import sys
import django
import json
from datetime import datetime
import hashlib
from itertools import product

# Django 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_base')
django.setup()

from video_planning.gemini_service import GeminiService

print("=" * 80)
print("VideoPlanet    ")
print("=" * 80)

#   
options = {
    'tone': ['', '', '', ' ', ''],
    'genre': ['', '', '', '', ''],
    'concept': ['AI ', '', '', '', ''],
    'target': ['10', '20-30', '40-50', '', ''],
    'purpose': ['', '', '', '', ''],
    'duration': ['1', '3', '5', '10', '30'],
    'story_framework': ['classic', 'hook_immersion', 'pixar', 'deductive', 'inductive', 'documentary'],
    'development_level': ['minimal', 'light', 'balanced', 'detailed']
}

#  
advanced_options = {
    'aspectRatio': ['16:9', '9:16', '1:1', '4:3', '21:9'],
    'platform': ['YouTube', 'Instagram', 'TikTok', 'TV', ''],
    'colorTone': ['', '', '', '', ''],
    'editingStyle': [' ', '', '', '', ''],
    'musicStyle': ['', '', '', '', '']
}

#  
base_planning = """
      ,
   AI     
"""

# GeminiService 
print("\n   ...")
try:
    service = GeminiService()
    print(" GeminiService  ")
except Exception as e:
    print(f"   : {str(e)}")
    sys.exit(1)

#     
def get_story_fingerprint(story):
    """    """
    fingerprint = f"{story.get('title', '')}|{story.get('summary', '')}|{story.get('key_content', '')}"
    return hashlib.md5(fingerprint.encode()).hexdigest()[:8]

#  
all_results = {}
unique_stories = set()
total_tests = 0
success_count = 0

# 1.   
print(f"\n{'='*80}")
print("    ")
print("="*80)

for option_name, option_values in options.items():
    print(f"\n {option_name}   ({len(option_values)} )")
    option_results = {}
    
    for value in option_values:
        #   
        context = {
            'tone': '',
            'genre': '',
            'concept': '',
            'target': ' ',
            'purpose': ' ',
            'duration': '5',
            'story_framework': 'classic',
            'development_level': 'balanced'
        }
        
        #   
        context[option_name] = value
        
        print(f"  - {value}: ", end="", flush=True)
        total_tests += 1
        
        try:
            result = service.generate_stories_from_planning(base_planning, context)
            
            if result and 'stories' in result and len(result['stories']) > 0:
                stories = result['stories']
                fingerprints = [get_story_fingerprint(s) for s in stories]
                unique_stories.update(fingerprints)
                
                option_results[value] = {
                    'success': True,
                    'story_count': len(stories),
                    'first_title': stories[0].get('title', 'N/A'),
                    'fingerprints': fingerprints
                }
                print(f" {len(stories)}  ")
                success_count += 1
            else:
                option_results[value] = {'success': False, 'error': ' '}
                print(" ")
                
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg:
                print(" 403  (API  )")
            else:
                print(f" : {error_msg[:50]}...")
            option_results[value] = {'success': False, 'error': error_msg}
    
    all_results[option_name] = option_results

# 2.   (   )
print(f"\n{'='*80}")
print("   ")
print("="*80)

test_combinations = [
    {
        'name': '  ',
        'context': {
            'tone': ' ',
            'genre': '',
            'concept': 'AI ',
            'target': '20-30',
            'purpose': '',
            'duration': '10',
            'story_framework': 'hook_immersion',
            'development_level': 'detailed',
            'aspectRatio': '21:9',
            'platform': '',
            'colorTone': '',
            'editingStyle': ' ',
            'musicStyle': ''
        }
    },
    {
        'name': ' ',
        'context': {
            'tone': '',
            'genre': '',
            'concept': '',
            'target': '',
            'purpose': '',
            'duration': '30',
            'story_framework': 'documentary',
            'development_level': 'detailed',
            'aspectRatio': '16:9',
            'platform': 'YouTube',
            'colorTone': '',
            'editingStyle': '',
            'musicStyle': ''
        }
    },
    {
        'name': 'SNS  ',
        'context': {
            'tone': '',
            'genre': '',
            'concept': '',
            'target': '10',
            'purpose': '',
            'duration': '1',
            'story_framework': 'pixar',
            'development_level': 'minimal',
            'aspectRatio': '9:16',
            'platform': 'TikTok',
            'colorTone': '',
            'editingStyle': '',
            'musicStyle': ''
        }
    }
]

combination_results = {}
for combo in test_combinations:
    print(f"\n {combo['name']} ")
    total_tests += 1
    
    try:
        result = service.generate_stories_from_planning(base_planning, combo['context'])
        
        if result and 'stories' in result:
            stories = result['stories']
            fingerprints = [get_story_fingerprint(s) for s in stories]
            unique_stories.update(fingerprints)
            
            combination_results[combo['name']] = {
                'success': True,
                'story_count': len(stories),
                'titles': [s.get('title', 'N/A') for s in stories],
                'fingerprints': fingerprints
            }
            
            print(f" ! {len(stories)}  ")
            for i, story in enumerate(stories[:2], 1):  #  2 
                print(f"    {i}: {story.get('title', 'N/A')}")
            
            success_count += 1
        else:
            print("   ")
            combination_results[combo['name']] = {'success': False}
            
    except Exception as e:
        print(f" : {str(e)[:100]}...")
        combination_results[combo['name']] = {'success': False, 'error': str(e)}

# 3.   
print(f"\n{'='*80}")
print("   ")
print("="*80)

extreme_combos = [
    {
        'name': ' ',
        'context': {
            'development_level': 'minimal',
            'duration': '1',
            'story_framework': 'classic'
        }
    },
    {
        'name': ' ',
        'context': {
            **{k: v[-1] for k, v in options.items()},
            **{k: v[-1] for k, v in advanced_options.items()}
        }
    }
]

for combo in extreme_combos:
    print(f"\n {combo['name']}")
    total_tests += 1
    
    try:
        result = service.generate_stories_from_planning(base_planning, combo['context'])
        
        if result and 'stories' in result:
            stories = result['stories']
            print(f" {len(stories)}  ")
            success_count += 1
        else:
            print(" ")
            
    except Exception as e:
        print(f" : {str(e)[:50]}...")

#  
print(f"\n{'='*80}")
print("   ")
print("="*80)

print(f"\n : {total_tests}")
print(f": {success_count} ({success_count/total_tests*100:.1f}%)")
print(f"  : {len(unique_stories)}")

#   
print("\n  :")
for option_name, results in all_results.items():
    success = sum(1 for r in results.values() if r.get('success', False))
    total = len(results)
    print(f"- {option_name}: {success}/{total} ({success/total*100:.1f}%)")

#  
token_usage = service.get_token_usage()
print(f"\n   :")
print(f"- : {token_usage['total']:,}")
print(f"- : {token_usage['prompt']:,}")
print(f"- : {token_usage['response']:,}")

#   
output_file = f"diversity_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'test_summary': {
            'total_tests': total_tests,
            'success_count': success_count,
            'success_rate': success_count/total_tests if total_tests > 0 else 0,
            'unique_stories': len(unique_stories)
        },
        'option_results': all_results,
        'combination_results': combination_results,
        'token_usage': token_usage
    }, f, ensure_ascii=False, indent=2)

print(f"\n   {output_file} .")

# 403   
if any('403' in str(r.get('error', '')) for results in all_results.values() for r in results.values()):
    print("\n  403   :")
    print("1. Google Cloud Console API   ")
    print("2. HTTP referer    localhost ")
    print("3.   API   ( )")
    print("4. Railway   ")

print("\n" + "="*80)
print(" !")
print("="*80)