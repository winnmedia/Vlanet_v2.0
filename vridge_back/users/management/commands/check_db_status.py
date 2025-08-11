from django.core.management.base import BaseCommand
from django.db import connection
from projects.models import Project, Members, ProjectInvitation
from users.models import User
import traceback


class Command(BaseCommand):
    help = '    '

    def handle(self, *args, **options):
        try:
            #   
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS("   "))
            
            #    
            self.stdout.write("\n===    ===")
            self.stdout.write(f"User: {User.objects.count()}")
            self.stdout.write(f"Project: {Project.objects.count()}")
            self.stdout.write(f"Members: {Members.objects.count()}")
            
            # ProjectInvitation  
            try:
                count = ProjectInvitation.objects.count()
                self.stdout.write(f"ProjectInvitation: {count}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"ProjectInvitation : {str(e)}"))
            
            #    
            self.stdout.write("\n===    ===")
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE '%project%'
                    ORDER BY table_name
                """)
                tables = cursor.fetchall()
                for table in tables:
                    self.stdout.write(f" {table[0]}")
            
            #   
            self.stdout.write("\n===   ===")
            from django.db.migrations.recorder import MigrationRecorder
            recorder = MigrationRecorder(connection)
            applied = recorder.applied_migrations()
            
            project_migrations = [m for m in applied if m[0] == 'projects']
            self.stdout.write(f"projects  : {len(project_migrations)} ")
            
            if project_migrations:
                latest = max(project_migrations, key=lambda x: x[1])
                self.stdout.write(f" : {latest[1]}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n :"))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))