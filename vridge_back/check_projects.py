#!/usr/bin/env python3
import os
import sys
import django

# Django 
sys.path.insert(0, '/home/winnmedia/VideoPlanet/vridge_back')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')
django.setup()

from projects.models import Project
from users.models import User

try:
    #   
    all_projects = Project.objects.all()
    print(f"  : {all_projects.count()}")
    
    for project in all_projects:
        print(f"\n: {project.name} (ID: {project.id})")
        print(f"  - : {project.user.email if project.user else 'None'}")
        print(f"  - : {project.created}")
        print(f"  - : {project.manager}")
        print(f"  - : {project.consumer}")
    
    # CEO   
    user = User.objects.filter(username="ceo@winnmedia.co.kr").first()
    if user:
        user_projects = user.projects.all()
        print(f"\n\nceo@winnmedia.co.kr  : {user_projects.count()}")
        for project in user_projects:
            print(f"  - {project.name} (ID: {project.id})")
            
except Exception as e:
    print(f" : {e}")
    import traceback
    traceback.print_exc()