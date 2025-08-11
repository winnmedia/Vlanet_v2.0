import os
import logging
import time
from typing import Dict, List, Optional, Any
from django.conf import settings
from twelvelabs import TwelveLabs
from twelvelabs.models.task import Task

logger = logging.getLogger(__name__)


class TwelveLabsService:
    """
    Twelve Labs API    
    """
    
    def __init__(self):
        api_key = getattr(settings, 'TWELVE_LABS_API_KEY', None) or os.environ.get('TWELVE_LABS_API_KEY')
        if not api_key:
            raise ValueError("TWELVE_LABS_API_KEY not found in settings or environment variables")
        
        self.client = TwelveLabs(api_key=api_key)
        self.default_index_id = None
        
        #     
        self._ensure_default_index()
    
    def _ensure_default_index(self):
        """     """
        try:
            #    
            indexes = self.client.index.list()
            
            if indexes and len(indexes) > 0:
                # VideoPlanet  
                for index in indexes:
                    if index.name == "videoplanet_videos":
                        self.default_index_id = index.id
                        logger.info(f"Using existing index: {index.name} (ID: {index.id})")
                        return
                
                # VideoPlanet      
                self.default_index_id = indexes[0].id
                logger.info(f"Using first available index: {indexes[0].name} (ID: {indexes[0].id})")
            else:
                #    
                self._create_default_index()
                
        except Exception as e:
            logger.error(f"Error checking indexes: {e}")
            #   
            self._create_default_index()
    
    def _create_default_index(self):
        """  """
        try:
            index = self.client.index.create(
                name="videoplanet_videos",
                engines=[
                    {
                        "name": "marengo2.6",
                        "options": ["visual", "conversation", "text_in_video", "logo"]
                    }
                ],
                addons=["thumbnail"]  #   
            )
            self.default_index_id = index.id
            logger.info(f"Created new index: videoplanet_videos (ID: {index.id})")
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            raise
    
    def upload_video(self, video_url: str, video_name: str, metadata: Dict = None) -> Dict:
        """
         Twelve Labs  
        
        Args:
            video_url:  URL
            video_name:  
            metadata:  
            
        Returns:
              
        """
        try:
            if not self.default_index_id:
                raise ValueError("No default index available")
            
            #    
            task = self.client.task.create(
                index_id=self.default_index_id,
                url=video_url,
                name=video_name,
                metadata=metadata or {}
            )
            
            logger.info(f"Video upload task created: {task.id}")
            
            #   
            task_result = self._wait_for_task_completion(task.id)
            
            return {
                "success": True,
                "task_id": task.id,
                "video_id": task_result.video_id if task_result else None,
                "status": task_result.status if task_result else "unknown",
                "metadata": task_result.metadata if task_result else {}
            }
            
        except Exception as e:
            logger.error(f"Failed to upload video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _wait_for_task_completion(self, task_id: str, timeout: int = 600) -> Optional[Task]:
        """  """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                task = self.client.task.retrieve(task_id)
                
                if task.status == "ready":
                    logger.info(f"Task {task_id} completed successfully")
                    return task
                elif task.status == "failed":
                    logger.error(f"Task {task_id} failed")
                    return task
                
                #   
                if hasattr(task, 'progress'):
                    logger.info(f"Task {task_id} progress: {task.progress}%")
                
                time.sleep(5)  # 5 
                
            except Exception as e:
                logger.error(f"Error checking task status: {e}")
                time.sleep(5)
        
        logger.error(f"Task {task_id} timed out after {timeout} seconds")
        return None
    
    def analyze_video(self, video_id: str) -> Dict:
        """
          
        
        Args:
            video_id: Twelve Labs  ID
            
        Returns:
             
        """
        try:
            #   
            video = self.client.video.retrieve(
                index_id=self.default_index_id,
                id=video_id
            )
            
            #   
            summary = self._generate_summary(video_id)
            
            #   
            key_moments = self._extract_key_moments(video_id)
            
            #   (OCR)
            text_in_video = self._extract_text_in_video(video_id)
            
            #  
            conversations = self._analyze_conversations(video_id)
            
            return {
                "success": True,
                "video_info": {
                    "id": video.id,
                    "name": video.metadata.get("name", ""),
                    "duration": video.metadata.get("duration", 0),
                    "fps": video.metadata.get("fps", 0),
                    "width": video.metadata.get("width", 0),
                    "height": video.metadata.get("height", 0)
                },
                "analysis": {
                    "summary": summary,
                    "key_moments": key_moments,
                    "text_in_video": text_in_video,
                    "conversations": conversations
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_summary(self, video_id: str) -> Dict:
        """  """
        try:
            response = self.client.generate.summarize(
                video_id=video_id,
                type="summary"
            )
            
            return {
                "text": response.summary,
                "chapters": response.chapters if hasattr(response, 'chapters') else []
            }
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return {"text": "", "chapters": []}
    
    def _extract_key_moments(self, video_id: str, limit: int = 10) -> List[Dict]:
        """  """
        try:
            #    
            response = self.client.search.query(
                index_id=self.default_index_id,
                query="important moments key scenes highlights",
                options=["visual"],
                filter={"video_id": [video_id]},
                page_limit=limit
            )
            
            moments = []
            for result in response.data:
                moments.append({
                    "start_time": result.start,
                    "end_time": result.end,
                    "confidence": result.confidence,
                    "thumbnail_url": result.thumbnail_url if hasattr(result, 'thumbnail_url') else None
                })
            
            return moments
            
        except Exception as e:
            logger.error(f"Failed to extract key moments: {e}")
            return []
    
    def _extract_text_in_video(self, video_id: str) -> List[Dict]:
        """    (OCR)"""
        try:
            response = self.client.search.query(
                index_id=self.default_index_id,
                query="text",
                options=["text_in_video"],
                filter={"video_id": [video_id]},
                page_limit=20
            )
            
            texts = []
            for result in response.data:
                if hasattr(result, 'text'):
                    texts.append({
                        "text": result.text,
                        "start_time": result.start,
                        "end_time": result.end,
                        "confidence": result.confidence
                    })
            
            return texts
            
        except Exception as e:
            logger.error(f"Failed to extract text: {e}")
            return []
    
    def _analyze_conversations(self, video_id: str) -> List[Dict]:
        """ """
        try:
            response = self.client.search.query(
                index_id=self.default_index_id,
                query="conversation dialogue speech",
                options=["conversation"],
                filter={"video_id": [video_id]},
                page_limit=50
            )
            
            conversations = []
            for result in response.data:
                if hasattr(result, 'transcript'):
                    conversations.append({
                        "transcript": result.transcript,
                        "start_time": result.start,
                        "end_time": result.end,
                        "speaker": result.speaker if hasattr(result, 'speaker') else None
                    })
            
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to analyze conversations: {e}")
            return []
    
    def search_in_videos(self, query: str, options: List[str] = None, limit: int = 10) -> List[Dict]:
        """
          
        
        Args:
            query:  
            options:   ["visual", "conversation", "text_in_video", "logo"]
            limit:   
            
        Returns:
              
        """
        try:
            if not options:
                options = ["visual", "conversation", "text_in_video"]
            
            response = self.client.search.query(
                index_id=self.default_index_id,
                query=query,
                options=options,
                page_limit=limit
            )
            
            results = []
            for result in response.data:
                results.append({
                    "video_id": result.video_id,
                    "start_time": result.start,
                    "end_time": result.end,
                    "confidence": result.confidence,
                    "thumbnail_url": result.thumbnail_url if hasattr(result, 'thumbnail_url') else None,
                    "metadata": result.metadata if hasattr(result, 'metadata') else {}
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search videos: {e}")
            return []
    
    def delete_video(self, video_id: str) -> bool:
        """ """
        try:
            self.client.video.delete(
                index_id=self.default_index_id,
                id=video_id
            )
            logger.info(f"Video {video_id} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete video: {e}")
            return False