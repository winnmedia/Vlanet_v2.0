"""
App configuration for AI Video Generation
"""
from django.apps import AppConfig


class AiVideoConfig(AppConfig):
    """Configuration for AI Video app"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_video'
    verbose_name = 'AI Video Generation'
    
    def ready(self):
        """Initialize app when Django starts"""
        # Import signal handlers if any
        try:
            from . import signals
        except ImportError:
            pass