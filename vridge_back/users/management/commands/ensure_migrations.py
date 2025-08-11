"""
Django  : ensure_migrations
   .
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection

class Command(BaseCommand):
    help = '   '

    def handle(self, *args, **options):
        self.stdout.write('  ...')
        
        #  
        apps_order = [
            'contenttypes',
            'auth', 
            'users',
            'projects',
            'feedbacks',
            'video_planning',
            'video_analysis',
            'admin',
            'sessions',
        ]
        
        #    
        for app in apps_order:
            try:
                self.stdout.write(f' {app}  ...')
                call_command('migrate', app, verbosity=0)
                self.stdout.write(self.style.SUCCESS(f' {app} '))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  {app} : {e}'))
                continue
        
        #  
        try:
            self.stdout.write('   ...')
            call_command('migrate', verbosity=0)
            self.stdout.write(self.style.SUCCESS('   '))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'    : {e}'))
        
        #  
        self.verify_tables()
        
    def verify_tables(self):
        """  """
        self.stdout.write('\n   :')
        
        critical_tables = [
            'django_migrations',
            'auth_user',
            'users_user',
            'projects_project',
            'feedbacks_feedback',
        ]
        
        with connection.cursor() as cursor:
            for table in critical_tables:
                try:
                    cursor.execute(f"SELECT 1 FROM {table} LIMIT 1")
                    self.stdout.write(f'    {table}')
                except:
                    self.stdout.write(self.style.ERROR(f'    {table}'))
        
        self.stdout.write(self.style.SUCCESS('\n   !'))