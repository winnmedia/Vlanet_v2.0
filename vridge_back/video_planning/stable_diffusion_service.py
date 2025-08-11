import os
import logging
import requests
import base64
from io import BytesIO
from PIL import Image
from django.conf import settings

logger = logging.getLogger(__name__)


class StableDiffusionService:
    """
    Hugging Face API  Stable Diffusion   
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'HUGGINGFACE_API_KEY', None) or os.environ.get('HUGGINGFACE_API_KEY')
        self.available = bool(self.api_key)
        
        if not self.available:
            logger.warning("HUGGINGFACE_API_KEY not found. Image generation will not be available.")
        else:
            logger.info("Stable Diffusion service initialized with API key")
        
        # Hugging Face Inference API endpoints - v1.5 
        self.models = [
            "runwayml/stable-diffusion-v1-5",  #     ()
        ]
        self.current_model_index = 0
        self.api_url = f"https://api-inference.huggingface.co/models/{self.models[self.current_model_index]}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def generate_storyboard_image(self, frame_data):
        """
             .
        """
        if not self.available:
            return {
                "success": False,
                "error": "     . HUGGINGFACE_API_KEY .",
                "image_url": None
            }
        
        try:
            prompt = self._create_storyboard_prompt(frame_data)
            
            #    
            for attempt in range(len(self.models)):
                current_model = self.models[self.current_model_index]
                self.api_url = f"https://api-inference.huggingface.co/models/{current_model}"
                
                logger.info(f"Trying model: {current_model}")
                
                # v1.5  
                width, height = 512, 512  # v1.5 512x512 
                steps = 25  #    
                
                # Hugging Face API 
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "negative_prompt": "ugly, blurry, low quality, distorted, disfigured",
                            "num_inference_steps": steps,
                            "guidance_scale": 7.5,
                            "width": width,
                            "height": height
                        }
                    },
                    timeout=30
                )
            
                if response.status_code == 200:
                    #   base64 
                    image_bytes = response.content
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                    image_url = f"data:image/png;base64,{image_base64}"
                    
                    logger.info(f"Successfully generated image with model: {current_model}")
                    return {
                        "success": True,
                        "image_url": image_url,
                        "prompt_used": prompt,
                        "model_used": current_model
                    }
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', '   ')
                    except:
                        error_msg = f"Status {response.status_code}: {response.text[:200]}"
                    logger.warning(f"Model {current_model} failed: {error_msg}")
                    
                    #   
                    self.current_model_index = (self.current_model_index + 1) % len(self.models)
                    
                    # 503      
                    if response.status_code == 503:
                        continue
                    # 429  
                    elif response.status_code == 429:
                        continue
            
            #    
            return {
                "success": False,
                "error": "    .    .",
                "image_url": None,
                "models_tried": self.models
            }
                    
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return {
                "success": False,
                "error": f"    : {str(e)}",
                "image_url": None
            }
    
    def _create_storyboard_prompt(self, frame_data):
        """
             .
        v1.5  
        """
        visual_desc = frame_data.get('visual_description', '')
        shot_type = frame_data.get('shot_type', '')
        action = frame_data.get('action', '')
        
        # v1.5    
        prompt_parts = []
        
        #  
        if visual_desc:
            #    
            prompt_parts.append(visual_desc)
        
        if action:
            prompt_parts.append(action)
        
        #   (v1.5 )
        prompt_parts.extend([
            "storyboard",
            "professional",
            "clean lines",
            "sketch style",
            "movie storyboard"
        ])
        
        prompt = ", ".join(filter(None, prompt_parts))
        
        # v1.5 75    
        if len(prompt) > 150:
            prompt = prompt[:150]
            
        logger.debug(f"Generated prompt: {prompt}")
        return prompt