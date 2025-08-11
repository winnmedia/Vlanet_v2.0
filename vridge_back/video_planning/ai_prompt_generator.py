"""
AI      
"""
import json
from typing import Dict, List, Optional
import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class VideoPlanningPromptGenerator:
    """   AI  """
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if self.api_key:
            openai.api_key = self.api_key
    
    def generate_quick_suggestions(self, project_data: Dict) -> Dict:
        """     """
        try:
            prompt = self._build_suggestion_prompt(project_data)
            
            #  OpenAI API  (API     )
            if not self.api_key:
                return self._get_dummy_suggestions(project_data)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "   .    ."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return self._parse_suggestion_response(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"AI   : {str(e)}")
            return self._get_dummy_suggestions(project_data)
    
    def generate_full_planning(self, planning_data: Dict) -> Dict:
        """   """
        try:
            #    
            template = self._get_planning_template(planning_data['projectType'])
            
            # AI  
            prompt = self._build_full_planning_prompt(planning_data, template)
            
            #  API    
            if not self.api_key:
                return self._get_dummy_full_planning(planning_data)
            
            response = openai.ChatCompletion.create(
                model="gpt-4" if planning_data.get('enableProOptions') else "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "   .    ."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            return self._parse_planning_response(response.choices[0].message.content, planning_data)
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return self._get_dummy_full_planning(planning_data)
    
    def _build_suggestion_prompt(self, data: Dict) -> str:
        """    """
        return f"""
              :
        -  : {data.get('project_type')}
        - : {data.get('main_topic')}
        -  : {data.get('target_audience')}
        -  : {data.get('duration')}
        
          :
        1.   ()
        2.   3-5
        3.   1-2
        """
    
    def _build_full_planning_prompt(self, data: Dict, template: Dict) -> str:
        """     """
        pro_options = ""
        if data.get('enableProOptions'):
            pro_options = f"""
              :
            - : {data.get('colorTone')}
            -  : {data.get('aspectRatio')}
            -  : {data.get('cameraType')}
            - : {data.get('lensType')}
            -  : {data.get('cameraMovement')}
            """
        
        return f"""
              :
        
         :
        -  : {data.get('projectType')}
        -  : {data.get('duration')}
        -  : {data.get('targetAudience')}
        - : {data.get('mainTopic')}
        -  : {data.get('keyMessage')}
        -  : {data.get('desiredMood')}
        
        {pro_options}
        
          :
        1.    (200)
        2.  4  ( 100)
        3.   3  ( 12,  50)
        4.   
        5.   
        """
    
    def _get_planning_template(self, project_type: str) -> Dict:
        """   """
        templates = {
            'youtube': {
                'structure': '(10%) - (70%) - (20%)',
                'key_elements': ['', '', 'CTA'],
                'tips': ' 15 '
            },
            'corporate': {
                'structure': ' -  -  - ',
                'key_elements': ['', '', ''],
                'tips': '   '
            },
            'advertisement': {
                'structure': ' -  -  - ',
                'key_elements': ['', '', 'CTA'],
                'tips': '   '
            },
            'documentary': {
                'structure': ' -  -  - ',
                'key_elements': ['', '', ''],
                'tips': '   '
            }
        }
        return templates.get(project_type, templates['youtube'])
    
    def _parse_suggestion_response(self, response: str) -> Dict:
        """AI    """
        #       
        lines = response.strip().split('\n')
        return {
            'structure': lines[0] if len(lines) > 0 else '',
            'keywords': lines[1].split(',') if len(lines) > 1 else [],
            'tips': lines[2] if len(lines) > 2 else ''
        }
    
    def _parse_planning_response(self, response: str, original_data: Dict) -> Dict:
        """AI    """
        #       
        return {
            'title': original_data.get('mainTopic', ' '),
            'planning': response[:500],  #  
            'stories': self._generate_stories_from_response(response),
            'scenes': self._generate_scenes_from_response(response),
            'id': None  #   ID 
        }
    
    def _generate_stories_from_response(self, response: str) -> List[Dict]:
        """  """
        #  
        stages = ['', '', '', '']
        stories = []
        for i, stage in enumerate(stages):
            stories.append({
                'stage': stage,
                'stage_name': f"{stage} -  {i+1}",
                'content': f"AI  {stage}  .",
                'order': i
            })
        return stories
    
    def _generate_scenes_from_response(self, response: str) -> List[Dict]:
        """  """
        #  
        scenes = []
        for story_idx in range(4):
            for scene_idx in range(3):
                scenes.append({
                    'story_index': story_idx,
                    'scene_number': scene_idx + 1,
                    'title': f" {story_idx * 3 + scene_idx + 1}",
                    'description': f"AI   .",
                    'duration': '30'
                })
        return scenes
    
    def _get_dummy_suggestions(self, data: Dict) -> Dict:
        """  """
        project_type = data.get('project_type', 'youtube')
        
        suggestions = {
            'youtube': {
                'structure': '(15) →  (30) →  (2) →  (3) → (30)',
                'keywords': ['', ' ', ' ', '', ''],
                'tips': '       ,        .'
            },
            'corporate': {
                'structure': ' (30) →  (1) →  (1) →  (30)',
                'keywords': ['', '', '', '', ''],
                'tips': '       .'
            },
            'advertisement': {
                'structure': ' (5) →  (10) →   (10) →  (5)',
                'keywords': ['', '', '', '', ''],
                'tips': ' 3          .'
            },
            'documentary': {
                'structure': ' (1) →  (3) →  (4) → (2)',
                'keywords': ['', '', '', '', ''],
                'tips': '        .'
            }
        }
        
        return suggestions.get(project_type, suggestions['youtube'])
    
    def _get_dummy_full_planning(self, data: Dict) -> Dict:
        """   """
        project_type = data.get('projectType', 'youtube')
        main_topic = data.get('mainTopic', '')
        
        #  
        planning_text = f"""
        [{main_topic}]  
        
        : {data.get('targetAudience', '')}
        : {data.get('duration', '5')}
        : {data.get('desiredMood', '')}
        
         : {data.get('keyMessage', '  ')}
        
          {main_topic}  {data.get('targetAudience', '')} 
             .
        """
        
        #  
        stories = [
            {
                'stage': '',
                'stage_name': '',
                'content': f"{main_topic}        .      .",
                'order': 0
            },
            {
                'stage': '',
                'stage_name': '',
                'content': f"{main_topic}     .        .",
                'order': 1
            },
            {
                'stage': '',
                'stage_name': '',
                'content': f"{main_topic}    .        .",
                'order': 2
            },
            {
                'stage': '',
                'stage_name': '',
                'content': f"   {main_topic}  .        .",
                'order': 3
            }
        ]
        
        #   3  
        scenes = []
        for story_idx, story in enumerate(stories):
            for scene_idx in range(3):
                scene_num = story_idx * 3 + scene_idx + 1
                scenes.append({
                    'story_index': story_idx,
                    'scene_number': scene_idx + 1,
                    'title': f"{story['stage']} -  {scene_idx + 1}",
                    'description': f"{story['stage']}  {scene_idx + 1} . {story['content'][:50]}...",
                    'duration': '20-30',
                    'camera_notes': data.get('cameraMovement', 'static') if data.get('enableProOptions') else None,
                    'color_tone': data.get('colorTone', 'natural') if data.get('enableProOptions') else None
                })
        
        return {
            'id': None,
            'title': f"[AI ] {main_topic} - {project_type}  ",
            'planning': planning_text,
            'stories': stories,
            'scenes': scenes,
            'shots': [],  #   
            'storyboards': [],  #   
            'pro_options': {
                'colorTone': data.get('colorTone'),
                'aspectRatio': data.get('aspectRatio'),
                'cameraType': data.get('cameraType'),
                'lensType': data.get('lensType'),
                'cameraMovement': data.get('cameraMovement')
            } if data.get('enableProOptions') else None
        }

# VEO3    
class VEO3PromptGenerator:
    """VEO3     """
    
    def generate_video_prompt(self, scene_data: Dict, pro_options: Dict = None) -> str:
        """  VEO3    """
        
        base_prompt = f"{scene_data.get('description', '')}"
        
        if pro_options:
            #      
            technical_details = []
            
            if pro_options.get('colorTone'):
                color_mapping = {
                    'natural': 'natural lighting',
                    'warm': 'warm color grading',
                    'cool': 'cool blue tones',
                    'cinematic': 'cinematic color grading',
                    'vibrant': 'vibrant saturated colors'
                }
                technical_details.append(color_mapping.get(pro_options['colorTone'], ''))
            
            if pro_options.get('cameraType'):
                camera_mapping = {
                    'dslr': 'shot with DSLR camera',
                    'cinema': 'shot with cinema camera, shallow depth of field',
                    'smartphone': 'shot with smartphone',
                    'drone': 'aerial drone footage'
                }
                technical_details.append(camera_mapping.get(pro_options['cameraType'], ''))
            
            if pro_options.get('lensType'):
                lens_mapping = {
                    '24mm': '24mm wide angle lens',
                    '35mm': '35mm lens',
                    '50mm': '50mm standard lens',
                    '85mm': '85mm portrait lens, bokeh',
                    'zoom': 'zoom lens'
                }
                technical_details.append(lens_mapping.get(pro_options['lensType'], ''))
            
            if pro_options.get('cameraMovement'):
                movement_mapping = {
                    'static': 'static shot',
                    'pan': 'smooth panning movement',
                    'tilt': 'tilting camera movement',
                    'dolly': 'dolly camera movement',
                    'handheld': 'handheld camera movement'
                }
                technical_details.append(movement_mapping.get(pro_options['cameraMovement'], ''))
            
            if technical_details:
                base_prompt += f", {', '.join(filter(None, technical_details))}"
        
        return base_prompt
    
    def generate_image_prompt(self, scene_data: Dict, pro_options: Dict = None) -> str:
        """      """
        
        base_prompt = f"cinematic still frame, {scene_data.get('description', '')}"
        
        if pro_options:
            #    
            if pro_options.get('aspectRatio'):
                base_prompt += f", aspect ratio {pro_options['aspectRatio']}"
            
            if pro_options.get('colorTone'):
                base_prompt += f", {pro_options['colorTone']} color grading"
        
        #   
        base_prompt += ", highly detailed, professional photography, 8k resolution"
        
        return base_prompt