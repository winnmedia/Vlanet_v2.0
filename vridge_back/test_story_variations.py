#!/usr/bin/env python
"""       """
import os
import sys
import django
import json
from datetime import datetime
import hashlib

# Django 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_base')
django.setup()

from video_planning.gemini_service import GeminiService

print("=" * 80)
print("VideoPlanet    ")
print("=" * 80)

#   ()
planning_text = """
      
       5  .
    .
"""

#   ()
test_context = {
    'tone': '',
    'genre': '',
    'concept': '',
    'target': '10-20',
    'purpose': ' ',
    'duration': '5',
    'story_framework': 'pixar',  #   
    'character_name': '',
    'character_description': '  '
}

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

# 5   
print(f"\n   5   ")
print(f": {planning_text[:50]}...")
print(f": {test_context['story_framework']}")
print("=" * 80)

all_results = []
unique_stories = set()
story_variations = {}

for attempt in range(5):
    print(f"\n  {attempt + 1}/5")
    print("-" * 60)
    
    try:
        #  
        result = service.generate_stories_from_planning(planning_text, test_context)
        
        if result and 'stories' in result and len(result['stories']) > 0:
            stories = result['stories']
            print(f" ! {len(stories)}  ")
            
            #    
            attempt_fingerprints = []
            
            for i, story in enumerate(stories, 1):
                fingerprint = get_story_fingerprint(story)
                attempt_fingerprints.append(fingerprint)
                
                if fingerprint not in story_variations:
                    story_variations[fingerprint] = {
                        'count': 0,
                        'story': story,
                        'first_seen': attempt + 1
                    }
                story_variations[fingerprint]['count'] += 1
                
                print(f"\n  [ {i}] (ID: {fingerprint})")
                print(f"  : {story.get('title', 'N/A')}")
                print(f"  : {story.get('stage_name', 'N/A')}")
                print(f"  : {story.get('key_content', 'N/A')[:80]}...")
            
            all_results.append({
                'attempt': attempt + 1,
                'stories': stories,
                'fingerprints': attempt_fingerprints
            })
            
            #   
            unique_stories.update(attempt_fingerprints)
            
        else:
            print(f" :   .")
            
    except Exception as e:
        print(f"  : {str(e)}")

#  
print(f"\n{'='*80}")
print("   ")
print("="*80)

total_stories = sum(len(r['stories']) for r in all_results)
print(f"\n   : {total_stories}")
print(f"  : {len(unique_stories)}")
print(f" : {len(unique_stories)/total_stories*100:.1f}%")

#   
print("\n   :")
duplicates = 0
for fp, data in story_variations.items():
    if data['count'] > 1:
        duplicates += 1
        print(f"\n  (ID: {fp})")
        print(f"  : {data['story'].get('title', 'N/A')}")
        print(f"   : {data['count']}")
        print(f"   : {data['first_seen']} ")

if duplicates == 0:
    print("\n   !")

#  
print(f"\n{'='*80}")
print("     ")
print("="*80)

frameworks = ['classic', 'hook_immersion', 'documentary']
framework_results = {}

for framework in frameworks:
    print(f"\n {framework}  ")
    test_context['story_framework'] = framework
    
    try:
        result = service.generate_stories_from_planning(planning_text, test_context)
        
        if result and 'stories' in result:
            stories = result['stories']
            print(f" {len(stories)}  ")
            
            #    
            if stories:
                first = stories[0]
                print(f"   : {first.get('title', 'N/A')}")
                print(f"  : {first.get('stage_name', 'N/A')}")
                
            framework_results[framework] = stories
            
    except Exception as e:
        print(f" : {str(e)}")

#    
print(f"\n{'='*80}")
print("   ")
print("="*80)

for framework, stories in framework_results.items():
    if stories:
        print(f"\n[{framework}]")
        stages = [s.get('stage_name', '') for s in stories]
        print(f" : {' → '.join(stages)}")
        
        #   
        all_text = ' '.join([s.get('summary', '') + s.get('key_content', '') for s in stories])
        keywords = set(word for word in all_text.split() if len(word) > 3 and word not in ['', '', ''])
        print(f" : {', '.join(list(keywords)[:5])}")

#   
output_file = f"story_variation_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'planning_text': planning_text,
        'test_context': test_context,
        'multiple_attempts': all_results,
        'unique_story_count': len(unique_stories),
        'total_story_count': total_stories,
        'diversity_ratio': len(unique_stories)/total_stories if total_stories > 0 else 0,
        'framework_comparison': {k: [{'title': s.get('title'), 'stage': s.get('stage_name')} for s in v] for k, v in framework_results.items()}
    }, f, ensure_ascii=False, indent=2)

print(f"\n   {output_file} .")
print("\n" + "="*80)
print(" !")
print("="*80)