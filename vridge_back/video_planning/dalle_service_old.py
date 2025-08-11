import os
import logging
import requests
import base64
from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)


class DalleService:
    """
    OpenAI DALL-E 3    
    """
    
    def __init__(self):
        #    
        settings_key = getattr(settings, 'OPENAI_API_KEY', None)
        env_key = os.environ.get('OPENAI_API_KEY')
        
        logger.info(f" OPENAI_API_KEY :")
        logger.info(f"  - settings.OPENAI_API_KEY: {settings_key[:10] + '...' if settings_key else 'None'}")
        logger.info(f"  - os.environ.get('OPENAI_API_KEY'): {env_key[:10] + '...' if env_key else 'None'}")
        
        self.api_key = settings_key or env_key
        self.available = bool(self.api_key)
        
        if not self.available:
            logger.warning(" OPENAI_API_KEY not found. DALL-E image generation will not be available.")
            logger.warning("  - Railway   ")
            logger.warning("  -    ")
        else:
            logger.info(f" DALL-E service initialized with API key: {self.api_key[:10]}...")
            try:
                # OpenAI   -   
                import openai
                #  
                openai_version = getattr(openai, '__version__', '0.0.0')
                logger.info(f"OpenAI library version: {openai_version}")
                
                #  
                self.client = OpenAI(api_key=self.api_key)
                self.available = True
                logger.info("OpenAI client initialized successfully")
            except TypeError as e:
                # Railway  proxies  -  
                logger.warning(f"TypeError during client init: {e}")
                try:
                    #    
                    os.environ['OPENAI_API_KEY'] = self.api_key
                    from openai import OpenAI
                    self.client = OpenAI()
                    self.available = True
                    logger.info("OpenAI client initialized via environment variable")
                except Exception as env_e:
                    logger.error(f"Failed to initialize with env var: {env_e}")
                    self.available = False
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.available = False
    
    def generate_storyboard_image(self, frame_data, style='minimal'):
        """
             .
        
        Args:
            frame_data:  
            style:   ('minimal', 'realistic', 'sketch', 'cartoon', 'cinematic')
        """
        if not self.available:
            return {
                "success": False,
                "error": "     . OPENAI_API_KEY .",
                "image_url": None
            }
        
        try:
            prompt = self._create_storyboard_prompt(frame_data, style)
            
            logger.info(f"Generating image with DALL-E 3, prompt: {prompt[:100]}...")
            
            # OpenAI 1.3.7  client    
            if not hasattr(self, 'client') or self.client is None:
                #   
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=self.api_key)
                except Exception as e:
                    logger.error(f"Failed to reinitialize client: {e}")
                    raise Exception("OpenAI   ")
            
            # DALL-E 3 API  -  
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",  # 16:9 
                quality="standard", #   (  )
                n=1,
                style="vivid"      #     
            )
            image_url = response.data[0].url
            
            # URL   base64 
            image_response = requests.get(image_url, timeout=30)
            if image_response.status_code == 200:
                image_base64 = base64.b64encode(image_response.content).decode('utf-8')
                final_image_url = f"data:image/png;base64,{image_base64}"
                
                logger.info("Successfully generated image with DALL-E 3")
                return {
                    "success": True,
                    "image_url": final_image_url,
                    "prompt_used": prompt,
                    "model_used": "dall-e-3",
                    "original_url": image_url  #  URL 
                }
            else:
                raise Exception(f"Failed to download image from {image_url}")
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"DALL-E image generation failed: {error_msg}")
            
            # API    
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                error_msg = "OpenAI API   ."
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                error_msg = "OpenAI API   ."
            
            return {
                "success": False,
                "error": error_msg,
                "image_url": None
            }
    
    def _filter_forbidden_words(self, text):
        """
                 .
        """
        forbidden_words = [
            'storyboard', 'frame', 'scene description', 'scene',
            'text box', 'textbox', 'caption', 'label',
            'write', 'written', 'explained', 'annotated',
            'comic panel with narration', 'comic panel',
            'diagram', 'layout', 'template',
            'slide', 'presentation', 'whiteboard',
            'panel', 'box', 'description', 'narration',
            'subtitle', 'title card', 'text overlay',
            'document', 'paper', 'poster', 'sign',
            'Frame #', 'Scene:', 'frame number', 'shot number',
            '', '', '', ''
        ]
        
        #    
        filtered_text = text
        for word in forbidden_words:
            import re
            #       
            pattern = r'\b' + re.escape(word) + r'\b'
            filtered_text = re.sub(pattern, '', filtered_text, flags=re.IGNORECASE)
        
        #   
        filtered_text = ' '.join(filtered_text.split())
        
        return filtered_text
    
    def _create_storyboard_prompt(self, frame_data, style='minimal'):
        """
           DALL-E  .
        Midjourney     .
        
        Args:
            frame_data:  
            style:   ('minimal', 'realistic', 'sketch', 'cartoon', 'cinematic')
        """
        visual_desc = frame_data.get('visual_description', '')
        composition = frame_data.get('composition', '')
        lighting = frame_data.get('lighting', '')
        #     -    
        
        #        
        scene_translations = {
            # /
            '': 'interior space with visible walls and ceiling',
            '': 'outdoor environment with open sky',
            '': 'modern office interior with desks and computers',
            '': 'urban street with buildings on both sides',
            '': 'cozy home interior with furniture',
            '': 'coffee shop interior with tables and warm lighting',
            '': 'park with trees and benches',
            '': 'school classroom with desks and blackboard',
            '': 'hospital corridor with clean white walls',
            '': 'conference room with large table and chairs',
            '': 'bedroom with bed and window',
            '': 'living room with sofa and TV',
            '': 'kitchen with cabinets and appliances',
            '': 'road with cars and traffic',
            '': 'tall buildings and urban skyline',
            '': 'forest with tall trees and natural lighting',
            '': 'ocean view with waves and horizon',
            '': 'mountain landscape with peaks',
            '': 'sky with clouds',
            '': 'cityscape with buildings and streets',
            
            #   -   
            '': 'man',
            '': 'woman',
            '': 'child',
            '': 'elderly person',
            '': 'young person',
            '': 'middle-aged person',
            '': 'boy',
            '': 'girl',
            '': 'person',
            '': 'woman',
            '': 'man',
            '': 'father figure',
            '': 'mother figure',
            '': 'student',
            '': 'teacher',
            '': 'doctor in white coat',
            '': 'nurse',
            '': 'office worker',
            '20': 'young adult',
            '30': 'person in thirties',
            '40': 'middle-aged person',
            '50': 'mature person',
            
            # /
            '': 'walking with natural stride',
            '': 'sitting on chair with relaxed posture',
            '': 'standing upright',
            '': 'running with dynamic motion',
            '': 'speaking with expressive gestures',
            '': 'listening attentively',
            '': 'looking intently at something',
            '': 'smiling with warm expression',
            '': 'crying with emotional expression',
            '': 'deep in thought with hand on chin',
            '': 'writing at desk',
            '': 'reading book or document',
            '': 'eating at table',
            '': 'drinking from cup',
            '': 'working at desk with focused expression',
            '': 'playing with joyful expression',
            '': 'sleeping peacefully',
            '': 'driving car with hands on wheel'
        }
        
        # /   -   
        camera_angles = {
            '': 'extremely wide landscape view',
            '': 'person framed from waist up',
            '': 'tight shot on face filling frame',
            '': 'view over someone shoulder',
            '': 'camera high above looking down',
            '': 'camera near ground looking up',
            ' ': 'macro shot of eyes only',
            '': 'full figure head to toe',
            '': 'two people together in frame'
        }
        
        #    -   
        lighting_styles = {
            '': 'bright sunny daylight',
            ' ': 'soft even lighting no shadows',
            ' ': 'stark light and shadow contrast',
            '': 'strong backlight silhouette',
            '': 'warm orange sunset glow',
            '': 'dark night blue hour lighting',
            '': 'cozy warm indoor lamps'
        }
        
        #   
        translated_desc = visual_desc
        for korean, english in scene_translations.items():
            if korean in visual_desc:
                translated_desc = translated_desc.replace(korean, english)
        
        #    - /   
        style_prompts = {
            'minimal': {
                'base': "minimalist pencil sketch",
                'details': [
                    "simple clean lines",
                    "minimal detail",
                    "black and white",
                    "16:9 cinematic composition"
                ]
            },
            'realistic': {
                'base': "photorealistic cinematic shot",
                'details': [
                    "cinematic lighting",
                    "shallow depth of field",
                    "film grain",
                    "16:9 aspect ratio"
                ]
            },
            'sketch': {
                'base': "black-and-white pencil sketch",
                'details': [
                    "hand-drawn style",
                    "soft shading",
                    "artistic composition",
                    "cinematic angle"
                ]
            },
            'cartoon': {
                'base': "Vibrant cartoon artwork",
                'details': [
                    "bright cartoon colors",
                    "thick black outlines",
                    "cel-shaded style",
                    "animated character design"
                ]
            },
            'cinematic': {
                'base': "Dramatic cinematic shot",
                'details': [
                    "film noir atmosphere",
                    "chiaroscuro lighting",
                    "wide aspect ratio",
                    "movie still quality"
                ]
            },
            'watercolor': {
                'base': "Soft watercolor painting",
                'details': [
                    "watercolor paint on paper",
                    "wet-on-wet technique",
                    "flowing paint bleeds",
                    "transparent color layers"
                ]
            },
            'digital': {
                'base': "Digital artwork rendering",
                'details': [
                    "glossy digital painting",
                    "vibrant neon colors",
                    "smooth gradients",
                    "futuristic aesthetic"
                ]
            },
            'noir': {
                'base': "Black and white film noir",
                'details': [
                    "high contrast monochrome",
                    "deep shadows",
                    "1940s noir style",
                    "venetian blind shadows"
                ]
            },
            'pastel': {
                'base': "Soft pastel artwork",
                'details': [
                    "chalk pastel on paper",
                    "muted pastel tones",
                    "soft edges",
                    "dreamy soft focus"
                ]
            },
            'comic': {
                'base': "Comic book artwork",
                'details': [
                    "comic book art",
                    "dynamic action shot",
                    "ben day dots",
                    "vibrant pop art colors"
                ]
            }
        }
        
        #    (: sketch)
        selected_style = style_prompts.get(style, style_prompts['sketch'])
        
        # Midjourney    
        prompt_parts = []
        
        # 1.   
        prompt_parts.append(selected_style['base'])
        
        # 2.   ()
        if translated_desc:
            #   
            clean_desc = translated_desc
            clean_desc = clean_desc.replace('around ', '')
            clean_desc = clean_desc.replace(' years old', '')
            clean_desc = clean_desc.replace('standing ', '')
            clean_desc = clean_desc.replace('sitting ', '')
            #    
            prompt_parts.append(clean_desc.strip())
        
        # 3.   (shot )
        if composition in camera_angles:
            angle = camera_angles[composition]
            angle = angle.replace(' shot', '').replace('camera ', '').replace(' view', '')
            if angle and angle not in prompt_parts[0]:  #  
                prompt_parts.append(angle)
        
        # 4.  ()
        if lighting in lighting_styles:
            light = lighting_styles[lighting]
            if 'lighting' not in light:  # lighting   
                light = light.replace('bright ', '').replace('dark ', '')
            prompt_parts.append(light)
        
        # 5.   ()
        for detail in selected_style['details'][:2]:  #  2
            if detail not in ' '.join(prompt_parts):  #  
                prompt_parts.append(detail)
        
        #   - Midjourney   
        prompt = ', '.join(filter(None, prompt_parts))
        
        #     ( )
        prompt = self._filter_forbidden_words(prompt)
        
        #   - Frame #1    
        import re
        prompt = re.sub(r'Frame\s*#?\d*', '', prompt, flags=re.IGNORECASE)
        prompt = re.sub(r'Scene\s*:?\s*\d*', '', prompt, flags=re.IGNORECASE)
        prompt = re.sub(r'Shot\s*#?\d*', '', prompt, flags=re.IGNORECASE)
        prompt = re.sub(r'\b\d+\s*(frame|scene|shot)\b', '', prompt, flags=re.IGNORECASE)
        
        #  / 
        prompt = re.sub(r'\s+', ' ', prompt)
        prompt = re.sub(r',\s*,', ',', prompt)
        prompt = prompt.strip(' ,')
        
        logger.info(f"Cleaned DALL-E prompt: {prompt}")
        return prompt