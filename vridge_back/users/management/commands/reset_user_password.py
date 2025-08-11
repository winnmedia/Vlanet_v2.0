from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from users.models import User


class Command(BaseCommand):
    help = '   '

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help=' ')
        parser.add_argument('password', type=str, help=' ')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        
        try:
            #   username  
            user = User.objects.filter(username=email).first()
            if not user:
                user = User.objects.filter(email=email).first()
            
            if user:
                user.set_password(password)
                user.is_active = True
                user.email_verified = True
                user.save()
                
                self.stdout.write(self.style.SUCCESS(f'  : {user.username}'))
                self.stdout.write(f': {user.email}')
                self.stdout.write(f' : {password}')
            else:
                self.stdout.write(self.style.ERROR(f'   : {email}'))
                
                #    
                all_users = User.objects.all()[:10]
                self.stdout.write('\n  :')
                for u in all_users:
                    self.stdout.write(f'- {u.username} ({u.email})')
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f' : {e}'))
            import traceback
            traceback.print_exc()