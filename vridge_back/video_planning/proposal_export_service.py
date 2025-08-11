"""
AI    
Google Gemini Google Slides API        
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from django.conf import settings
from .google_slides_service import GoogleSlidesService

logger = logging.getLogger(__name__)


class ProposalExportService:
    """   """
    
    def __init__(self):
        # Gemini API 
        api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY  .")
        
        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Google Slides  
        try:
            self.slides_service = GoogleSlidesService()
            self.slides_available = self.slides_service.service is not None
        except Exception as e:
            logger.error(f"Google Slides   : {e}")
            self.slides_service = None
            self.slides_available = False
    
    def process_proposal_text(self, raw_text: str) -> Dict[str, Any]:
        """
              
        
        Args:
            raw_text:      
            
        Returns:
              
        """
        try:
            prompt = self._create_structuring_prompt(raw_text)
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            
            # JSON  
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            structured_data = json.loads(response_text)
            return {
                'success': True,
                'data': structured_data,
                'original_text': raw_text
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON  : {e}")
            return self._get_fallback_structure(raw_text)
        except Exception as e:
            logger.error(f"  : {e}")
            return self._get_fallback_structure(raw_text)
    
    def _create_structuring_prompt(self, raw_text: str) -> str:
        """
        Gemini API    
        
        A4      
        """
        return f"""
     . 
      A4  Google Slides   .

**    **
1. A4 (16:9)   
2.    5-7  
3.    
4.     
5.     

**   **
{raw_text}

**   **
 JSON  :

{{
    "metadata": {{
        "title": "  (20 )",
        "subtitle": " (30 )",
        "project_type": "  (: , ,  )",
        "target_audience": " ",
        "duration": " ",
        "budget_range": "   ( )",
        "deadline": " ( )"
    }},
    "slides": [
        {{
            "slide_number": 1,
            "layout": "TITLE",
            "title": " ",
            "content": {{
                "title_text": " ",
                "subtitle_text": ""
            }}
        }},
        {{
            "slide_number": 2,
            "layout": "TITLE_AND_BODY",
            "title": " ",
            "content": {{
                "bullet_points": [
                    "•  :   ",
                    "•  :  ",
                    "•  :  ",
                    "•  :   "
                ]
            }}
        }},
        {{
            "slide_number": 3,
            "layout": "TITLE_AND_TWO_COLUMNS",
            "title": " ",
            "content": {{
                "left_column": [
                    "•  (10-15%)",
                    "•     ",
                    "•   "
                ],
                "right_column": [
                    "•  (70-80%)",
                    "•   ",
                    "•    "
                ]
            }}
        }},
        {{
            "slide_number": 4,
            "layout": "TITLE_AND_BODY",
            "title": " ",
            "content": {{
                "bullet_points": [
                    "•  :  ",
                    "•  :  ",
                    "•  : , ,  ",
                    "•  : , , "
                ]
            }}
        }},
        {{
            "slide_number": 5,
            "layout": "TITLE_AND_BODY",
            "title": "  ",
            "content": {{
                "budget_breakdown": [
                    "• /:  ",
                    "• :   ",
                    "• :   CG",
                    "•  : ,  "
                ],
                "timeline": [
                    "•  : ",
                    "•  : ", 
                    "•  : ",
                    "•  : "
                ]
            }}
        }},
        {{
            "slide_number": 6,
            "layout": "TITLE_AND_BODY",
            "title": "    ",
            "content": {{
                "bullet_points": [
                    "•   ",
                    "•    ",
                    "•  KPI ",
                    "•     "
                ]
            }}
        }}
    ]
}}

**  **
1.       "    " 
2.    15-25  
3.     
4.     
5. A4      

  JSON  .
"""
    
    def _get_fallback_structure(self, raw_text: str) -> Dict[str, Any]:
        """Gemini API     """
        return {
            'success': False,
            'error': 'AI  ',
            'data': {
                'metadata': {
                    'title': ' ',
                    'subtitle': '  ...',
                    'project_type': '',
                    'target_audience': '   ',
                    'duration': ' ',
                    'budget_range': '    ',
                    'deadline': '    '
                },
                'slides': [
                    {
                        'slide_number': 1,
                        'layout': 'TITLE',
                        'title': ' ',
                        'content': {
                            'title_text': ' ',
                            'subtitle_text': '   '
                        }
                    },
                    {
                        'slide_number': 2,
                        'layout': 'TITLE_AND_BODY',
                        'title': '  ',
                        'content': {
                            'bullet_points': [
                                f'•  : {raw_text[:100]}...',
                                '• AI   ',
                                '•   '
                            ]
                        }
                    }
                ]
            },
            'original_text': raw_text
        }
    
    def create_google_slides(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """
          Google Slides  
        
        Args:
            structured_data: process_proposal_text()   
            
        Returns:
             Google Slides  (URL )
        """
        if not self.slides_available:
            return {
                'success': False,
                'error': 'Google Slides    . GOOGLE_APPLICATION_CREDENTIALS .'
            }
        
        try:
            data = structured_data['data']
            metadata = data['metadata']
            title = metadata['title']
            
            # Google Slides 
            result = self.slides_service.create_structured_presentation(title, data)
            
            if 'error' in result:
                return {
                    'success': False,
                    'error': result['error']
                }
            
            return {
                'success': True,
                'presentation_id': result['presentation_id'],
                'url': result['url'],
                'title': title,
                'slide_count': len(data['slides'])
            }
            
        except Exception as e:
            logger.error(f"Google Slides  : {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_proposal(self, raw_text: str) -> Dict[str, Any]:
        """
            
        
        Args:
            raw_text:   
            
        Returns:
              (Google Slides URL )
        """
        logger.info(f"   -  : {len(raw_text)}")
        
        # 1:  
        structure_result = self.process_proposal_text(raw_text)
        
        if not structure_result['success']:
            return {
                'success': False,
                'step': 'structuring',
                'error': '  ',
                'details': structure_result
            }
        
        # 2: Google Slides 
        slides_result = self.create_google_slides(structure_result)
        
        if not slides_result['success']:
            return {
                'success': False,
                'step': 'slides_creation',
                'error': 'Google Slides  ',
                'structured_data': structure_result['data'],  #   
                'details': slides_result
            }
        
        # 
        return {
            'success': True,
            'structured_data': structure_result['data'],
            'presentation': {
                'id': slides_result['presentation_id'],
                'url': slides_result['url'],
                'title': slides_result['title'],
                'slide_count': slides_result['slide_count']
            },
            'original_text': raw_text
        }


class ProposalPromptOptimizer:
    """    """
    
    @staticmethod
    def create_executive_summary_prompt(text: str) -> str:
        """  """
        return f"""
    :
-   3
-  ROI
-    
-  

: {text}
"""
    
    @staticmethod
    def create_technical_spec_prompt(text: str) -> str:
        """  """
        return f"""
    :
-   
-   
-    
-  

: {text}
"""
    
    @staticmethod
    def create_budget_breakdown_prompt(text: str) -> str:
        """   """
        return f"""
     :
-  (, , )
-  ( , , )
-  (, , )
-  (, , )

: {text}
"""