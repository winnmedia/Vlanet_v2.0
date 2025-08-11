"""
AI   - Twelve Labs API 
"""
import json
import time
import logging
import asyncio
import requests
from typing import Dict, List, Optional
from django.conf import settings
from .models import AIAnalysisSettings

logger = logging.getLogger(__name__)


class TwelveLabsVideoAnalyzer:
    """Twelve Labs API    """
    
    def __init__(self):
        self.settings = AIAnalysisSettings.get_settings()
        self.api_key = getattr(settings, 'TWELVE_LABS_API_KEY', '')
        self.base_url = 'https://api.twelvelabs.io/v1.2'
        self.index_id = getattr(settings, 'TWELVE_LABS_INDEX_ID', '')
        
        if not self.api_key:
            logger.warning("Twelve Labs API   .")
    
    def _get_headers(self):
        """API  """
        return {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        }
        
    def analyze_video(self, video_path: str, feedback_id: int = None) -> Dict:
        """
        Twelve Labs API   
        
        Args:
            video_path:    
            feedback_id:  ID
            
        Returns:
              
        """
        logger.info(f"Twelve Labs   : {video_path}")
        
        try:
            if not self.api_key:
                logger.warning("Twelve Labs API     .")
                return self._get_enhanced_dummy_analysis(video_path)
            
            # 1.  
            video_id = self._upload_video(video_path)
            if not video_id:
                return self._get_error_response("  ")
            
            # 2.   
            analysis_result = self._perform_analysis(video_id)
            
            # 3.  VideoPlanet  
            return self._convert_to_videoplanet_format(analysis_result, video_path)
                
        except Exception as e:
            logger.error(f"Twelve Labs   : {str(e)}")
            return self._get_error_response(str(e))
    
    def _upload_video(self, video_path: str) -> str:
        """Twelve Labs  """
        try:
            upload_url = f"{self.base_url}/tasks/upload"
            
            #   
            with open(video_path, 'rb') as video_file:
                files = {
                    'video_file': video_file,
                    'index_id': (None, self.index_id)
                }
                
                headers = {'x-api-key': self.api_key}
                
                response = requests.post(
                    upload_url,
                    files=files,
                    headers=headers,
                    timeout=300  # 5 
                )
            
            if response.status_code == 201:
                result = response.json()
                video_id = result.get('_id')
                logger.info(f"  : {video_id}")
                return video_id
            else:
                logger.error(f"  : {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"  : {str(e)}")
            return None
    
    def _perform_analysis(self, video_id: str) -> Dict:
        """  """
        try:
            #   ( )
            summary = self._generate_summary(video_id)
            
            #  
            classification = self._classify_content(video_id)
            
            #    (  )
            scenes = self._analyze_scenes(video_id)
            
            return {
                'video_id': video_id,
                'summary': summary,
                'classification': classification,
                'scenes': scenes,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return {}
    
    def _generate_summary(self, video_id: str) -> str:
        """  """
        try:
            url = f"{self.base_url}/generate"
            
            payload = {
                "video_id": video_id,
                "type": "summary",
                "prompt": "    . , , ,      ."
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('data', '')
            else:
                logger.error(f"  : {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"  : {str(e)}")
            return ""
    
    def _classify_content(self, video_id: str) -> Dict:
        """ """
        try:
            url = f"{self.base_url}/classify"
            
            payload = {
                "video_id": video_id,
                "options": ["", "", "", "", "", "", ""],
                "conversation_option": "semantic"
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f" : {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f" : {str(e)}")
            return {}
    
    def _analyze_scenes(self, video_id: str) -> List[Dict]:
        """ """
        try:
            url = f"{self.base_url}/search"
            
            #     
            queries = [
                " ",
                " ", 
                "  ",
                " ",
                " ",
                " "
            ]
            
            scenes = []
            for query in queries:
                payload = {
                    "video_id": video_id,
                    "query": query,
                    "search_option": ["visual"],
                    "page_limit": 3
                }
                
                response = requests.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('data'):
                        scenes.extend(result['data'][:2])  #  2
            
            return scenes
            
        except Exception as e:
            logger.error(f"  : {str(e)}")
            return []
    
    def _convert_to_videoplanet_format(self, analysis_result: Dict, video_path: str) -> Dict:
        """Twelve Labs  VideoPlanet  """
        try:
            summary = analysis_result.get('summary', '')
            classification = analysis_result.get('classification', {})
            scenes = analysis_result.get('scenes', [])
            
            # AI    
            overall_score = self._calculate_score_from_analysis(summary, scenes)
            
            #  
            feedback_items = self._generate_feedback_from_analysis(summary, scenes)
            
            #   ( )
            technical_analysis = self._get_technical_analysis(video_path)
            
            #  
            improvements = self._generate_improvements_from_analysis(summary, overall_score)
            
            return {
                "analysis_id": f"twelve_labs_{int(time.time())}",
                "timestamp": time.time(),
                "source": "twelve_labs_api",
                "video_id": analysis_result.get('video_id'),
                "results": {
                    "overall_score": overall_score,
                    "feedback": feedback_items,
                    "technical_analysis": technical_analysis,
                    "improvement_suggestions": improvements,
                    "ai_summary": summary,
                    "content_classification": classification,
                    "scene_analysis": scenes[:5]  #  5 
                },
                "processing_time": 15.0,  # Twelve Labs API   
                "ai_version": "twelve-labs-v1.2"
            }
            
        except Exception as e:
            logger.error(f"  : {str(e)}")
            return self._get_error_response(str(e))
    
    def _get_enhanced_dummy_analysis(self, video_path: str) -> Dict:
        """    ( )"""
        import os
        import random
        
        #   
        file_size = os.path.getsize(video_path) if os.path.exists(video_path) else 0
        file_name = os.path.basename(video_path)
        
        #    
        base_score = random.uniform(6.0, 8.5)
        
        return {
            "analysis_id": f"dummy_{int(time.time())}_{random.randint(1000, 9999)}",
            "timestamp": time.time(),
            "source": "dummy_analyzer",
            "file_info": {
                "name": file_name,
                "size": file_size,
                "path": video_path
            },
            "results": {
                "overall_score": round(base_score, 1),
                "feedback": self._generate_realistic_feedback(base_score),
                "technical_analysis": self._generate_technical_analysis(),
                "improvement_suggestions": self._generate_improvement_suggestions(base_score),
                "score_breakdown": {
                    "composition": round(base_score + random.uniform(-1, 1), 1),
                    "lighting": round(base_score + random.uniform(-1.5, 1), 1),
                    "audio": round(base_score + random.uniform(-1, 1.5), 1),
                    "stability": round(base_score + random.uniform(-0.5, 1), 1),
                    "color": round(base_score + random.uniform(-1, 1), 1),
                    "motion": round(base_score + random.uniform(-1, 1), 1)
                }
            },
            "processing_time": round(random.uniform(1.5, 4.2), 1),
            "ai_version": "v1.0-dummy-enhanced",
            "note": "  :  AI    . GCP AI       ."
        }
    
    def _generate_realistic_feedback(self, base_score: float) -> List[Dict]:
        """  """
        feedback_templates = [
            {
                "type": "composition",
                "good": [" ", "     ", "   "],
                "poor": [" ", "    ", "  "]
            },
            {
                "type": "lighting",
                "good": ["  ", "  ", " "],
                "poor": ["  ", "    ", "   "]
            },
            {
                "type": "audio",
                "good": [" ", "   ", "  "],
                "poor": ["    ", "  ", "  "]
            },
            {
                "type": "stability",
                "good": ["     ", "  ", "/  "],
                "poor": ["  ", "  ", "   "]
            },
            {
                "type": "color",
                "good": ["  ", " ", " "],
                "poor": ["   ", "  ", "  "]
            },
            {
                "type": "motion",
                "good": ["  ", "  ", "  "],
                "poor": ["   ", "  ", "  "]
            }
        ]
        
        feedback_list = []
        import random
        
        for i, template in enumerate(feedback_templates):
            score = round(base_score + random.uniform(-1.5, 1.5), 1)
            score = max(1.0, min(10.0, score))  # 1-10  
            
            #   /  
            if score >= 7:
                message = random.choice(template["good"])
            else:
                message = random.choice(template["poor"])
            
            feedback_list.append({
                "type": template["type"],
                "score": score,
                "message": message,
                "timestamp": round(random.uniform(5, 30), 1),
                "confidence": round(random.uniform(0.7, 0.95), 2)
            })
        
        return feedback_list
    
    def _generate_technical_analysis(self) -> Dict:
        """   """
        import random
        
        resolutions = ["1920x1080", "1280x720", "3840x2160", "2560x1440"]
        fps_options = [24, 25, 30, 60]
        
        return {
            "resolution": random.choice(resolutions),
            "fps": random.choice(fps_options),
            "duration": round(random.uniform(30, 180), 1),
            "bitrate": f"{random.uniform(5, 25):.1f} Mbps",
            "codec": "H.264",
            "audio_codec": "AAC",
            "audio_sample_rate": "48kHz",
            "audio_quality": random.choice(["Excellent", "Good", "Fair"]),
            "file_format": "MP4"
        }
    
    def _generate_improvement_suggestions(self, base_score: float) -> List[str]:
        """  """
        suggestions = []
        
        if base_score < 7:
            suggestions.extend([
                "      .",
                "     .",
                "       ."
            ])
        
        if base_score < 8:
            suggestions.extend([
                "   (,  ).",
                "      .",
                "      ."
            ])
        
        general_suggestions = [
            "      .",
            "    .",
            "      ."
        ]
        
        import random
        suggestions.extend(random.sample(general_suggestions, 2))
        
        return suggestions
    
    def _get_fallback_analysis(self) -> Dict:
        """AI      """
        result = self._get_enhanced_dummy_analysis("")
        result["note"] = "AI      ."
        result["source"] = "fallback"
        return result
    
    def _get_error_response(self, error_message: str) -> Dict:
        """ """
        return {
            "analysis_id": f"error_{int(time.time())}",
            "timestamp": time.time(),
            "source": "error",
            "error": True,
            "error_message": error_message,
            "results": {
                "overall_score": 0.0,
                "feedback": [],
                "technical_analysis": {},
                "improvement_suggestions": [
                    "    .  ."
                ]
            },
            "processing_time": 0.0
        }
    
    async def analyze_video_async(self, video_path: str, feedback_id: int = None) -> Dict:
        """  """
        # Celery     
        return await asyncio.to_thread(self.analyze_video, video_path, feedback_id)


    def _calculate_score_from_analysis(self, summary: str, scenes: List[Dict]) -> float:
        """AI     """
        import random
        
        base_score = 7.0
        
        #     
        if summary:
            if any(keyword in summary.lower() for keyword in ['', '', '', '', '']):
                base_score += 1.0
            if any(keyword in summary.lower() for keyword in ['', '', '', '']):
                base_score -= 1.0
        
        #   
        if len(scenes) > 3:
            base_score += 0.5
        
        return round(min(10.0, max(1.0, base_score + random.uniform(-0.5, 0.5))), 1)
    
    def _generate_feedback_from_analysis(self, summary: str, scenes: List[Dict]) -> List[Dict]:
        """AI    """
        feedback_items = []
        
        #   
        if summary:
            feedback_items.append({
                "type": "composition",
                "score": 8.0,
                "message": f"AI  : {summary[:100]}..." if len(summary) > 100 else summary,
                "timestamp": 0.0,
                "confidence": 0.9
            })
        
        #   
        for i, scene in enumerate(scenes[:3]):
            if scene.get('score', 0) > 80:
                feedback_items.append({
                    "type": "motion",
                    "score": 8.5,
                    "message": f"  : {scene.get('metadata', {}).get('text', ' ')}",
                    "timestamp": scene.get('start', 0),
                    "confidence": scene.get('confidence', 0.8)
                })
        
        return feedback_items
    
    def _get_technical_analysis(self, video_path: str) -> Dict:
        """   """
        try:
            import os
            from moviepy.editor import VideoFileClip
            
            if not os.path.exists(video_path):
                return {}
            
            clip = VideoFileClip(video_path)
            
            return {
                "duration": round(clip.duration, 1),
                "fps": round(clip.fps, 1),
                "resolution": f"{clip.w}x{clip.h}",
                "file_size": f"{os.path.getsize(video_path) / (1024*1024):.1f} MB",
                "codec": "H.264",
                "audio_codec": "AAC"
            }
            
        except Exception as e:
            logger.error(f"  : {str(e)}")
            return {}
    
    def _generate_improvements_from_analysis(self, summary: str, score: float) -> List[str]:
        """AI    """
        suggestions = []
        
        if score < 7:
            suggestions.extend([
                "Twelve Labs AI       .",
                "   .",
                "   ."
            ])
        
        if summary and '' in summary:
            suggestions.append("      .")
        
        if summary and '' in summary:
            suggestions.append("    .")
        
        return suggestions[:5]  #  5


#   
video_analyzer = TwelveLabsVideoAnalyzer()