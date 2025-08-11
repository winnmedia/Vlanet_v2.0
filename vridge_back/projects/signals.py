from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import DevelopmentFramework

User = get_user_model()

@receiver(post_save, sender=User)
def create_default_framework(sender, instance, created, **kwargs):
    """       """
    if created:
        #     
        if not DevelopmentFramework.objects.filter(user=instance).exists():
            DevelopmentFramework.objects.create(
                user=instance,
                name='  ',
                intro_hook=' 5 !      .  ,  ,      .',
                immersion='     . 2-3  ,     .     .',
                twist='     .  ,   ,        .',
                hook_next='       . " ..."  "  ..."    .',
                is_default=True
            )