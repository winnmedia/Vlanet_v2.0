import os
import json
import google.generativeai as genai
from django.conf import settings
import logging
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

#  LLM    - Gemini 

#    import
try:
    from .dalle_service import DalleService
    IMAGE_SERVICE_AVAILABLE = True
except ImportError:
    logger.warning("DALL-E service not available")
    DalleService = None
    IMAGE_SERVICE_AVAILABLE = False

#   
try:
    from .placeholder_image_service import PlaceholderImageService
    PLACEHOLDER_SERVICE_AVAILABLE = True
except ImportError:
    logger.warning("Placeholder image service not available")
    PlaceholderImageService = None
    PLACEHOLDER_SERVICE_AVAILABLE = False


class GeminiService:
    def __init__(self):
        api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in settings or environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.pro_model = genai.GenerativeModel('gemini-1.5-pro')  # PDF  Pro 
        
        #   
        self.token_usage = {
            'total': 0,
            'prompt': 0,
            'response': 0,
            'by_feature': {
                'story': {'prompt': 0, 'response': 0, 'total': 0},
                'scene': {'prompt': 0, 'response': 0, 'total': 0},
                'shot': {'prompt': 0, 'response': 0, 'total': 0},
                'storyboard': {'prompt': 0, 'response': 0, 'total': 0}
            }
        }
        
        #  LLM   - Gemini 
        self.exaone_service = None
        self.hf_exaone_service = None
        self.friendli_service = None
        logger.info("[GeminiService] Using Gemini for all text generation")
        
        #     ()
        self.image_service_available = False
        self.image_service = None
        self.placeholder_service = None
        self.style = 'minimal'  #  
        self.draft_mode = True  #  draft  
        self.no_image = False  #    
        
        logger.info(f"IMAGE_SERVICE_AVAILABLE: {IMAGE_SERVICE_AVAILABLE}")
        logger.info(f"PLACEHOLDER_SERVICE_AVAILABLE: {PLACEHOLDER_SERVICE_AVAILABLE}")
        
        #  DALL-E 
        if IMAGE_SERVICE_AVAILABLE and DalleService:
            try:
                self.image_service = DalleService()
                self.image_service_available = self.image_service.available
                logger.info(f"Image service available: {self.image_service_available}")
                if self.image_service_available:
                    logger.info("DALL-E service initialized successfully")
                else:
                    logger.warning("DALL-E service initialized but API key not found")
            except Exception as e:
                logger.error(f"Image service initialization failed: {e}", exc_info=True)
                self.image_service_available = False
        
        #   
        if PLACEHOLDER_SERVICE_AVAILABLE and PlaceholderImageService:
            try:
                self.placeholder_service = PlaceholderImageService()
                logger.info("Placeholder image service initialized as fallback")
            except Exception as e:
                logger.error(f"Placeholder service initialization failed: {e}")
                self.placeholder_service = None
    
    def generate_structure(self, planning_input):
        prompt = f"""
           .       .

        :
        {planning_input}

          JSON :
        {{
            "title": " ",
            "sections": [
                {{
                    "title": " ",
                    "content": "  ",
                    "duration": " "
                }}
            ],
            "total_duration": "  ",
            "target_audience": " ",
            "key_message": " "
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            return json.loads(response_text)
        except Exception as e:
            return {
                "error": str(e),
                "fallback": {
                    "title": " ",
                    "sections": [
                        {
                            "title": "",
                            "content": "   ",
                            "duration": "10"
                        },
                        {
                            "title": "",
                            "content": "  ",
                            "duration": "1 30"
                        },
                        {
                            "title": "",
                            "content": "   ",
                            "duration": "20"
                        }
                    ],
                    "total_duration": "2",
                    "target_audience": " ",
                    "key_message": "  "
                }
            }
    
    def generate_story(self, structure_data):
        prompt = f"""
          .      .

        :
        {json.dumps(structure_data, ensure_ascii=False, indent=2)}

          JSON :
        {{
            "story": "   ( )",
            "genre": "",
            "tone": "",
            "key_message": " ",
            "emotional_arc": " "
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            return json.loads(response_text)
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                return {
                    "error": "Gemini API    .   .",
                    "error_type": "quota_exceeded",
                    "fallback": {
                        "story": "    .",
                        "genre": "/",
                        "tone": " ",
                        "key_message": structure_data.get('key_message', ' '),
                        "emotional_arc": "  →   →  →  "
                    }
                }
            return {
                "error": error_msg,
                "fallback": {
                    "story": "    .",
                    "genre": "/",
                    "tone": " ",
                    "key_message": structure_data.get('key_message', ' '),
                    "emotional_arc": "  →   →  →  "
                }
            }
    
    def generate_stories_from_planning(self, planning_text, context=None):
        #   
        if context is None:
            context = {}
        
        logger.info(f"[GeminiService] generate_stories_from_planning ")
        logger.info(f"[GeminiService] planning_text : {len(planning_text)}")
        logger.info(f"[GeminiService] context: {context}")
        
        # Gemini 
        logger.info("[GeminiService] Using Gemini for text generation")
        
        tone = context.get('tone', '')
        genre = context.get('genre', '')
        concept = context.get('concept', '')
        target = context.get('target', '')
        purpose = context.get('purpose', '')
        duration = context.get('duration', '')
        story_framework = context.get('story_framework', 'classic')
        development_level = context.get('development_level', 'balanced')
        character_name = context.get('character_name', '')
        character_description = context.get('character_description', '')
        character_image = context.get('character_image', '')
        
        logger.info(f"[GeminiService] story_framework: {story_framework}")
        
        #   
        aspect_ratio = context.get('aspectRatio', '16:9')
        platform = context.get('platform', '')
        color_tone = context.get('colorTone', '')
        editing_style = context.get('editingStyle', '')
        music_style = context.get('musicStyle', '')
        
        #   
        framework_guides = {
            'classic': "  4 ",
            'hero': "  -  ,  , , ",
            'problem': "-  -  ,  ,  , ",
            'emotional': "  - , , , ",
            'hook_immersion': "--- ",
            'pixar': "  - , , , , ",
            'deductive': " - /,  1,  2,  3, ",
            'inductive': " -  1,  2,  3,  , ",
            'documentary': " -  , /, /, , "
        }
        
        #   
        development_guides = {
            'minimal': "   ",
            'light': "   ",
            'balanced': "   ",
            'detailed': "   "
        }
        
        prompt = f"""
            .     .
        
        [  ]
               .
              .
        
          :
        -  : {target if target else ' '} (       )
        - : {genre if genre else ''} (    )
        - : {tone if tone else ''} (    )
        - : {concept if concept else ''} (   )
        -  : {purpose if purpose else ' '} (     )
        -  : {duration if duration else '3-5'} (   )
        -  : {framework_guides.get(story_framework, framework_guides['classic'])}
        -  : {development_guides.get(development_level, development_guides['balanced'])}
        {f'''-  : {character_name}
        -  : {character_description}''' if character_name or character_description else ''}
        
           :
        {f'- : {platform} (    )' if platform else ''}
        {f'-  : {aspect_ratio} (   )' if aspect_ratio else ''}
        {f'- /: {color_tone} (   )' if color_tone else ''}
        {f'-  : {editing_style} (  )' if editing_style else ''}
        {f'-  : {music_style} (  )' if music_style else ''}
        
          :
        -        (: "10 ", " " )
        -   
        -     
        -       
        {f'-  "{character_name}"  ,     ' if character_name else ''}
        
          :
        -  : " 10   "
        -  :    ,  10    
        
        -  : "  ..."
        -  :       
        
        {self._get_framework_structure(story_framework)}
        
             :
        -   (    )
        -   (///)
        -  
        -  /
        -  
        -   (2-3)
        
        :
        - (, ,  )    
        -    
        -     
        -      
        -    
        
        :
        {planning_text}
        
        {self._get_json_response_format(story_framework)}
        
          4  .
           JSON  ,     JSON .
        """
        
        try:
            logger.info(f"[GeminiService] Gemini API  ")
            
            #   
            max_retries = 3
            retry_count = 0
            last_error = None
            
            while retry_count < max_retries:
                try:
                    response = self.model.generate_content(prompt)
                    response_text = response.text.strip()
                    break  #   
                except Exception as retry_error:
                    retry_count += 1
                    last_error = retry_error
                    logger.warning(f"[GeminiService] Gemini API  {retry_count}/{max_retries} : {retry_error}")
                    
                    if retry_count < max_retries:
                        import time
                        time.sleep(2)  # 2   
                    else:
                        raise last_error  #      
            
            #     
            if hasattr(response, 'usage_metadata'):
                prompt_tokens = response.usage_metadata.prompt_token_count
                response_tokens = response.usage_metadata.candidates_token_count
                total_tokens = response.usage_metadata.total_token_count
                logger.info(f"[GeminiService]   - : {prompt_tokens}, : {response_tokens}, : {total_tokens}")
                self._update_token_usage('story', prompt_tokens, response_tokens)
            
            logger.info(f"[GeminiService] Gemini API  : {len(response_text)}")
            
            # JSON   
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            #  
            response_text = response_text.strip()
            
            # JSON  
            try:
                result = json.loads(response_text)
                #  
                if 'stories' in result and isinstance(result['stories'], list) and len(result['stories']) > 0:
                    logger.info(f"[GeminiService]   : {len(result['stories'])}")
                    return result
                else:
                    raise ValueError("Invalid story structure")
            except json.JSONDecodeError as json_error:
                # JSON        
                logger.error(f"JSON   - : {story_framework}, : {str(json_error)}")
                logger.error(f"   100: {response_text[:100]}")
                logger.error(f"   100: {response_text[-100:]}")
                
                # :    
                if story_framework == 'inductive':
                    with open(f'/tmp/inductive_response_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', 'w') as f:
                        f.write(response_text)
                    logger.error(f"  /tmp/inductive_response_*.txt  .")
                
                raise json_error
                
        except Exception as e:
            logger.error(f"   - : {story_framework}, : {str(e)}")
            
            # Gemini   DALL-E 
            if self.image_service_available and self.image_service:
                logger.info("[GeminiService] Gemini , DALL-E  ")
                try:
                    # DALL-E    ( )
                    #  DALL-E   ,    
                    logger.info("[GeminiService] DALL-E  ,   ")
                except Exception as dalle_error:
                    logger.error(f"DALL-E  : {dalle_error}")
            
            #    
            fallback_stories = self._get_fallback_stories(story_framework)
            
            return {
                "error": str(e),
                "stories": fallback_stories
            }
    
    def generate_scenes_from_story(self, story_data):
        # Gemini 
        logger.info("[GeminiService] Using Gemini for scene generation")
        
        # planning_options 
        planning_options = story_data.get('planning_options', {})
        tone = planning_options.get('tone', '')
        genre = planning_options.get('genre', '')
        concept = planning_options.get('concept', '')
        target = planning_options.get('target', '')
        purpose = planning_options.get('purpose', '')
        duration = planning_options.get('duration', '')
        
        #   
        aspect_ratio = planning_options.get('aspectRatio', '16:9')
        platform = planning_options.get('platform', '')
        color_tone = planning_options.get('colorTone', '')
        editing_style = planning_options.get('editingStyle', '')
        music_style = planning_options.get('musicStyle', '')
        
        prompt = f"""
             .    3  .
           , ,   .
        
        [ ] -    :
        -  : {target if target else ' '}
        - : {genre if genre else ''}
        - : {tone if tone else ''}
        - : {concept if concept else ''}
        -  : {purpose if purpose else ' '}
        -  : {duration if duration else '3-5'}
        
        [  ] -    :
        {f'-   {aspect_ratio}: {"  ,   " if aspect_ratio == "9:16" else " ,   " if aspect_ratio == "16:9" else " ,  "}' if aspect_ratio else ''}
        {f'-  {platform}: {"   " if platform in ["youtube_shorts", "tiktok", "instagram_reels"] else "  " if platform in ["youtube", "tv_broadcast"] else "  "}' if platform else ''}
        {f'-  {color_tone}:     ' if color_tone else ''}
        {f'-   {editing_style}:     ' if editing_style else ''}
        {f'-  {music_style}:     ' if music_style else ''}
        
             :
        1.   (1, 2, 3)
        2.  (   )
        3. 
        4.   (   )
        5.    (  )
        6.   (     )
        
        :
        : {story_data.get('title', '')}
        : {story_data.get('stage', '')} - {story_data.get('stage_name', '')}
        : {', '.join(story_data.get('characters', []))}
         : {story_data.get('key_content', '')}
        : {story_data.get('summary', '')}
        
          JSON :
        {{
            "scenes": [
                {{
                    "scene_number": 1,
                    "location": "",
                    "time": "",
                    "action": " ",
                    "dialogue": "  ",
                    "purpose": " "
                }},
                {{
                    "scene_number": 2,
                    "location": "",
                    "time": "",
                    "action": " ",
                    "dialogue": "  ",
                    "purpose": " "
                }},
                {{
                    "scene_number": 3,
                    "location": "",
                    "time": "",
                    "action": " ",
                    "dialogue": "  ",
                    "purpose": " "
                }}
            ]
        }}
        
          3  .
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            #     
            if hasattr(response, 'usage_metadata'):
                prompt_tokens = response.usage_metadata.prompt_token_count
                response_tokens = response.usage_metadata.candidates_token_count
                total_tokens = response.usage_metadata.total_token_count
                logger.info(f"[GeminiService]     - : {prompt_tokens}, : {response_tokens}, : {total_tokens}")
                self._update_token_usage('scene', prompt_tokens, response_tokens)
            
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            return json.loads(response_text)
        except Exception as e:
            return {
                "error": str(e),
                "fallback": {
                    "scenes": [
                        {
                            "scene_number": 1,
                            "location": "",
                            "time": "",
                            "action": "    ",
                            "dialogue": "  .   ...",
                            "purpose": "    "
                        },
                        {
                            "scene_number": 2,
                            "location": "",
                            "time": "",
                            "action": "     ",
                            "dialogue": "  .   .",
                            "purpose": "    "
                        },
                        {
                            "scene_number": 3,
                            "location": " ",
                            "time": "",
                            "action": "     ",
                            "dialogue": "    .",
                            "purpose": "    "
                        }
                    ]
                }
            }
    
    def generate_shots_from_scene(self, scene_data):
        """
          3  .
        """
        # Gemini 
        logger.info("[GeminiService] Using Gemini for shot generation")
        
        # planning_options 
        planning_options = scene_data.get('planning_options', {})
        tone = planning_options.get('tone', '')
        genre = planning_options.get('genre', '')
        concept = planning_options.get('concept', '')
        
        #   
        aspect_ratio = planning_options.get('aspectRatio', '16:9')
        platform = planning_options.get('platform', '')
        color_tone = planning_options.get('colorTone', '')
        editing_style = planning_options.get('editingStyle', '')
        music_style = planning_options.get('musicStyle', '')
        
        prompt = f"""
           .    3  .
               .
        
        [ ]:
        - : {tone if tone else ''}
        - : {genre if genre else ''}
        - : {concept if concept else ''}
        
        [  ]:
        {f'-   {aspect_ratio}: {" ,  " if aspect_ratio == "9:16" else "  " if aspect_ratio == "21:9" else "  "}' if aspect_ratio else ''}
        {f'-  {color_tone}: {"   " if color_tone == "warm" else "   " if color_tone == "cool" else " "} ' if color_tone else ''}
        {f'-   {editing_style}: {"   " if editing_style == "fast_cuts" else "   " if editing_style == "long_takes" else " "}' if editing_style else ''}
        
             :
        1.   (1, 2, 3)
        2.   (, , ,  )
        3.   (, , , ,  )
        4.   (2-5)
        5.  
        
         :
         : {scene_data.get('scene_number', '')}
        : {scene_data.get('location', '')}
        : {scene_data.get('time', '')}
        : {scene_data.get('action', '')}
        : {scene_data.get('dialogue', '')}
        : {scene_data.get('purpose', '')}
        
        JSON  :
        {{
            "shots": [
                {{
                    "shot_number": 1,
                    "shot_type": " ",
                    "camera_movement": " ",
                    "duration": 3,
                    "description": " "
                }},
                {{
                    "shot_number": 2,
                    "shot_type": " ",
                    "camera_movement": " ",
                    "duration": 3,
                    "description": " "
                }},
                {{
                    "shot_number": 3,
                    "shot_type": " ",
                    "camera_movement": " ",
                    "duration": 3,
                    "description": " "
                }}
            ]
        }}
        
          3  .
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            #     
            if hasattr(response, 'usage_metadata'):
                prompt_tokens = response.usage_metadata.prompt_token_count
                response_tokens = response.usage_metadata.candidates_token_count
                total_tokens = response.usage_metadata.total_token_count
                logger.info(f"[GeminiService]     - : {prompt_tokens}, : {response_tokens}, : {total_tokens}")
                self._update_token_usage('shot', prompt_tokens, response_tokens)
            
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            return json.loads(response_text)
        except Exception as e:
            return {
                "error": str(e),
                "fallback": {
                    "shots": [
                        {
                            "shot_number": 1,
                            "shot_type": "",
                            "camera_movement": "",
                            "duration": 3,
                            "description": "     "
                        },
                        {
                            "shot_number": 2,
                            "shot_type": "",
                            "camera_movement": " ",
                            "duration": 4,
                            "description": "    "
                        },
                        {
                            "shot_number": 3,
                            "shot_type": "",
                            "camera_movement": "",
                            "duration": 3,
                            "description": "    "
                        }
                    ]
                }
            }
    
    def generate_shots(self, story_data):
        prompt = f"""
           .      .

        :
        {json.dumps(story_data, ensure_ascii=False, indent=2)}

          JSON :
        {{
            "shots": [
                {{
                    "shot_number": 1,
                    "type": "  (: ,  )",
                    "description": "  ",
                    "camera_angle": " ",
                    "movement": " ",
                    "duration": " ",
                    "audio": "/ "
                }}
            ],
            "total_shots": "  ",
            "estimated_duration": "  "
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            return json.loads(response_text)
        except Exception as e:
            return {
                "error": str(e),
                "fallback": {
                    "shots": [
                        {
                            "shot_number": 1,
                            "type": "",
                            "description": "  ",
                            "camera_angle": "",
                            "movement": "",
                            "duration": "5",
                            "audio": " "
                        },
                        {
                            "shot_number": 2,
                            "type": "",
                            "description": "  ",
                            "camera_angle": "",
                            "movement": " ",
                            "duration": "10",
                            "audio": ""
                        }
                    ],
                    "total_shots": 2,
                    "estimated_duration": "15"
                }
            }
    
    def generate_storyboards_from_shot(self, shot_data):
        # planning_options  (shot_data scene_info)
        planning_options = shot_data.get('planning_options', {})
        if not planning_options and 'scene_info' in shot_data:
            planning_options = shot_data['scene_info'].get('planning_options', {})
        
        tone = planning_options.get('tone', '')
        genre = planning_options.get('genre', '')
        concept = planning_options.get('concept', '')
        target = planning_options.get('target', '')
        
        #   
        aspect_ratio = planning_options.get('aspectRatio', '16:9')
        platform = planning_options.get('platform', '')
        color_tone = planning_options.get('colorTone', '')
        editing_style = planning_options.get('editingStyle', '')
        music_style = planning_options.get('musicStyle', '')
        
        prompt = f"""
           .     DALL-E 3       .
        
        [  ]:
        -  : {target if target else ' '}
        - : {genre if genre else ''}
        - : {tone if tone else ''}
        - : {concept if concept else ''}
        
        [  ]:
        {f'-   {aspect_ratio}: {"    " if aspect_ratio == "9:16" else "  " if aspect_ratio == "21:9" else "  16:9 "}' if aspect_ratio else ''}
        {f'-  {color_tone}: {"warm color temperature with soft golden tones" if color_tone == "warm" else "cool color temperature with blue undertones" if color_tone == "cool" else "vibrant saturated colors" if color_tone == "vibrant" else "soft pastel color palette" if color_tone == "pastel" else "natural color grading"}' if color_tone else ''}
        {f'-  {platform}: {"mobile-first vertical composition" if platform in ["tiktok", "instagram_reels", "youtube_shorts"] else "cinema-quality wide composition" if platform in ["cinema", "tv_broadcast"] else "standard web video composition"}' if platform else ''}

         :
        {json.dumps(shot_data, ensure_ascii=False, indent=2)}

         : visual_description DALL-E 3    .    :
        
         visual_description  :
        1.     (,  , , ,   )
        2.  : , , , , ,  
        3.   : "wide shot", "close-up", "medium shot", "over-the-shoulder" 
        4.    
        5.    
        
             :
        - "Storyboard", "Frame", "Scene", "", "", ""
        - "Description", "Caption", "Text", ""
        - "Panel", "Script", "Title", "Heading"
        -   ("Frame 1:", "Scene 1:" )
        
          :
        1. "Medium shot of a nervous middle-aged woman in colorful traditional Korean hanbok entering a dimly lit shaman shrine filled with incense smoke, wooden talismans hanging on dark walls, candlelight flickering"
        
        2. "Wide shot of a modern glass-walled office at sunset, young professionals in business casual attire working at computers, city skyline visible through windows, warm golden light streaming in"
        
        3. "Close-up of weathered hands holding prayer beads, soft natural light from side window, blurred traditional Korean interior in background"
        
        4. "Over-the-shoulder shot of a man in his 30s wearing a navy suit looking at laptop screen in busy coffee shop, other customers blurred in background, steam rising from coffee cup"
        
          :
        - "Frame 1:  "
        - "  "
        - "Scene showing entrance"
        - "Storyboard panel of cafe"
        
          JSON :
        {{
            "storyboards": [
                {{
                    "frame_number": 1,
                    "title": "  ( )",
                    "visual_description": "DALL-E    (  )",
                    "description_kr": "    (50    )",
                    "composition": " (: wide shot, close-up, medium shot)",
                    "camera_info": {{
                        "angle": " ",
                        "movement": " ",
                        "lens": " "
                    }},
                    "lighting": " ",
                    "audio": {{
                        "dialogue": "",
                        "sfx": "",
                        "music": ""
                    }},
                    "notes": "  ",
                    "duration": " "
                }}
            ],
            "total_frames": "  ",
            "technical_requirements": " "
        }}
        """
        
        storyboard_data = None
        gemini_error = None
        
        # Gemini    
        try:
            logger.info("[GeminiService] Gemini    ")
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            storyboard_data = json.loads(response_text)
            logger.info("[GeminiService] Gemini    ")
        except Exception as e:
            gemini_error = str(e)
            logger.error(f"[GeminiService] Gemini   : {gemini_error}")
            
            # Gemini     
            logger.info("[GeminiService]    ")
            storyboard_data = {
                "storyboards": [
                    {
                        "frame_number": 1,
                        "title": " ",
                        "visual_description": "Wide establishing shot showing the main character in their environment",
                        "description_kr": "     ",
                        "composition": "wide shot",
                        "camera_info": {
                            "angle": "eye level",
                            "movement": "static",
                            "lens": "standard"
                        },
                        "lighting": "natural lighting",
                        "audio": {
                            "dialogue": "",
                            "sfx": "ambient sound",
                            "music": "background music"
                        },
                        "notes": "  ",
                        "duration": "3"
                    }
                ],
                "total_frames": 1,
                "technical_requirements": "standard production",
                "gemini_error": gemini_error
            }
        
        if storyboard_data:
            
            #    - Gemini   DALL-E  
            storyboards = storyboard_data.get('storyboards', [])
            
            # no_image     
            if getattr(self, 'no_image', False):
                logger.info("Skipping image generation (no_image option is set)")
                for i, frame in enumerate(storyboards):
                    storyboard_data['storyboards'][i]['image_url'] = None
                    storyboard_data['storyboards'][i]['image_note'] = "  "
                return storyboard_data
            
            for i, frame in enumerate(storyboards):
                logger.info(f"Generating image for frame {i+1}")
                image_generated = False
                
                # Gemini  DALL-E  
                if gemini_error and self.image_service_available and self.image_service:
                    logger.info(f"[GeminiService] Gemini  DALL-E  ")
                
                # 1. DALL-E 
                if self.image_service_available and self.image_service:
                    draft_mode = getattr(self, 'draft_mode', True)
                    logger.info(f"[GeminiService] DALL-E    (draft_mode={draft_mode})")
                    try:
                        image_result = self.image_service.generate_storyboard_image(
                            frame, 
                            style=getattr(self, 'style', 'minimal'),
                            draft_mode=draft_mode
                        )
                        if image_result['success']:
                            storyboard_data['storyboards'][i]['image_url'] = image_result['image_url']
                            storyboard_data['storyboards'][i]['prompt_used'] = image_result.get('prompt_used', '')
                            storyboard_data['storyboards'][i]['model_used'] = image_result.get('model_used', 'dall-e')
                            storyboard_data['storyboards'][i]['draft_mode'] = draft_mode
                            image_generated = True
                            logger.info(f"[GeminiService] DALL-E   ")
                        else:
                            logger.warning(f"DALL-E failed for frame {i+1}: {image_result.get('error')}")
                    except Exception as dalle_error:
                        logger.error(f"[GeminiService] DALL-E   : {dalle_error}")
                
                # 2.  
                if not image_generated and self.placeholder_service:
                    logger.info(f"Using placeholder for frame {i+1}")
                    placeholder_result = self.placeholder_service.generate_storyboard_image(frame)
                    if placeholder_result['success']:
                        storyboard_data['storyboards'][i]['image_url'] = placeholder_result['image_url']
                        storyboard_data['storyboards'][i]['is_placeholder'] = True
                        storyboard_data['storyboards'][i]['image_note'] = "  (   )"
                    else:
                        storyboard_data['storyboards'][i]['image_url'] = None
                        storyboard_data['storyboards'][i]['image_error'] = "  "
            
            # Gemini    
            if gemini_error:
                storyboard_data['gemini_error'] = gemini_error
                storyboard_data['fallback_used'] = True
            
            return storyboard_data
        
        # storyboard_data    
        return {
            "error": "Failed to generate storyboard",
            "fallback": {
                    "storyboards": [
                        {
                            "frame_number": 1,
                            "title": " ",
                            "visual_description": "    ",
                            "description_kr": "     ",
                            "composition": " ",
                            "camera_info": {
                                "angle": "",
                                "movement": " ",
                                "lens": " "
                            },
                            "lighting": " ",
                            "audio": {
                                "dialogue": "",
                                "sfx": " ",
                                "music": "  "
                            },
                            "notes": "    ",
                            "duration": "3"
                        },
                        {
                            "frame_number": 2,
                            "title": " ",
                            "visual_description": "   ",
                            "description_kr": "    ",
                            "composition": "3 ",
                            "camera_info": {
                                "angle": "",
                                "movement": "",
                                "lens": " "
                            },
                            "lighting": "  ",
                            "audio": {
                                "dialogue": " ...",
                                "sfx": " ",
                                "music": " "
                            },
                            "notes": "   ",
                            "duration": "5"
                        }
                    ],
                    "total_frames": 2,
                    "technical_requirements": "4K , 60fps,  "
                }
            }
    
    def _get_framework_structure(self, framework):
        """   """
        structures = {
            'classic': """4   ():
        1. () -  [ 10-20%]
           -   
           -   
           -   
        
        2. () -  [ 20-40%]
           -    
           -   
           -  
        
        3. () -  [ 40-30%]
           -  
           -  
           -  
        
        4. () -  [ 30-10%]
           -  
           -   
           -   """,
           
            'hook_immersion': """4   (---):
        1. (Hook) -   [ 5-10%]
           -    
           -    
           -    
        
        2. (Immersion) -    [ 40-50%]
           -     
           -     
           -   
        
        3. (Twist) -    [ 30-35%]
           -     
           -    
           -   
        
        4. (Cliffhanger) -    [ 10-15%]
           -   
           -     
           -    """,
           
            'pixar': """4   ( ):
        1.   - " ..." [ 15-20%]
           -   
           -    
           -   
        
        2.   - "  ..." [ 25-30%]
           -    
           -    
           -    
        
        3.   - "..." [ 35-40%]
           -   
           -   
           -    
        
        4.   - "..." [ 15-20%]
           -   
           -    
           -    """,
           
            'deductive': """4   ( ):
        1.  /  [ 15-20%]
           -     
           -      
           -    
        
        2.     [ 25-30%]
           -     
           -    
           -    
        
        3.    [ 30-35%]
           -    
           -    
           -    
        
        4.    [ 20-25%]
           -     
           -      
           -   """,
           
            'inductive': """4   ( ):
        1.     [ 20-25%]
           -     
           -   
           -   
        
        2.    [ 30-35%]
           -    
           -    
           -   
        
        3.    [ 25-30%]
           -     
           -     
           -     
        
        4.    [ 20-25%]
           -    
           -    
           -   """,
           
            'documentary': """4   ( ):
        1.     [ 20-25%]
           -     
           -    
           -   
        
        2.    [ 30-35%]
           -   
           -    
           -   
        
        3.   [ 25-30%]
           -    
           -   
           -    
        
        4.   [ 20-25%]
           -   
           -   
           -    """
        }
        
        return structures.get(framework, structures['classic'])
    
    def _get_json_response_format(self, framework):
        """ JSON  """
        formats = {
            'classic': """  JSON :
        {{
            "stories": [
                {{
                    "title": "",
                    "stage": "",
                    "stage_name": "",
                    "characters": ["1", "2"],
                    "key_content": " ",
                    "summary": " "
                }},
                {{
                    "title": "",
                    "stage": "",
                    "stage_name": "",
                    "characters": ["1", "2"],
                    "key_content": " ",
                    "summary": " "
                }},
                {{
                    "title": "",
                    "stage": "",
                    "stage_name": "",
                    "characters": ["1", "2"],
                    "key_content": " ",
                    "summary": " "
                }},
                {{
                    "title": "",
                    "stage": "",
                    "stage_name": "",
                    "characters": ["1", "2"],
                    "key_content": " ",
                    "summary": " "
                }}
            ]
        }}""",
            
            'hook_immersion': """  JSON :
        {{
            "stories": [
                {{
                    "title": "  ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": [""],
                    "key_content": "    ",
                    "summary": " 5     "
                }},
                {{
                    "title": " ",
                    "stage": "",
                    "stage_name": "  ",
                    "characters": [" "],
                    "key_content": "  ",
                    "summary": "      "
                }},
                {{
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": [" "],
                    "key_content": "    ",
                    "summary": "    "
                }},
                {{
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": [""],
                    "key_content": "    ",
                    "summary": "    "
                }}
            ]
        }}""",
            
            'pixar': """  JSON :
        {{
            "stories": [
                {{
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": ["", ""],
                    "key_content": "   ",
                    "summary": "   "
                }},
                {{
                    "title": "  ",
                    "stage": "",
                    "stage_name": "  ",
                    "characters": ["", " "],
                    "key_content": "   ",
                    "summary": "    "
                }},
                {{
                    "title": " ",
                    "stage": "",
                    "stage_name": "",
                    "characters": ["", ""],
                    "key_content": "  ,  ",
                    "summary": "    "
                }},
                {{
                    "title": " ",
                    "stage": "",
                    "stage_name": "",
                    "characters": [" "],
                    "key_content": "   ",
                    "summary": "     "
                }}
            ]
        }}""",
            
            'deductive': """  JSON :
        {{
            "stories": [
                {{
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": ["/"],
                    "key_content": "   ",
                    "summary": "     "
                }},
                {{
                    "title": "  ",
                    "stage": "1",
                    "stage_name": " ",
                    "characters": ["", " "],
                    "key_content": "   ",
                    "summary": "    "
                }},
                {{
                    "title": " ",
                    "stage": "2",
                    "stage_name": " ",
                    "characters": [" "],
                    "key_content": "   ",
                    "summary": "     "
                }},
                {{
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": [""],
                    "key_content": "    ",
                    "summary": "      "
                }}
            ]
        }}""",
            
            'inductive': """  JSON :
        {{
            "stories": [
                {{
                    "title": " ",
                    "stage": "1",
                    "stage_name": "  ",
                    "characters": [" "],
                    "key_content": "   ",
                    "summary": "     "
                }},
                {{
                    "title": " ",
                    "stage": "2",
                    "stage_name": " ",
                    "characters": [" "],
                    "key_content": "  ",
                    "summary": "    "
                }},
                {{
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": ["/"],
                    "key_content": "   ",
                    "summary": "    "
                }},
                {{
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": [""],
                    "key_content": " ",
                    "summary": "    "
                }}
            ]
        }}""",
            
            'documentary': """  JSON :
        {{
            "stories": [
                {{
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": ["", ""],
                    "key_content": "   ",
                    "summary": "   ,  "
                }},
                {{
                    "title": "  ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": ["", ""],
                    "key_content": "  ",
                    "summary": "      "
                }},
                {{
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": [" "],
                    "key_content": "    ",
                    "summary": "    "
                }},
                {{
                    "title": " ",
                    "stage": "",
                    "stage_name": "",
                    "characters": [""],
                    "key_content": "  ",
                    "summary": "     "
                }}
            ]
        }}"""
        }
        
        return formats.get(framework, formats['classic'])
    
    def summarize_for_pdf(self, planning_data):
        """PDF      """
        try:
            #   
            user_settings = {
                'tone': planning_data.get('tone', ''),
                'genre': planning_data.get('genre', ''),
                'concept': planning_data.get('concept', ''),
                'target': planning_data.get('target', ''),
                'purpose': planning_data.get('purpose', ''),
                'duration': planning_data.get('duration', ''),
                'aspectRatio': planning_data.get('planning_options', {}).get('aspectRatio', '16:9'),
                'platform': planning_data.get('planning_options', {}).get('platform', ''),
                'colorTone': planning_data.get('planning_options', {}).get('colorTone', ''),
                'editingStyle': planning_data.get('planning_options', {}).get('editingStyle', ''),
                'musicStyle': planning_data.get('planning_options', {}).get('musicStyle', ''),
                'storyFramework': planning_data.get('planning_options', {}).get('storyFramework', ''),
                'characterName': planning_data.get('planning_options', {}).get('characterName', ''),
                'characterDescription': planning_data.get('planning_options', {}).get('characterDescription', '')
            }
            
            prompt = f"""
     . 
PDF         .

[  ]
- : {user_settings['tone']}
- : {user_settings['genre']} 
- : {user_settings['concept']}
- : {user_settings['target']}
- : {user_settings['purpose']}
- : {user_settings['duration']}
- : {user_settings['aspectRatio']}
- : {user_settings['platform']}
- : {user_settings['colorTone']}
- : {user_settings['editingStyle']}
- : {user_settings['musicStyle']}
- : {user_settings['storyFramework']}
- : {user_settings['characterName']} - {user_settings['characterDescription']}

[ ]
{planning_data.get('planning_text', '')}

[ ]
{json.dumps(planning_data.get('stories', []), ensure_ascii=False)}

[ ]
{json.dumps(planning_data.get('scenes', []), ensure_ascii=False)}

   :

1. ** ** ( )
2. ** ** (  )
   -   (, ,  )
   -   (, ,  )
   -   (,   )
3. ** ** (3-4   )
4. **  ** (  1-2 )
5. ** ** (    )

    ,      .
"""
            
            response = self.pro_model.generate_content(prompt)
            summary = response.text
            
            # JSON   
            return {
                'success': True,
                'summary': summary,
                'original_settings': user_settings
            }
            
        except Exception as e:
            logger.error(f"PDF   : {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'summary': None
            }
    
    def _get_fallback_stories(self, framework):
        """   """
        fallback_stories = {
            'classic': [
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": "",
                    "characters": ["", ""],
                    "key_content": "     ",
                    "summary": "         ."
                },
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": "",
                    "characters": ["", "", ""],
                    "key_content": "     ",
                    "summary": "     ."
                },
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": "",
                    "characters": ["", "", ""],
                    "key_content": "      ",
                    "summary": "       ."
                },
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": "",
                    "characters": ["", "", " "],
                    "key_content": "     ",
                    "summary": "     ."
                }
            ],
            'hook_immersion': [
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": [""],
                    "key_content": "    ",
                    "summary": "      ."
                },
                {
                    "title": "  ",
                    "stage": "",
                    "stage_name": "  ",
                    "characters": ["", " "],
                    "key_content": "    ",
                    "summary": "     ."
                },
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": ["", " "],
                    "key_content": "    ",
                    "summary": "     ."
                },
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": [""],
                    "key_content": "    ",
                    "summary": "      ."
                }
            ],
            'pixar': [
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": ["", " "],
                    "key_content": "   ",
                    "summary": "    ."
                },
                {
                    "title": "  ",
                    "stage": "",
                    "stage_name": "  ",
                    "characters": ["", " "],
                    "key_content": "   ",
                    "summary": "     ."
                },
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": "",
                    "characters": ["", ""],
                    "key_content": "  ,  ",
                    "summary": "    ."
                },
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": "",
                    "characters": [" "],
                    "key_content": "   ",
                    "summary": "     ."
                }
            ],
            'deductive': [
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": ["/"],
                    "key_content": "   ",
                    "summary": "     ."
                },
                {
                    "title": " ",
                    "stage": "1",
                    "stage_name": " ",
                    "characters": ["", " "],
                    "key_content": "   ",
                    "summary": "    ."
                },
                {
                    "title": " ",
                    "stage": "2",
                    "stage_name": " ",
                    "characters": [" "],
                    "key_content": "   ",
                    "summary": "     ."
                },
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": [""],
                    "key_content": "    ",
                    "summary": "      ."
                }
            ],
            'inductive': [
                {
                    "title": "  ",
                    "stage": "1",
                    "stage_name": "  ",
                    "characters": ["", " "],
                    "key_content": "   ",
                    "summary": "      "
                },
                {
                    "title": " ",
                    "stage": "2",
                    "stage_name": " ",
                    "characters": ["  "],
                    "key_content": "   ",
                    "summary": "      "
                },
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": ["", ""],
                    "key_content": "    ",
                    "summary": "     "
                },
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": [""],
                    "key_content": "   ",
                    "summary": "       "
                }
            ],
            'documentary': [
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": ["", ""],
                    "key_content": "   ",
                    "summary": "    ."
                },
                {
                    "title": "  ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": ["", ""],
                    "key_content": "   ",
                    "summary": "    ."
                },
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": " ",
                    "characters": [" "],
                    "key_content": "    ",
                    "summary": "    ."
                },
                {
                    "title": " ",
                    "stage": "",
                    "stage_name": "",
                    "characters": [""],
                    "key_content": "   ",
                    "summary": "     ."
                }
            ]
        }
        
        #      ,  classic 
        return fallback_stories.get(framework, fallback_stories['classic'])
    
    def _update_token_usage(self, feature, prompt_tokens, response_tokens):
        """  """
        total_tokens = prompt_tokens + response_tokens
        
        #   
        self.token_usage['total'] += total_tokens
        self.token_usage['prompt'] += prompt_tokens
        self.token_usage['response'] += response_tokens
        
        #   
        if feature in self.token_usage['by_feature']:
            self.token_usage['by_feature'][feature]['prompt'] += prompt_tokens
            self.token_usage['by_feature'][feature]['response'] += response_tokens
            self.token_usage['by_feature'][feature]['total'] += total_tokens
    
    def get_token_usage(self):
        """  """
        return self.token_usage
    
    def reset_token_usage(self):
        """  """
        self.token_usage = {
            'total': 0,
            'prompt': 0,
            'response': 0,
            'by_feature': {
                'story': {'prompt': 0, 'response': 0, 'total': 0},
                'scene': {'prompt': 0, 'response': 0, 'total': 0},
                'shot': {'prompt': 0, 'response': 0, 'total': 0},
                'storyboard': {'prompt': 0, 'response': 0, 'total': 0}
            }
        }