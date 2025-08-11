from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from users.models import User


class Command(BaseCommand):
    help = '  '

    def handle(self, *args, **options):
        try:
            #   
            user = User.objects.filter(username='test@videoplanet.com').first()
            
            if user:
                #  
                user.set_password('test1234')
                user.is_active = True
                user.email_verified = True
                user.email_verified_at = timezone.now()
                user.save()
                self.stdout.write(self.style.SUCCESS('    '))
            else:
                #   
                user = User.objects.create(
                    username='test@videoplanet.com',
                    email='test@videoplanet.com',
                    nickname='',
                    is_active=True,
                    email_verified=True,
                    email_verified_at=timezone.now(),
                    login_method='email'
                )
                user.set_password('test1234')
                user.save()
                self.stdout.write(self.style.SUCCESS('    '))
            
            self.stdout.write(f': {user.email}')
            self.stdout.write(f': test1234')
            self.stdout.write(f': {user.is_active}')
            self.stdout.write(f' : {user.email_verified}')
            
            #  
            from django.db import connection
            self.stdout.write(f'\n: {connection.vendor}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f' : {e}'))
            import traceback
            traceback.print_exc()