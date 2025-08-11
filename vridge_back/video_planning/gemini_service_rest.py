import os
import json
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiServiceREST:
    """Gemini REST API   - 403  """
    
    def __init__(self):
        self.api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in settings or environment variables")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.headers = {
            "Content-Type": "application/json",
            "Referer": "http://localhost:3000",
            "Origin": "http://localhost:3000"
        }
        
        #   
        self.token_usage = {
            'total': 0,
            'prompt': 0,
            'response': 0,
            'by_feature': {
                'story': {'prompt': 0, 'response': 0, 'total': 0},
                'scene': {'prompt': 0, 'response': 0, 'total': 0},
                'shot': {'prompt': 0, 'response': 0, 'total': 0}
            }
        }
    
    def _make_request(self, model_name, prompt, temperature=0.9, max_tokens=None):
        """REST API """
        url = f"{self.base_url}/{model_name}:generateContent?key={self.api_key}"
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": temperature,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        if max_tokens:
            data["generationConfig"]["maxOutputTokens"] = max_tokens
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                
                #   
                if 'usageMetadata' in result:
                    usage = result['usageMetadata']
                    prompt_tokens = usage.get('promptTokenCount', 0)
                    response_tokens = usage.get('candidatesTokenCount', 0)
                    total_tokens = usage.get('totalTokenCount', 0)
                    
                    self.token_usage['prompt'] += prompt_tokens
                    self.token_usage['response'] += response_tokens
                    self.token_usage['total'] += total_tokens
                    
                    logger.info(f"Token usage - Prompt: {prompt_tokens}, Response: {response_tokens}, Total: {total_tokens}")
                
                #   
                if result.get('candidates') and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    logger.error("No candidates in response")
                    return None
                    
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"API request error: {str(e)}")
            return None
    
    def _update_token_usage(self, feature, prompt_tokens, response_tokens):
        """  """
        total = prompt_tokens + response_tokens
        self.token_usage['by_feature'][feature]['prompt'] += prompt_tokens
        self.token_usage['by_feature'][feature]['response'] += response_tokens
        self.token_usage['by_feature'][feature]['total'] += total
    
    def get_token_usage(self):
        """  """
        return self.token_usage
    
    def generate_content(self, prompt, temperature=0.9, model="gemini-1.5-flash"):
        """  """
        return self._make_request(model, prompt, temperature)
    
    def generate_stories_from_planning(self, planning_text, context=None):
        """  """
        if context is None:
            context = {}
        
        #   
        tone = context.get('tone', '')
        genre = context.get('genre', '')
        concept = context.get('concept', '')
        target = context.get('target', '')
        purpose = context.get('purpose', '')
        duration = context.get('duration', '')
        story_framework = context.get('story_framework', 'classic')
        
        #  
        framework_structures = {
            'classic': " ",
            'hook_immersion': "--- ",
            'pixar': " ",
            'deductive': " ",
            'inductive': " ",
            'documentary': " "
        }
        
        prompt = f"""
            .    {framework_structures.get(story_framework, '')}   .
        
        : {target if target else ' '}
        : {genre if genre else ''}
        : {tone if tone else ''}
        : {concept if concept else ''}
        : {purpose if purpose else ' '}
        : {duration if duration else '3-5'}
        
        :
        {planning_text}
        
         JSON   4  :
        {{
            "stories": [
                {{
                    "title": "",
                    "stage": "",
                    "stage_name": " ",
                    "characters": ["1", "2"],
                    "key_content": " ",
                    "summary": " "
                }}
            ]
        }}
        
           JSON  ,    JSON .
        """
        
        try:
            response_text = self._make_request("gemini-1.5-flash", prompt)
            
            if response_text:
                # JSON  
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                result = json.loads(response_text.strip())
                
                if 'stories' in result:
                    #    ()
                    self._update_token_usage('story', len(prompt)//4, len(response_text)//4)
                    return result
                    
            return None
            
        except Exception as e:
            logger.error(f"Story generation error: {str(e)}")
            return None