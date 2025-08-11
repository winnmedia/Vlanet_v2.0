"""
Lazy loading wrapper for video analyzer
      
"""
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class LazyVideoAnalyzer:
    """
         
        
    """
    
    def __init__(self):
        self._analyzer = None
        self._initialization_error = None
    
    @property
    def analyzer(self):
        """    ( )"""
        if self._analyzer is None and self._initialization_error is None:
            try:
                from .analyzer import TwelveLabsVideoAnalyzer
                self._analyzer = TwelveLabsVideoAnalyzer()
                logger.info("Video analyzer initialized successfully")
            except Exception as e:
                self._initialization_error = e
                logger.error(f"Failed to initialize video analyzer: {e}")
                #   Mock  
                if self._is_development():
                    from .mock_analyzer import MockVideoAnalyzer
                    self._analyzer = MockVideoAnalyzer()
                    logger.info("Using mock analyzer for development")
        
        if self._initialization_error and not self._analyzer:
            raise self._initialization_error
        
        return self._analyzer
    
    def _is_development(self):
        """  """
        from django.conf import settings
        return settings.DEBUG or not hasattr(settings, 'TWELVELABS_API_KEY')
    
    def __getattr__(self, name):
        """  """
        return getattr(self.analyzer, name)
    
    def is_available(self):
        """    """
        try:
            return self.analyzer is not None
        except:
            return False


#     
video_analyzer = LazyVideoAnalyzer()


@lru_cache(maxsize=1)
def get_video_analyzer():
    """
        
    Django     
    """
    return video_analyzer