from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User


class Command(BaseCommand):
    help = '     '

    def handle(self, *args, **options):
        try:
            #   False   
            users_to_fix = User.objects.filter(email_verified=False)
            count = users_to_fix.count()
            
            if count > 0:
                self.stdout.write(f'   {count} ')
                
                #      
                users_to_fix.update(
                    email_verified=True,
                    email_verified_at=timezone.now()
                )
                
                self.stdout.write(self.style.SUCCESS(f'{count}    '))
            else:
                self.stdout.write('    ')
            
            #    
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            verified_users = User.objects.filter(email_verified=True).count()
            
            self.stdout.write(f'\n : {total_users}')
            self.stdout.write(f' : {active_users}')
            self.stdout.write(f'  : {verified_users}')
            
            #   
            sample_users = User.objects.all()[:5]
            if sample_users:
                self.stdout.write('\n :')
                for user in sample_users:
                    self.stdout.write(f'- {user.username} (active: {user.is_active}, verified: {user.email_verified})')
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f' : {e}'))
            import traceback
            traceback.print_exc()