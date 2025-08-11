#!/usr/bin/env python
"""      """
import os
import sys
import django
import json
from datetime import datetime
import hashlib
from collections import defaultdict

# Django 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_base')

# 403     
os.environ['HTTP_REFERER'] = 'http://localhost:3000'

django.setup()

from video_planning.gemini_service import GeminiService

print("=" * 80)
print("VideoPlanet    ")
print("=" * 80)

#    (  )
test_options = {
    'tone': ['', '', ''],
    'genre': ['', '', ''],
    'concept': ['AI ', '', ''],
    'target': ['10', '20-30', ''],
    'purpose': ['', '', ''],
    'duration': ['1', '5', '30'],
    'story_framework': ['classic', 'pixar', 'documentary'],
    'development_level': ['minimal', 'balanced', 'detailed']
}

#   ()
advanced_options = {
    'aspectRatio': ['16:9', '9:16'],
    'platform': ['YouTube', 'TikTok'],
    'colorTone': ['', ''],
    'editingStyle': [' ', ''],
    'musicStyle': ['', '']
}

#   ()
base_planning = """
     ,
     
"""

# GeminiService 
print("\n   ...")
service = None
try:
    #   API  
    service = GeminiService()
    print(" GeminiService  ")
    
    #  
    test_prompt = "  ."
    test_response = service.model.generate_content(test_prompt)
    print(f" API  : {test_response.text[:50]}...")
    
except Exception as e:
    if "403" in str(e):
        print(" 403   - API   ")
        print("\n  :")
        print("1. Google AI Studio  API   ( )")
        print("2. .env  GOOGLE_API_KEY ")
        print("3.  ")
    else:
        print(f"  : {str(e)}")
    sys.exit(1)

#   
def get_story_fingerprint(story):
    """   """
    key_elements = [
        story.get('title', ''),
        story.get('stage_name', ''),
        story.get('key_content', ''),
        story.get('summary', '')
    ]
    fingerprint = '|'.join(key_elements)
    return hashlib.md5(fingerprint.encode()).hexdigest()[:8]

def analyze_story_content(story, option_name, option_value):
    """    """
    content = f"{story.get('title', '')} {story.get('summary', '')} {story.get('key_content', '')}"
    content_lower = content.lower()
    
    #   
    keyword_map = {
        'tone': {
            '': ['', '', '', '', ''],
            '': ['', '', '', '', ''],
            '': ['', '', '', '', '']
        },
        'genre': {
            '': ['', '', '', '', ''],
            '': ['', '', '', '', ''],
            '': ['', '', '', '', '']
        },
        'duration': {
            '1': ['', '', '', ''],
            '5': ['', '', ''],
            '30': ['', '', '', '']
        }
    }
    
    #   
    if option_name in keyword_map and option_value in keyword_map[option_name]:
        keywords = keyword_map[option_name][option_value]
        matches = sum(1 for keyword in keywords if keyword in content_lower)
        return matches > 0
    
    return False

#  
all_results = {}
unique_stories = set()
option_reflection_stats = defaultdict(lambda: {'reflected': 0, 'total': 0})

# 1.   
print(f"\n{'='*80}")
print("     ")
print("="*80)

for option_name, option_values in test_options.items():
    print(f"\n [{option_name}]  ({len(option_values)} )")
    option_results = {}
    
    for value in option_values:
        #   (  )
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
        
        print(f"\n  [{value}]:")
        
        try:
            result = service.generate_stories_from_planning(base_planning, context)
            
            if result and 'stories' in result and len(result['stories']) > 0:
                stories = result['stories']
                
                #  
                fingerprints = []
                reflection_count = 0
                
                for story in stories:
                    fp = get_story_fingerprint(story)
                    fingerprints.append(fp)
                    unique_stories.add(fp)
                    
                    #    
                    if analyze_story_content(story, option_name, value):
                        reflection_count += 1
                
                reflection_rate = reflection_count / len(stories) * 100
                option_reflection_stats[option_name]['reflected'] += reflection_count
                option_reflection_stats[option_name]['total'] += len(stories)
                
                #  
                print(f"     {len(stories)}  ")
                print(f"      : {reflection_rate:.1f}%")
                print(f"      : {stories[0].get('title', 'N/A')}")
                
                #   
                if stories and reflection_count > 0:
                    for story in stories[:1]:  #  
                        if analyze_story_content(story, option_name, value):
                            print(f"      : {story.get('summary', '')[:100]}...")
                
                option_results[value] = {
                    'success': True,
                    'story_count': len(stories),
                    'fingerprints': fingerprints,
                    'reflection_rate': reflection_rate,
                    'sample_title': stories[0].get('title', 'N/A')
                }
                
            else:
                print(f"      ")
                option_results[value] = {'success': False}
                
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg:
                print(f"     403 ")
            else:
                print(f"     : {error_msg[:50]}...")
            option_results[value] = {'success': False, 'error': error_msg}
    
    all_results[option_name] = option_results

# 2.   ( )
print(f"\n{'='*80}")
print("     ")
print("="*80)

test_combinations = [
    {
        'name': '  ',
        'context': {
            'tone': ' ',
            'genre': '',
            'concept': 'AI ',
            'target': '10',
            'purpose': '',
            'duration': '5',
            'story_framework': 'hook_immersion',
            'development_level': 'detailed'
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
            'development_level': 'detailed'
        }
    },
    {
        'name': 'SNS  ',
        'context': {
            'tone': '',
            'genre': '',
            'concept': '',
            'target': '20-30',
            'purpose': '',
            'duration': '1',
            'story_framework': 'pixar',
            'development_level': 'minimal',
            'aspectRatio': '9:16',
            'platform': 'TikTok'
        }
    }
]

combo_results = {}
for combo in test_combinations:
    print(f"\n [{combo['name']}]")
    
    try:
        result = service.generate_stories_from_planning(base_planning, combo['context'])
        
        if result and 'stories' in result:
            stories = result['stories']
            
            print(f"   {len(stories)}  ")
            
            #       
            for i, story in enumerate(stories[:2], 1):
                print(f"\n  [ {i}]")
                print(f"  : {story.get('title', 'N/A')}")
                print(f"  : {story.get('stage_name', 'N/A')}")
                print(f"  : {story.get('summary', 'N/A')[:100]}...")
            
            combo_results[combo['name']] = {
                'success': True,
                'story_count': len(stories),
                'titles': [s.get('title', 'N/A') for s in stories]
            }
            
        else:
            print(f"    ")
            combo_results[combo['name']] = {'success': False}
            
    except Exception as e:
        print(f"   : {str(e)[:100]}...")
        combo_results[combo['name']] = {'success': False, 'error': str(e)}

# 3.  
print(f"\n{'='*80}")
print("   ")
print("="*80)

extreme_tests = [
    {
        'name': '  (1 )',
        'context': {
            'duration': '1',
            'development_level': 'minimal',
            'story_framework': 'classic'
        }
    },
    {
        'name': '  (30 )',
        'context': {
            'duration': '30',
            'development_level': 'detailed',
            'story_framework': 'documentary',
            'tone': '',
            'genre': '',
            'purpose': ''
        }
    }
]

for test in extreme_tests:
    print(f"\n[{test['name']}]")
    
    try:
        result = service.generate_stories_from_planning(base_planning, test['context'])
        
        if result and 'stories' in result:
            stories = result['stories']
            print(f"   {len(stories)}  ")
            
            #   
            total_length = sum(len(s.get('summary', '')) + len(s.get('key_content', '')) for s in stories)
            print(f"     : {total_length}")
            
        else:
            print(f"   ")
            
    except Exception as e:
        print(f"   : {str(e)[:50]}...")

#  
print(f"\n{'='*80}")
print("   ")
print("="*80)

#  
total_tests = sum(len(results) for results in all_results.values()) + len(combo_results) + len(extreme_tests)
success_tests = sum(1 for results in all_results.values() for r in results.values() if r.get('success', False))
success_tests += sum(1 for r in combo_results.values() if r.get('success', False))

print(f"\n  :")
print(f"-  : {total_tests}")
print(f"- : {success_tests}")
print(f"-   : {len(unique_stories)}")

#  
print(f"\n   :")
for option_name, stats in option_reflection_stats.items():
    if stats['total'] > 0:
        avg_rate = stats['reflected'] / stats['total'] * 100
        print(f"- {option_name}: {avg_rate:.1f}%")

#   
print(f"\n   :")
for option_name, results in all_results.items():
    success_results = [r for r in results.values() if r.get('success', False)]
    if success_results:
        #      
        all_fps = []
        for r in success_results:
            all_fps.extend(r.get('fingerprints', []))
        
        unique_fps = len(set(all_fps))
        total_fps = len(all_fps)
        diversity_rate = unique_fps / total_fps * 100 if total_fps > 0 else 0
        
        print(f"- {option_name}: {unique_fps}/{total_fps}  ({diversity_rate:.1f}%)")

#  
token_usage = service.get_token_usage()
print(f"\n   :")
print(f"- : {token_usage['total']:,}")
print(f"- : {token_usage['prompt']:,}")
print(f"- : {token_usage['response']:,}")

#   
output_file = f"comprehensive_story_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'test_summary': {
            'total_tests': total_tests,
            'success_tests': success_tests,
            'unique_stories': len(unique_stories),
            'option_reflection_stats': dict(option_reflection_stats)
        },
        'individual_results': all_results,
        'combination_results': combo_results,
        'token_usage': token_usage
    }, f, ensure_ascii=False, indent=2)

print(f"\n   {output_file} .")

#  
print(f"\n{'='*80}")
print("  ")
print("="*80)
print("\n        ")
print("       ")
print("      ")

if any("403" in str(r.get('error', '')) for results in all_results.values() for r in results.values()):
    print("\n    403  ")
    print("   → Google AI Studio  API   ")

print("\n" + "="*80)