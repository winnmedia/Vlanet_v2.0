from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = ""
    
    def ready(self):
        """     """
        try:
            from .email_queue import start_email_queue
            start_email_queue()
        except ImportError:
            pass  # email_queue   
