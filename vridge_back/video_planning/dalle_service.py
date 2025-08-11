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
        self.client = None
        
        if not self.api_key:
            logger.warning(" OPENAI_API_KEY not found. DALL-E image generation will not be available.")
            logger.warning("  - Railway   ")
            logger.warning("  -    ")
            self.available = False
        else:
            logger.info(f" API Key found: {self.api_key[:10]}...")
            try:
                # OpenAI   -   
                try:
                    #  1:  API  
                    self.client = OpenAI(api_key=self.api_key)
                    logger.info(" Method 1: OpenAI client initialized with direct API key")
                except Exception as e1:
                    logger.warning(f" Method 1 failed (proxy issue?): {e1}")
                    
                    try:
                        #  2:     (  )
                        os.environ['OPENAI_API_KEY'] = self.api_key
                        #    
                        for proxy_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
                            if proxy_var in os.environ:
                                logger.info(f"Removing proxy env var: {proxy_var}")
                                del os.environ[proxy_var]
                        
                        self.client = OpenAI()
                        logger.info(" Method 2: OpenAI client initialized via environment variable")
                    except Exception as e2:
                        logger.error(f" Method 2 failed: {e2}")
                        
                        try:
                            #  3:   
                            import httpx
                            self.client = OpenAI(
                                api_key=self.api_key,
                                http_client=httpx.Client()
                            )
                            logger.info(" Method 3: OpenAI client initialized with custom HTTP client")
                        except Exception as e3:
                            logger.error(f" Method 3 failed: {e3}")
                            raise e3
                
                #      
                if self.client:
                    self.available = True
                    logger.info(" DALL-E service ready for image generation")
                else:
                    self.available = False
                
            except Exception as e:
                logger.error(f" Failed to initialize OpenAI client: {e}")
                self.available = False
                self.client = None
    
    def generate_storyboard_image(self, frame_data, style='minimal', draft_mode=True):
        """
             .
        
        Args:
            frame_data:  
            style:   ('minimal', 'realistic', 'sketch', 'cartoon', 'cinematic')
            draft_mode: True      ( )
        """
        # API    available   
        if not self.api_key:
            return {
                "success": False,
                "error": "OPENAI_API_KEY  .",
                "image_url": None
            }
        
        if not self.client:
            #   
            try:
                logger.info("Attempting to reinitialize OpenAI client...")
                self.client = OpenAI(api_key=self.api_key)
                logger.info(" OpenAI client reinitialized successfully")
            except Exception as e:
                logger.error(f" Failed to reinitialize client: {e}")
                return {
                    "success": False,
                    "error": f"OpenAI   : {str(e)}",
                    "image_url": None
                }
        
        try:
            # draft     
            if draft_mode:
                style = 'sketch'
            
            prompt = self._create_visual_prompt(frame_data, style, draft_mode=draft_mode)
            
            logger.info(f"Generating image with DALL-E 3 (draft_mode={draft_mode}), prompt: {prompt[:100]}...")
            
            # OpenAI 1.3.7  client    
            if not hasattr(self, 'client') or self.client is None:
                #   
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=self.api_key)
                except Exception as e:
                    logger.error(f"Failed to reinitialize client: {e}")
                    raise Exception("OpenAI   ")
            
            # draft_mode   
            if draft_mode:
                #    draft  
                image_size = "1024x1024"    #  (  )
                image_quality = "standard"   #  
                image_style = "natural"      #   ( )
            else:
                #   
                image_size = "1792x1024"    # 16:9 
                image_quality = "hd"         # HD 
                image_style = "vivid"        #     
            
            # DALL-E 3 API 
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=image_size,
                quality=image_quality,
                n=1,
                style=image_style
            )
            image_url = response.data[0].url
            
            # URL   base64  ( )
            image_response = requests.get(image_url, timeout=60)
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
    
    def _create_visual_prompt(self, frame_data, style='minimal', draft_mode=False):
        """
           DALL-E 3    .
        
        Args:
            frame_data:  
            style:  
            draft_mode: True     
        """
        visual_desc = frame_data.get('visual_description', '')
        
        # visual_description      
        if self._is_english(visual_desc):
            #     
            base_prompt = visual_desc
        else:
            #   
            base_prompt = self._translate_korean_to_english(visual_desc)
        
        #    ( )
        composition = frame_data.get('composition', '')
        if composition and not any(term in base_prompt.lower() for term in ['wide shot', 'close-up', 'medium shot']):
            #    
            comp_map = {
                '': 'wide shot',
                '': 'close-up',
                '': 'medium shot',
                '': 'full shot',
                '': 'over-the-shoulder shot'
            }
            for kr, en in comp_map.items():
                if kr in composition:
                    base_prompt = f"{en} of {base_prompt}"
                    break
        
        #  
        if draft_mode:
            # draft    
            style_prompts = {
                'sketch': 'simple rough pencil sketch, quick draft drawing',
                'minimal': 'very simple line drawing, minimal details',
                'default': 'rough sketch, draft storyboard'
            }
        else:
            #    
            style_prompts = {
                'minimal': 'minimalist pencil sketch',
                'sketch': 'detailed pencil sketch',
                'realistic': 'photorealistic',
                'watercolor': 'watercolor painting',
                'cinematic': 'cinematic dramatic lighting',
                'black-and-white': 'black and white photograph',
                'oil-painting': 'oil painting',
                'digital-art': 'digital art illustration'
            }
        
        style_prefix = style_prompts.get(style, style_prompts.get('default', 'cinematic'))
        prompt = f"{style_prefix}, {base_prompt}"
        
        #   (   )
        lighting = frame_data.get('lighting', '')
        if lighting and '' not in prompt:
            lighting_trans = self._translate_lighting(lighting)
            if lighting_trans and lighting_trans != lighting:
                prompt += f", {lighting_trans}"
        
        #   
        prompt += ", no text, no words, no letters, without any text"
        
        #    
        prompt = self._remove_forbidden_words(prompt)
        
        #  
        prompt = ' '.join(prompt.split())
        
        logger.info(f"Final DALL-E prompt: {prompt}")
        return prompt
    
    def _is_english(self, text):
        """   """
        #   
        if not text:
            return False
        alpha_count = sum(1 for c in text if c.isalpha() and ord(c) < 128)
        total_alpha = sum(1 for c in text if c.isalpha())
        return total_alpha > 0 and alpha_count / total_alpha > 0.8
    
    def _translate_korean_to_english(self, text):
        """
            .
        """
        #     
        text = self._clean_text_triggers(text)
        
        #        
        korean_char_count = sum(1 for char in text if '\uac00' <= char <= '\ud7a3')
        total_char_count = len(text.replace(' ', ''))
        
        if total_char_count > 0 and korean_char_count / total_char_count > 0.5:
            #  50%      
            logger.info(f"Korean text detected ({korean_char_count}/{total_char_count}), using enhanced scene description")
            logger.info(f"Original Korean text: {text}")
            
            #      
            result = None
            
            # /  
            if '' in text or '' in text or '' in text:
                if '' in text and '' in text:
                    result = "elderly female shaman in colorful traditional Korean dress holding hands with worried middle-aged woman client, sitting on floor cushions in dimly lit shrine room filled with hanging paper talismans and burning incense"
                elif '' in text:
                    result = "shaman in vibrant hanbok and client sitting face to face on traditional floor cushions in mystical shrine interior, candlelight flickering on walls covered with spiritual paintings and talismans"
                elif '' in text or '' in text:
                    result = "atmospheric shaman shrine interior with burning incense creating smoke patterns, multiple candles casting warm light on wooden walls decorated with colorful spiritual paintings and paper charms"
                else:
                    result = "traditional Korean shaman shrine interior with elderly female shaman in ceremonial dress, wooden walls covered in talismans, altar with offerings, incense smoke drifting through dim candlelit space"
            
            #   
            elif '' in text:
                if '' in text or '' in text:
                    result = "man in casual business attire pushing glass door to enter modern coffee shop, warm interior lights visible through windows, other customers visible inside"
                elif '' in text:
                    result = "people sitting at wooden table in cozy coffee shop, laptops open, coffee cups steaming, large windows showing street view, warm ambient lighting"
                else:
                    result = "bustling modern coffee shop interior with customers at various tables, barista behind counter, exposed brick walls, industrial lighting, plants by windows"
            
            #   
            elif '' in text:
                if '' in text:
                    result = "professional woman in business suit presenting to seated colleagues in modern conference room, projector screen showing charts, city view through floor-to-ceiling windows"
                else:
                    result = "group of business professionals around polished conference table in modern meeting room, laptops open, large monitor on wall, minimalist decor"
            
            #   
            elif '' in text:
                if '' in text or '' in text:
                    result = "children playing on colorful playground equipment in sunny park, parents watching from benches, trees providing shade, blue sky with fluffy clouds"
                else:
                    result = "peaceful urban park with walking paths, green grass, mature trees, people strolling, benches along pathways, city buildings visible in distance"
            
            #   
            elif '' in text:
                result = "modern open office space with rows of desks, computer monitors, employees working, glass partition walls, fluorescent lighting, potted plants"
            
            #  
            elif '' in text and ('' in text or '' in text):
                result = "extreme close-up of two people's hands clasped together showing emotional connection, soft natural lighting, blurred background"
            elif '' in text or '' in text:
                if '' in text:
                    result = "close-up portrait of person with serious thoughtful expression, eyes focused, natural window light on face, shallow depth of field"
                else:
                    result = "close-up of person's face showing genuine emotion, natural lighting, detailed facial features visible, blurred background"
            elif '' in text:
                result = "detailed close-up shot showing texture and detail, shallow depth of field, professional lighting"
            elif '' in text:
                result = "expansive wide shot showing full interior space with architectural details, people as small figures in larger environment"
            else:
                #    ( )
                result = "well-lit interior space with people engaged in activity, modern furnishings, natural light from windows, comfortable atmosphere"
            
            logger.info(f"Enhanced Korean to English result: {result}")
            return result
        
        #     ( !)
        translations = [
            #   (  )
            ('  ', 'people working in office'),
            ('  ', 'man walks into cafe'),
            ('  ', 'woman giving presentation in meeting room'),
            ('  ', 'children running in park playground'),
            ('  ', 'man walking'),
            (' ', 'presentation in meeting room'),
            ('  ', 'children running in park'),
            ('  ', 'cafe entrance'),
            (' ', 'cafe entrance'),
            (' ', 'working in office'),
            (' ', 'entering cafe'),
            (' ', 'presenting in meeting room'),
            (' ', 'playing in park'),
            
            # 
            ('', 'shaman shrine'),
            ('', 'shaman house'),
            ('', 'ward'),
            ('', 'cafe'),
            ('', 'coffee shop'),
            ('', 'meeting room'),
            ('', 'park'),
            ('', 'office'),
            ('', 'street'),
            ('', 'road'),
            ('', 'home'),
            ('', 'school'),
            ('', 'hospital'),
            ('', 'shop'),
            ('', 'restaurant'),
            ('', 'window'),
            ('', 'door'),
            ('', 'wall'),
            ('', 'floor'),
            ('', 'ceiling'),
            
            # 
            ('', 'young woman'),
            ('', 'middle aged woman'),
            ('', 'white cat'),
            ('', 'shaman'),
            ('', 'children'),
            ('', 'man'),
            ('', 'woman'),
            ('', 'woman'),
            ('', 'man'),
            ('', 'child'),
            ('', 'person'),
            ('', 'people'),
            ('', 'client'),
            ('', 'customer'),
            
            # 
            ('', 'sitting'),
            ('', 'sitting'),
            ('', 'entering'),
            ('', 'exiting'),
            ('', 'walking'),
            ('', 'running'),
            ('', 'sitting'),
            ('', 'standing'),
            ('', 'speaking'),
            ('', 'listening'),
            ('', 'smiling'),
            ('', 'working'),
            ('', 'playing'),
            ('', 'playing'),
            ('', 'walking'),
            ('', 'presentation'),
            ('', 'holding'),
            ('', 'holding'),
            ('', 'shining'),
            ('', 'hanging'),
            (' ', 'listening'),
            
            #  
            ('', 'interior'),
            ('', 'sunlight'),
            ('', 'near'),
            ('', 'front'),
            ('', 'beside'),
            ('', 'quietly'),
            ('', 'neat'),
            ('', 'cozy'),
            ('', 'atmosphere'),
            ('', 'talisman'),
            ('', 'painting'),
            ('', 'expression'),
            ('', 'serious'),
            ('', 'gentle'),
            ('', 'close up'),
            
            #  ( )
            ('', ' in '),
            ('', ' at '),
            ('', ''),
            ('', ''),
            ('', ''),
            ('', ''),
            ('', ''),
            ('', ''),
            ('', '')
        ]
        
        result = text
        #   (    )
        for korean, english in translations:
            result = result.replace(korean, english)
        
        #   
        result = ' '.join(result.split())
        
        return result
    
    def _clean_text_triggers(self, text):
        """
         /    .
        """
        import re
        
        #  (:)    
        if ':' in text:
            #    
            parts = text.split(':', 1)
            if len(parts) > 1:
                text = parts[1].strip()
        
        #  
        patterns_to_remove = [
            r'\s*#?\s*\d*',
            r'Frame\s*#?\s*\d*',
            r'\s*\d*',
            r'Scene\s*\d*',
            r'\s*',
            r'Scene\s*description',
            r'\s*\d*',
            r'\s*\d*',
            r'Cut\s*\d*',
            r'\s*\d*',
            r'Shot\s*\d*',
            r'\s*:',
            r'description\s*:',
            r'^\d+\.\s*',  #   
            r'^\-\s*',     #   
            r'^\*\s*',     #   
            r'#\d+',       # #1, #2 
        ]
        
        cleaned_text = text
        for pattern in patterns_to_remove:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        #   
        cleaned_text = ' '.join(cleaned_text.split())
        
        return cleaned_text.strip()
    
    def _translate_composition(self, composition):
        """
           
        """
        comp_dict = {
            '': 'closeup',
            '': 'medium',
            '': 'wide',
            '': 'full',
            '': 'long',
            '': 'aerial',
            '': 'low angle',
            '': 'high angle'
        }
        return comp_dict.get(composition, composition)
    
    def _translate_lighting(self, lighting):
        """
           
        """
        light_dict = {
            '': 'natural light',
            '': 'indoor lighting',
            '': 'golden hour',
            '': 'backlight',
            '': 'soft light',
            '': 'harsh light',
            '': 'dark',
            '': 'bright'
        }
        return light_dict.get(lighting, lighting)
    
    def _remove_forbidden_words(self, prompt):
        """
             .
        """
        forbidden_patterns = [
            r'frame\s*#?\s*\d*',
            r'scene\s*:?\s*\d*',
            r'shot\s*#?\s*\d*',
            r'storyboard',
            r'description',
            r'text\s*box',
            r'caption',
            r'label',
            r'written',
            r'explained',
            r'annotated',
            r'panel',
            r'slide',
            r'script',
            r'title',
            r'heading',
            r'',
            r'',
            r'',
            r'',
            r''
        ]
        
        result = prompt
        for pattern in forbidden_patterns:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        
        #    
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r',\s*,', ',', result)
        result = result.strip(' ,')
        
        return result