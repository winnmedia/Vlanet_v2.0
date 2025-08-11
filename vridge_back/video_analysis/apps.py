from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class VideoAnalysisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'video_analysis'
    verbose_name = 'AI  '

    def ready(self):
        """   """
        try:
            #      
            #    
            logger.info("Video analysis app ready (using lazy loading)")
        except Exception as e:
            logger.error(f"Error in video_analysis app initialization: {e}")
            #       