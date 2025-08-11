from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import DevelopmentFramework

User = get_user_model()

class Command(BaseCommand):
    help = '    '

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='  ID  ',
        )

    def handle(self, *args, **options):
        default_framework_data = {
            'name': '  ',
            'intro_hook': ' 5 !      .  ,  ,      .',
            'immersion': '     . 2-3  ,     .     .',
            'twist': '     .  ,   ,        .',
            'hook_next': '       . " ..."  "  ..."    .',
            'is_default': True
        }

        user_id = options.get('user_id')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                users = [user]
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f' ID {user_id}   .'))
                return
        else:
            users = User.objects.all()

        created_count = 0
        for user in users:
            #     
            if DevelopmentFramework.objects.filter(user=user).exists():
                self.stdout.write(f' {user.username}    .')
                continue
            
            #   
            framework = DevelopmentFramework.objects.create(
                user=user,
                **default_framework_data
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f' {user.username}   .'))

        self.stdout.write(self.style.SUCCESS(f' {created_count}   .'))