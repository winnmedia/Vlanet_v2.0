#!/usr/bin/env python3
import os
import sys
import django

# Django 
sys.path.insert(0, '/home/winnmedia/VideoPlanet/vridge_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')
django.setup()

from video_planning.models import VideoPlanning
from users.models import User

try:
    #   
    user = User.objects.get(username='ceo@winnmedia.co.kr')
    print(f" : {user.username}")
    
    #   
    planning = VideoPlanning.objects.create(
        user=user,
        title=' ',
        planning_text='  ',
        stories=[],
        scenes=[],
        shots=[],
        storyboards=[]
    )
    print(f"  ! ID: {planning.id}")
    
    #   
    saved_planning = VideoPlanning.objects.get(id=planning.id)
    print(f"  : {saved_planning.title}")
    
except Exception as e:
    print(f" : {e}")
    import traceback
    traceback.print_exc()