import logging
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

logger = logging.getLogger(__name__)


class PlaceholderImageService:
    """
            
    """
    
    def __init__(self):
        self.available = True
        logger.info("Placeholder image service initialized")
    
    def generate_storyboard_image(self, frame_data):
        """
            .
        """
        try:
            # 16:9   
            width, height = 768, 432
            
            #  ( )
            background_color = (240, 240, 240)
            
            #  
            img = Image.new('RGB', (width, height), background_color)
            draw = ImageDraw.Draw(img)
            
            #   
            frame_number = frame_data.get('frame_number', 0)
            title = frame_data.get('title', ' ')
            visual_desc = frame_data.get('visual_description', ' ')
            
            #  
            border_color = (200, 200, 200)
            draw.rectangle([0, 0, width-1, height-1], outline=border_color, width=3)
            
            #  
            text_color = (50, 50, 50)
            
            #  
            try:
                #   
                #  ()
                draw.text((20, 40), title, fill=text_color)
                
                #  ()
                #     
                max_width = width - 40
                words = visual_desc.split()
                lines = []
                current_line = []
                
                for word in words:
                    current_line.append(word)
                    test_line = ' '.join(current_line)
                    #    ( 8)
                    if len(test_line) * 8 > max_width:
                        if len(current_line) > 1:
                            current_line.pop()
                            lines.append(' '.join(current_line))
                            current_line = [word]
                        else:
                            lines.append(test_line)
                            current_line = []
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                #  
                y_offset = height // 2 - (len(lines) * 20) // 2
                for i, line in enumerate(lines[:5]):  #  5
                    draw.text((20, y_offset + i * 25), line, fill=text_color)
                
                #  "STORYBOARD" 
                draw.text((width - 120, height - 30), "STORYBOARD", fill=(180, 180, 180))
                
            except Exception as e:
                logger.warning(f"Error drawing text: {e}")
                #      
                draw.rectangle([20, 20, width-20, height-20], outline=text_color, width=2)
            
            #  base64 
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            image_bytes = buffer.getvalue()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            image_url = f"data:image/png;base64,{image_base64}"
            
            return {
                "success": True,
                "image_url": image_url,
                "prompt_used": f"Placeholder for: {visual_desc}",
                "is_placeholder": True
            }
            
        except Exception as e:
            logger.error(f"Error generating placeholder image: {str(e)}")
            return {
                "success": False,
                "error": f"   : {str(e)}",
                "image_url": None
            }