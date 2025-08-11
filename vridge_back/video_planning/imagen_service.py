import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class ImagenService:
    """
    Google Imagen  ( placeholder)
    
    : Google Imagen API  Vertex AI   ,
     google-generativeai     .
    
       Imagen API     .
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in settings or environment variables")
        
        #  Imagen API     placeholder
        self.available = False
        logger.info("Imagen service initialized (placeholder mode)")
    
    def generate_storyboard_image(self, frame_description):
        """
             .
         placeholder  .
        """
        
        #  Imagen API    
        #    
        
        prompt = self._create_storyboard_prompt(frame_description)
        
        return {
            "success": False,
            "error": "Imagen API  Vertex AI   ",
            "image_url": None,
            "prompt_used": prompt,
            "alternative": "        "
        }
    
    def _create_storyboard_prompt(self, frame_data):
        """
             .
        """
        visual_desc = frame_data.get('visual_description', '')
        composition = frame_data.get('composition', '')
        camera_info = frame_data.get('camera_info', {})
        lighting = frame_data.get('lighting', '')
        
        prompt = f"""
        Professional storyboard illustration:
        {visual_desc}
        
        Composition: {composition}
        Camera angle: {camera_info.get('angle', 'eye level')}
        Lighting: {lighting}
        
        Style: Clean pencil sketch, professional storyboard art
        """
        
        return prompt.strip()


class StableDiffusionService:
    """
    Stable Diffusion     (Hugging Face API)
       
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'HUGGINGFACE_API_KEY', None) or os.environ.get('HUGGINGFACE_API_KEY')
        #  Stable Diffusion  ( )
        # self.api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
        # self.api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        self.api_url = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
        self.available = bool(self.api_key)
        
        if not self.available:
            logger.warning("Hugging Face API key not found - Stable Diffusion service unavailable")
    
    def generate_storyboard_image(self, frame_description, retry_count=0):
        """
        Stable Diffusion    .
        503     
        """
        if not self.available:
            return {
                "success": False,
                "error": "Hugging Face API   ",
                "image_url": None
            }
        
        try:
            import requests
            import time
            import base64
            from django.core.files.base import ContentFile
            from django.core.files.storage import default_storage
            import uuid
            
            prompt = self._create_storyboard_prompt(frame_description)
            
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            #     
            timeout = 120 if retry_count == 0 else 60
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json={"inputs": prompt},
                timeout=timeout
            )
            
            if response.status_code == 200:
                #    
                image_data = response.content
                file_name = f"storyboard_{uuid.uuid4().hex[:8]}.png"
                file_path = f"storyboards/{file_name}"
                
                # Django  
                saved_path = default_storage.save(file_path, ContentFile(image_data))
                image_url = default_storage.url(saved_path)
                
                return {
                    "success": True,
                    "image_url": image_url,
                    "prompt_used": prompt
                }
            elif response.status_code == 503 and retry_count < 3:
                #    - 
                wait_time = 30 * (retry_count + 1)  # 30, 60, 90
                logger.info(f"  ... {wait_time}   ( {retry_count + 1}/3)")
                time.sleep(wait_time)
                return self.generate_storyboard_image(frame_description, retry_count + 1)
            else:
                error_msg = response.text[:200] if response.text else f" : {response.status_code}"
                return {
                    "success": False,
                    "error": f"API : {error_msg}",
                    "image_url": None
                }
                
        except requests.exceptions.Timeout:
            if retry_count < 2:
                logger.info(f" .  ... ( {retry_count + 1}/2)")
                time.sleep(10)
                return self.generate_storyboard_image(frame_description, retry_count + 1)
            else:
                return {
                    "success": False,
                    "error": "  .    .",
                    "image_url": None
                }
        except Exception as e:
            logger.error(f"Stable Diffusion   : {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "image_url": None
            }
    
    def _create_storyboard_prompt(self, frame_data):
        """
          Stable Diffusion  .
        """
        visual_desc = frame_data.get('visual_description', '')
        composition = frame_data.get('composition', '')
        camera_info = frame_data.get('camera_info', {})
        lighting = frame_data.get('lighting', '')
        
        # Stable Diffusion  
        prompt = f"""
        storyboard sketch, pencil drawing, professional storyboard art,
        {visual_desc},
        {composition} composition,
        {camera_info.get('angle', 'eye level')} angle,
        {lighting} lighting,
        black and white sketch, clean lines
        """
        
        return prompt.strip()