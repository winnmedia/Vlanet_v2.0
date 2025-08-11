"""
  Mock Video Analyzer
 API  / 
"""
import logging
from typing import Dict, List, Optional
import random

logger = logging.getLogger(__name__)


class MockVideoAnalyzer:
    """  Mock  """
    
    def __init__(self):
        logger.info("Mock Video Analyzer initialized")
        self.api_key = "mock_api_key"
    
    async def analyze_video(self, video_path: str, analysis_type: str = "comprehensive") -> Dict:
        """Mock  """
        logger.info(f"Mock analyzing video: {video_path} with type: {analysis_type}")
        
        return {
            "status": "completed",
            "analysis_type": analysis_type,
            "duration": 120.5,
            "results": {
                "technical_quality": {
                    "overall_score": 85,
                    "video_quality": 90,
                    "audio_quality": 80,
                    "stability": 85
                },
                "content_analysis": {
                    "scene_count": 15,
                    "dominant_colors": ["blue", "white", "gray"],
                    "detected_objects": ["person", "computer", "desk"],
                    "mood": "professional"
                },
                "suggestions": [
                    "    .",
                    "          .",
                    "          ."
                ]
            }
        }
    
    def get_analysis_status(self, task_id: str) -> Dict:
        """Mock   """
        return {
            "task_id": task_id,
            "status": "completed",
            "progress": 100
        }
    
    def create_index(self, index_name: str) -> Dict:
        """Mock  """
        return {
            "index_id": f"mock_index_{index_name}",
            "status": "created"
        }
    
    def upload_video(self, index_id: str, video_path: str) -> Dict:
        """Mock  """
        return {
            "video_id": f"mock_video_{random.randint(1000, 9999)}",
            "status": "uploaded",
            "duration": 120.5
        }
    
    def search_in_video(self, index_id: str, query: str) -> List[Dict]:
        """Mock   """
        return [
            {
                "timestamp": 10.5,
                "confidence": 0.95,
                "text": f"Found '{query}' in the video",
                "context": "This is a mock search result"
            }
        ]
    
    def generate_summary(self, video_id: str) -> str:
        """Mock   """
        return "   .   AI      ."
    
    def extract_highlights(self, video_id: str, num_highlights: int = 3) -> List[Dict]:
        """Mock  """
        return [
            {
                "start_time": i * 30,
                "end_time": (i + 1) * 30,
                "confidence": 0.9 - i * 0.1,
                "description": f"  {i + 1}"
            }
            for i in range(num_highlights)
        ]