#!/usr/bin/env python3
"""
    
        
"""

import os
import sys
import django
import json
from datetime import datetime

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')
django.setup()

from ai_video.services import StoryDevelopmentService, AIVideoService
from ai_video.models import Scene, Story


class ScenePromptTester:
    """   """
    
    def __init__(self):
        self.test_results = {}
        
    def run_detailed_tests(self):
        """  """
        print("=" * 80)
        print("    ")
        print("=" * 80 + "\n")
        
        #    
        mock_scene = self._create_mock_scene()
        
        #  1:   
        self.test_genre_prompts(mock_scene)
        
        #  2:   
        self.test_tone_prompts(mock_scene)
        
        #  3:   
        self.test_intensity_prompts(mock_scene)
        
        #  4:  
        self.test_complex_scenarios(mock_scene)
        
        #     
        self.generate_report()
    
    def test_genre_prompts(self, scene):
        """   """
        print("\n[ 1]   ")
        print("-" * 60)
        
        genres = ['action', 'comedy', 'horror', 'documentary', 'commercial']
        results = {}
        
        for genre in genres:
            prompt = AIVideoService._create_enhanced_prompt(
                scene, genre, 'dramatic', 5
            )
            results[genre] = prompt
            
            print(f"\n{genre.upper()} :")
            print(f" : {prompt['image_prompt'][:150]}...")
            print(f" : {prompt['video_prompt'][:150]}...")
            print(f" : {prompt['motion_intensity']}")
            
        self.test_results['genre_prompts'] = results
        
        #  
        self._analyze_prompt_differences(results, 'genre')
    
    def test_tone_prompts(self, scene):
        """   """
        print("\n[ 2]   ")
        print("-" * 60)
        
        tones = ['professional', 'casual', 'dramatic', 'playful', 'elegant', 'edgy']
        results = {}
        
        for tone in tones:
            prompt = AIVideoService._create_enhanced_prompt(
                scene, 'commercial', tone, 5
            )
            results[tone] = prompt
            
            print(f"\n{tone.upper()} :")
            print(f" : {prompt['image_prompt'][:150]}...")
            style_preset = prompt['image_parameters'].get('style_preset', 'N/A')
            print(f" : {style_preset}")
            
        self.test_results['tone_prompts'] = results
        self._analyze_prompt_differences(results, 'tone')
    
    def test_intensity_prompts(self, scene):
        """   """
        print("\n[ 3]   ")
        print("-" * 60)
        
        intensities = [1, 3, 5, 7, 10]
        results = {}
        
        for intensity in intensities:
            prompt = AIVideoService._create_enhanced_prompt(
                scene, 'action', 'dramatic', intensity
            )
            results[f'intensity_{intensity}'] = prompt
            
            print(f"\n {intensity}:")
            print(f" : {prompt['motion_intensity']}")
            print(f"  ID: {prompt['video_parameters']['motion_bucket_id']}")
            conditioning = prompt['video_parameters']['conditioning_augmentation']
            print(f" : {conditioning}")
            
        self.test_results['intensity_prompts'] = results
        self._analyze_prompt_differences(results, 'intensity')
    
    def test_complex_scenarios(self, scene):
        """  """
        print("\n[ 4]    ")
        print("-" * 60)
        
        scenarios = [
            {'name': 'Intense Action', 'genre': 'action', 'tone': 'edgy', 'intensity': 9},
            {'name': 'Soft Comedy', 'genre': 'comedy', 'tone': 'playful', 'intensity': 2},
            {'name': 'Elegant Commercial', 'genre': 'commercial', 'tone': 'elegant', 'intensity': 4},
            {'name': 'Dark Horror', 'genre': 'horror', 'tone': 'dramatic', 'intensity': 8},
            {'name': 'Professional Doc', 'genre': 'documentary', 'tone': 'professional', 'intensity': 3}
        ]
        
        results = {}
        
        for scenario in scenarios:
            prompt = AIVideoService._create_enhanced_prompt(
                scene, 
                scenario['genre'], 
                scenario['tone'], 
                scenario['intensity']
            )
            results[scenario['name']] = prompt
            
            print(f"\n{scenario['name']}:")
            print(f": {scenario['genre']}, : {scenario['tone']}, : {scenario['intensity']}")
            
            #   
            image_prompt = prompt['image_prompt']
            print(f"\n   :")
            
            #  
            keywords = self._extract_keywords(image_prompt)
            print(f"  -  : {', '.join(keywords[:5])}")
            
            #   
            print(f"\n :")
            print(f"  -  : {prompt['motion_intensity']}")
            print(f"  -  : {prompt['image_parameters'].get('style_preset', 'N/A')}")
            
        self.test_results['complex_scenarios'] = results
    
    def _create_mock_scene(self):
        """    """
        class MockStory:
            def __init__(self):
                self.fps = 30
                
        class MockScene:
            def __init__(self):
                self.order = 1
                self.title = "Opening Scene"
                self.description = "An establishing shot that sets the mood and introduces the main elements"
                self.start_time = 0
                self.end_time = 5
                self.duration = 5
                self.scene_type = 'intro'
                self.story = MockStory()
        
        return MockScene()
    
    def _extract_keywords(self, prompt):
        """   """
        #   
        common_words = {'a', 'the', 'and', 'or', 'with', 'for', 'that', 'shot', 'scene'}
        
        #    
        words = prompt.lower().split()
        keywords = []
        
        for word in words:
            #  
            word = word.strip('.,;:!?')
            #    4  
            if word not in common_words and len(word) > 3:
                keywords.append(word)
        
        #     ( )
        seen = {}
        for word in keywords:
            seen[word] = seen.get(word, 0) + 1
        
        sorted_keywords = sorted(seen.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_keywords]
    
    def _analyze_prompt_differences(self, results, category):
        """  """
        print(f"\n[] {category} ")
        print("-" * 40)
        
        if len(results) < 2:
            print("  .")
            return
        
        #     
        keys = list(results.keys())
        base_key = keys[0]
        base_result = results[base_key]
        
        differences_found = []
        
        for key in keys[1:]:
            result = results[key]
            
            #   
            if base_result['image_prompt'] != result['image_prompt']:
                differences_found.append(f"{key}:   ")
            
            #   
            if base_result['motion_intensity'] != result['motion_intensity']:
                differences_found.append(f"{key}:    ({result['motion_intensity']})")
            
            #  
            if base_result.get('image_parameters') != result.get('image_parameters'):
                differences_found.append(f"{key}:   ")
        
        if differences_found:
            print(f"  ({len(differences_found)}):")
            for diff in differences_found[:5]:  #  5 
                print(f"  - {diff}")
        else:
            print("   !")
    
    def generate_report(self):
        """  """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'/home/winnmedia/VideoPlanet/vridge_back/scene_prompt_test_{timestamp}.json'
        
        #   
        report = {
            'timestamp': timestamp,
            'test_categories': list(self.test_results.keys()),
            'test_results': self.test_results,
            'summary': self._generate_summary()
        }
        
        # JSON  
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n : {filename}")
        
        #  
        print("\n" + "=" * 80)
        print(" ")
        print("=" * 80)
        print(report['summary']['conclusion'])
    
    def _generate_summary(self):
        """  """
        total_tests = sum(len(results) for results in self.test_results.values())
        
        #    
        unique_counts = {}
        for category, results in self.test_results.items():
            unique_prompts = set()
            for key, result in results.items():
                unique_prompts.add(result['image_prompt'])
            unique_counts[category] = len(unique_prompts)
        
        avg_uniqueness = sum(unique_counts.values()) / len(unique_counts) if unique_counts else 0
        
        return {
            'total_tests': total_tests,
            'categories_tested': len(self.test_results),
            'unique_prompts_per_category': unique_counts,
            'average_uniqueness': avg_uniqueness,
            'conclusion': f"     .  {avg_uniqueness:.1f}   ."
        }


def main():
    """  """
    tester = ScenePromptTester()
    tester.run_detailed_tests()


if __name__ == '__main__':
    main()