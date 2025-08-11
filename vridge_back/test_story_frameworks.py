#!/usr/bin/env python
"""   """
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
print("VideoPlanet   ")
print("=" * 80)

#  
planning_text = """
      3   .
AI         ,
   .
"""

#   
frameworks = [
    ('classic', ''),
    ('hook_immersion', '---'),
    ('pixar', ' '),
    ('deductive', ' '),
    ('inductive', ' '),
    ('documentary', ' ')
]

#  
base_context = {
    'tone': '',
    'genre': '/',
    'concept': '',
    'target': '20-30 ',
    'purpose': '  ',
    'duration': '3',
    'character_name': '',
    'character_description': ''
}

# GeminiService 
print("\n   ...")
try:
    service = GeminiService()
    print(" GeminiService  ")
    
    # Gemini   
    print(" Gemini     ")
    
except Exception as e:
    print(f"   : {str(e)}")
    sys.exit(1)

#  
results = {}
success_count = 0

#   
for framework_key, framework_name in frameworks:
    print(f"\n{'='*60}")
    print(f" : {framework_name} ({framework_key})")
    print("="*60)
    
    #   
    context = base_context.copy()
    context['story_framework'] = framework_key
    
    try:
        #  
        print(f"⏳ {framework_name}    ...")
        result = service.generate_stories_from_planning(planning_text, context)
        
        if result and 'stories' in result and len(result['stories']) > 0:
            stories = result['stories']
            print(f" ! {len(stories)}  ")
            
            #   
            for i, story in enumerate(stories, 1):
                print(f"\n[ {i}]")
                print(f": {story.get('title', 'N/A')}")
                print(f": {story.get('stage', 'N/A')} - {story.get('stage_name', 'N/A')}")
                print(f": {', '.join(story.get('characters', []))}")
                print(f" : {story.get('key_content', 'N/A')}")
                print(f": {story.get('summary', 'N/A')[:100]}...")
            
            results[framework_key] = {
                'success': True,
                'stories': stories,
                'count': len(stories)
            }
            success_count += 1
            
        else:
            print(f" :   .")
            results[framework_key] = {
                'success': False,
                'error': result.get('error', 'Unknown error') if result else 'No result'
            }
            
    except Exception as e:
        print(f"  : {str(e)}")
        results[framework_key] = {
            'success': False,
            'error': str(e)
        }

#   
print(f"\n{'='*60}")
print("   ")
print("="*60)
token_usage = service.get_token_usage()
print(f" : {token_usage['total']:,}")
print(f" : {token_usage['prompt']:,}")
print(f" : {token_usage['response']:,}")

#  
print(f"\n{'='*60}")
print("   ")
print("="*60)
print(f": {success_count}/{len(frameworks)} ({success_count/len(frameworks)*100:.1f}%)")

#   
print("\n   :")
for framework_key, framework_name in frameworks:
    if results[framework_key]['success']:
        stories = results[framework_key]['stories']
        print(f"\n[{framework_name}]")
        
        #    
        stages = [story.get('stage_name', '') for story in stories]
        print(f" : {' → '.join(stages)}")
        
        #     
        first_story = stories[0]
        print(f" : {first_story.get('title', 'N/A')}")

#   
output_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n   {output_file} .")

#    
print(f"\n{'='*60}")
print("    ")
print("="*60)

#     
successful_framework = None
for framework_key, _ in frameworks:
    if results[framework_key]['success']:
        successful_framework = framework_key
        break

if successful_framework:
    test_story = results[successful_framework]['stories'][0]
    test_story['planning_options'] = base_context
    
    print(f"'{test_story.get('title', 'N/A')}'    ...")
    
    try:
        scene_result = service.generate_scenes_from_story(test_story)
        if scene_result and 'scenes' in scene_result:
            scenes = scene_result['scenes']
            print(f" {len(scenes)}   !")
            
            for i, scene in enumerate(scenes, 1):
                print(f"\n[ {i}]")
                print(f": {scene.get('location', 'N/A')}")
                print(f": {scene.get('time', 'N/A')}")
                print(f": {scene.get('action', 'N/A')}")
                
        else:
            print("   ")
            
    except Exception as e:
        print(f"   : {str(e)}")

print("\n" + "="*80)
print(" !")
print("="*80)