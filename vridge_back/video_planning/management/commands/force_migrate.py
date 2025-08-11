from django.core.management.base import BaseCommand
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Force apply video_planning migrations'

    def handle(self, *args, **options):
        self.stdout.write(' video_planning    ...')
        
        try:
            #   
            self.stdout.write('\n  :')
            call_command('showmigrations', 'video_planning')
            
            #  
            self.stdout.write('\n  ...')
            call_command('migrate', 'video_planning', verbosity=2)
            
            self.stdout.write(self.style.SUCCESS('\n  !'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n  : {e}'))
            logger.error(f"Force migration failed: {e}", exc_info=True)