import os
import logging
import requests
import base64
from django.conf import settings
from openai import OpenAI
import re

logger = logging.getLogger(__name__)


class DalleService:
    """
    OpenAI DALL-E 3     -  
    """
    
    def __init__(self):
        # API  
        settings_key = getattr(settings, 'OPENAI_API_KEY', None)
        env_key = os.environ.get('OPENAI_API_KEY')
        
        self.api_key = settings_key or env_key
        self.available = bool(self.api_key)
        
        if not self.available:
            logger.warning(" OPENAI_API_KEY not found.")
        else:
            logger.info(f" DALL-E service initialized")
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.available = True
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.available = False
    
    def generate_storyboard_image(self, frame_data, style='minimal'):
        """
          .
        """
        if not self.available:
            return {
                "success": False,
                "error": "OPENAI_API_KEY not configured",
                "image_url": None
            }
        
        try:
            # 3    
            prompts = self._create_multiple_prompts(frame_data, style)
            
            #    
            for i, prompt in enumerate(prompts):
                logger.info(f"Attempt {i+1} with prompt: {prompt}")
                
                try:
                    response = self.client.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        size="1792x1024",
                        quality="standard",
                        n=1,
                        style="vivid"
                    )
                    
                    image_url = response.data[0].url
                    
                    #    base64 
                    image_response = requests.get(image_url, timeout=30)
                    if image_response.status_code == 200:
                        image_base64 = base64.b64encode(image_response.content).decode('utf-8')
                        return {
                            "success": True,
                            "image_url": f"data:image/png;base64,{image_base64}",
                            "prompt_used": prompt,
                            "model_used": "dall-e-3",
                            "attempt": i+1
                        }
                except Exception as e:
                    logger.warning(f"Attempt {i+1} failed: {e}")
                    continue
            
            raise Exception("All prompt attempts failed")
                
        except Exception as e:
            logger.error(f"DALL-E generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "image_url": None
            }
    
    def _create_multiple_prompts(self, frame_data, style='minimal'):
        """
           .
        """
        visual_desc = frame_data.get('visual_description', '')
        
        #   
        eng_desc = self._translate_korean(visual_desc)
        
        # 3   
        prompts = []
        
        # 1.   
        if style == 'minimal':
            prompts.append(f"minimalist pencil sketch: {eng_desc}")
        elif style == 'sketch':
            prompts.append(f"pencil drawing: {eng_desc}")
        elif style == 'realistic':
            prompts.append(f"photorealistic: {eng_desc}")
        else:
            prompts.append(f"{style}: {eng_desc}")
        
        # 2.   
        composition = frame_data.get('composition', '')
        if composition:
            comp_eng = self._get_composition(composition)
            prompts.append(f"{prompts[0]}, {comp_eng}")
        
        # 3.   (  )
        artistic_prompt = self._create_artistic_prompt(eng_desc, style)
        prompts.append(artistic_prompt)
        
        return prompts
    
    def _translate_korean(self, text):
        """
           
        """
        #   
        full_translations = {
            '  ': 'man walking through café entrance',
            '  ': 'businesswoman giving presentation in meeting room',
            '  ': 'children running and playing in sunny park',
            '  ': 'people working at office desks',
            '  ': 'person walking down city street'
        }
        
        #    
        if text in full_translations:
            return full_translations[text]
        
        #  
        result = text
        translations = {
            '': 'café',
            '': 'meeting room',
            '': 'park',
            '': 'office',
            '': 'street',
            '': 'man',
            '': 'woman',
            '': 'woman',
            '': 'children',
            '': 'person',
            '': 'entering',
            '': 'presenting',
            '': 'playing',
            '': 'walking',
            '': 'working',
            '': ' in ',
            '': ' at ',
            '': '',
            '': '',
            '': '',
            '': '',
            '': ''
        }
        
        for kor, eng in translations.items():
            result = result.replace(kor, eng)
        
        return ' '.join(result.split())
    
    def _get_composition(self, korean_comp):
        """
           
        """
        compositions = {
            '': 'wide shot',
            '': 'medium shot',
            '': 'close up',
            '': 'full shot'
        }
        return compositions.get(korean_comp, '')
    
    def _create_artistic_prompt(self, description, style):
        """
           (   )
        """
        style_templates = {
            'minimal': f"simple line art showing {description}",
            'sketch': f"artistic pencil sketch of {description}",
            'realistic': f"photographic image of {description}",
            'watercolor': f"watercolor painting depicting {description}",
            'cinematic': f"movie still showing {description}"
        }
        
        return style_templates.get(style, f"illustration of {description}")
    
    def _remove_forbidden_words(self, prompt):
        """
          
        """
        #  
        forbidden = [
            r'\bframe\b', r'\bscene\b', r'\bstoryboard\b',
            r'\btext\b', r'\bcaption\b', r'\blabel\b',
            r'\bpanel\b', r'\bdescription\b', r'#\d+'
        ]
        
        result = prompt
        for pattern in forbidden:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        
        # 
        result = ' '.join(result.split())
        return result