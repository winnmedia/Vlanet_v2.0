#!/usr/bin/env python
"""
    
 (, , )     
"""

import os
import sys
import django
import json
from datetime import datetime
from typing import Dict, List, Any

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')
django.setup()

from ai_video.services import StoryDevelopmentService
from projects.models import Project


class StoryDevelopmentTester:
    """   """
    
    def __init__(self):
        self.test_results = []
        self.comparison_results = {}
        
    def run_all_tests(self):
        """  """
        print("=" * 80)
        print("    ")
        print("=" * 80 + "\n")
        
        #  1:   
        self.test_genre_variations()
        
        #  2:   
        self.test_tone_variations()
        
        #  3:   
        self.test_intensity_variations()
        
        #  4:   
        self.test_complex_variations()
        
        #  
        self.save_results()
        
        #   
        self.print_summary()
    
    def test_genre_variations(self):
        """ 1:     """
        print("\n[ 1]     ")
        print("-" * 60)
        
        base_settings = {
            'tone': 'dramatic',
            'intensity': 5,
            'target_audience': 'young_adults',
            'key_message': 'Innovation and Excellence',
            'brand_values': ['quality', 'innovation', 'trust']
        }
        
        genres = ['action', 'comedy', 'horror', 'documentary', 'commercial']
        results = {}
        
        for genre in genres:
            print(f"\n : {genre} ")
            
            #   
            mock_project = self._create_mock_project({
                **base_settings,
                'genre': genre
            })
            
            #  
            result = StoryDevelopmentService.develop_story_from_project(mock_project)
            
            if result['success']:
                results[genre] = result
                print(f" {genre}   ")
                
                #   
                story_structure = result['story_structure']
                print(f"  - Opening: {story_structure['act1_opening'][:100]}...")
                print(f"  - Theme: {story_structure['overall_theme']}")
            else:
                print(f" {genre}   : {result['error']}")
        
        #  
        self._compare_results(results, 'genre_variations')
        
    def test_tone_variations(self):
        """ 2:    """
        print("\n[ 2]     ")
        print("-" * 60)
        
        base_settings = {
            'genre': 'action',
            'intensity': 5,
            'target_audience': 'young_adults',
            'key_message': 'Innovation and Excellence',
            'brand_values': ['quality', 'innovation', 'trust']
        }
        
        tones = ['professional', 'casual', 'dramatic', 'playful', 'elegant', 'edgy']
        results = {}
        
        for tone in tones:
            print(f"\n : {tone} ")
            
            mock_project = self._create_mock_project({
                **base_settings,
                'tone': tone
            })
            
            result = StoryDevelopmentService.develop_story_from_project(mock_project)
            
            if result['success']:
                results[tone] = result
                print(f" {tone}   ")
                
                #    
                visual_style = result['style_guide']['visual_style']
                print(f"  - Visual Style: {visual_style.get('visual_style', 'N/A')}")
                print(f"  - Lighting: {visual_style.get('lighting', 'N/A')}")
                print(f"  - Color Palette: {visual_style.get('color_palette', 'N/A')}")
            else:
                print(f" {tone}   : {result['error']}")
        
        self._compare_results(results, 'tone_variations')
    
    def test_intensity_variations(self):
        """ 3:    """
        print("\n[ 3]     ")
        print("-" * 60)
        
        base_settings = {
            'genre': 'action',
            'tone': 'dramatic',
            'target_audience': 'young_adults',
            'key_message': 'Innovation and Excellence',
            'brand_values': ['quality', 'innovation', 'trust']
        }
        
        intensities = [1, 3, 5, 7, 10]
        results = {}
        
        for intensity in intensities:
            print(f"\n :  {intensity}")
            
            mock_project = self._create_mock_project({
                **base_settings,
                'intensity': intensity
            })
            
            result = StoryDevelopmentService.develop_story_from_project(mock_project)
            
            if result['success']:
                results[f'intensity_{intensity}'] = result
                print(f"  {intensity}   ")
                
                #    
                intensity_guide = result['style_guide']['intensity_guide']
                print(f"  - Motion: {intensity_guide.get('motion', 'N/A')}")
                print(f"  - Effects: {intensity_guide.get('effects', 'N/A')}")
                print(f"  - Pace: {intensity_guide.get('pace', 'N/A')}")
            else:
                print(f"  {intensity}   : {result['error']}")
        
        self._compare_results(results, 'intensity_variations')
    
    def test_complex_variations(self):
        """ 4:   """
        print("\n[ 4]    ")
        print("-" * 60)
        
        test_combinations = [
            {
                'name': 'Intense Action Drama',
                'genre': 'action',
                'tone': 'dramatic',
                'intensity': 9
            },
            {
                'name': 'Casual Comedy',
                'genre': 'comedy',
                'tone': 'casual',
                'intensity': 3
            },
            {
                'name': 'Elegant Commercial',
                'genre': 'commercial',
                'tone': 'elegant',
                'intensity': 5
            },
            {
                'name': 'Edgy Horror',
                'genre': 'horror',
                'tone': 'edgy',
                'intensity': 8
            },
            {
                'name': 'Professional Documentary',
                'genre': 'documentary',
                'tone': 'professional',
                'intensity': 2
            }
        ]
        
        results = {}
        
        for combo in test_combinations:
            print(f"\n : {combo['name']}")
            
            mock_project = self._create_mock_project({
                'genre': combo['genre'],
                'tone': combo['tone'],
                'intensity': combo['intensity'],
                'target_audience': 'young_adults',
                'key_message': 'Innovation and Excellence',
                'brand_values': ['quality', 'innovation', 'trust']
            })
            
            result = StoryDevelopmentService.develop_story_from_project(mock_project)
            
            if result['success']:
                results[combo['name']] = result
                print(f" {combo['name']}   ")
                
                #    
                if 'scene_prompts' in result:
                    first_scene = result['scene_prompts'][0] if result['scene_prompts'] else None
                    if first_scene:
                        print(f"  -   : {first_scene.get('title', 'N/A')}")
                        print(f"  -  : {first_scene.get('visual_prompt', 'N/A')[:150]}...")
            else:
                print(f" {combo['name']}   : {result['error']}")
        
        self._compare_results(results, 'complex_variations')
    
    def _create_mock_project(self, settings: Dict) -> Any:
        """    """
        class MockProject:
            def __init__(self, project_data):
                self.project_data = project_data
                self.id = 'test_project'
                self.name = 'Test Project'
                self.description = 'Test project for story development validation'
        
        return MockProject(settings)
    
    def _compare_results(self, results: Dict, test_name: str):
        """    """
        print(f"\n[] {test_name}  ")
        print("-" * 40)
        
        if len(results) < 2:
            print("   .")
            return
        
        #   
        story_structures = {}
        for key, result in results.items():
            if 'story_structure' in result:
                story_structures[key] = result['story_structure']
        
        #  
        differences = self._calculate_differences(story_structures)
        
        self.comparison_results[test_name] = {
            'total_variations': len(results),
            'unique_elements': differences['unique_count'],
            'similarity_score': differences['similarity'],
            'key_differences': differences['key_differences']
        }
        
        print(f"  : {len(results)}")
        print(f"  : {differences['unique_count']}")
        print(f" : {differences['similarity']:.2f}%")
        
        if differences['key_differences']:
            print("\n :")
            for diff in differences['key_differences'][:3]:
                print(f"  - {diff}")
    
    def _calculate_differences(self, structures: Dict) -> Dict:
        """   """
        if not structures:
            return {
                'unique_count': 0,
                'similarity': 100.0,
                'key_differences': []
            }
        
        #   
        all_texts = []
        for key, structure in structures.items():
            text = json.dumps(structure)
            all_texts.append(text)
        
        #  
        unique_texts = set(all_texts)
        unique_count = len(unique_texts)
        
        #   ( )
        if len(all_texts) > 1:
            #    
            base_text = all_texts[0]
            similarities = []
            for text in all_texts[1:]:
                #    ( )
                common_chars = sum(1 for c1, c2 in zip(base_text, text) if c1 == c2)
                max_len = max(len(base_text), len(text))
                similarity = (common_chars / max_len) * 100 if max_len > 0 else 0
                similarities.append(similarity)
            
            avg_similarity = sum(similarities) / len(similarities) if similarities else 100
        else:
            avg_similarity = 100
        
        #   
        key_differences = []
        structure_keys = list(structures.keys())
        if len(structure_keys) >= 2:
            struct1 = structures[structure_keys[0]]
            struct2 = structures[structure_keys[1]]
            
            for key in struct1:
                if key in struct2:
                    if struct1[key] != struct2[key]:
                        key_differences.append(f"{key}  ")
        
        return {
            'unique_count': unique_count,
            'similarity': 100 - avg_similarity,  #    
            'key_differences': key_differences
        }
    
    def save_results(self):
        """  JSON  """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'/home/winnmedia/VideoPlanet/vridge_back/story_development_test_{timestamp}.json'
        
        results = {
            'timestamp': timestamp,
            'test_summary': {
                'total_tests': len(self.comparison_results),
                'test_categories': list(self.comparison_results.keys())
            },
            'comparison_results': self.comparison_results,
            'conclusion': self._generate_conclusion()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n : {filename}")
    
    def _generate_conclusion(self) -> Dict:
        """  """
        total_variations = sum(
            r['total_variations'] 
            for r in self.comparison_results.values()
        )
        
        avg_unique = sum(
            r['unique_elements'] 
            for r in self.comparison_results.values()
        ) / len(self.comparison_results) if self.comparison_results else 0
        
        return {
            'system_works': avg_unique > 0,
            'total_variations_tested': total_variations,
            'average_unique_elements': avg_unique,
            'verdict': '      .' if avg_unique > 0 else '   .'
        }
    
    def print_summary(self):
        """   """
        print("\n" + "=" * 80)
        print("    ")
        print("=" * 80)
        
        conclusion = self._generate_conclusion()
        
        print(f"\n  : {conclusion['total_variations_tested']}")
        print(f"  : {conclusion['average_unique_elements']:.1f}")
        print(f"\n : {conclusion['verdict']}")
        
        if conclusion['system_works']:
            print("\n   !")
            print(" (, , )    .")
        else:
            print("\n   ")
            print("       .")
        
        print("\n" + "=" * 80)


def main():
    """  """
    tester = StoryDevelopmentTester()
    tester.run_all_tests()


if __name__ == '__main__':
    main()