#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
     Django management command
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from users.models import User
from projects.models import Project, Members
from feedbacks.models import FeedBack
import json


class Command(BaseCommand):
    help = '    '

    def handle(self, *args, **options):
        self.stdout.write("    ...")
        
        #   
        demo_accounts = [
            {
                "email": "test1@videoplanet.com",
                "nickname": " ",
                "password": "Test1234!@#$",
                "description": "   "
            },
            {
                "email": "test2@videoplanet.com", 
                "nickname": " ",
                "password": "Test1234!@#$",
                "description": "   "
            },
            {
                "email": "test3@videoplanet.com",
                "nickname": " ",
                "password": "Test1234!@#$", 
                "description": "   "
            }
        ]
        
        created_users = []
        
        #  
        for account in demo_accounts:
            try:
                user, created = User.objects.get_or_create(
                    username=account["email"],
                    defaults={
                        'nickname': account["nickname"],
                        'password': make_password(account["password"]),
                        'login_method': 'email'
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"  : {account['email']}")
                    )
                    created_users.append(user)
                else:
                    self.stdout.write(
                        self.style.WARNING(f"   : {account['email']}")
                    )
                    created_users.append(user)
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   {account['email']}: {e}")
                )
        
        #   
        if created_users:
            self.stdout.write("\n   ...")
            
            for i, user in enumerate(created_users[:2], 1):
                try:
                    project, created = Project.objects.get_or_create(
                        project_name=f"  {i}",
                        defaults={
                            'client_name': f"  {i}",
                            'budget': '1000000',
                            'project_status': 'wait',
                            'project_description': f'   {i}'
                        }
                    )
                    
                    if created:
                        #   
                        Members.objects.get_or_create(
                            project=project,
                            user=user,
                            role='project_manager'
                        )
                        
                        #  
                        feedback = FeedBack.objects.create(
                            project=project,
                            feedback_name=f"  {i}",
                            feedback_round=1,
                            feedback_description="  "
                        )
                        
                        self.stdout.write(
                            self.style.SUCCESS(f"  : {project.project_name}")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"    : {project.project_name}")
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"   : {e}")
                    )
        
        #   
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("   "))
        self.stdout.write("="*60)
        
        for account in demo_accounts:
            self.stdout.write(f"\n: {account['email']}")
            self.stdout.write(f": {account['password']}")
            self.stdout.write(f": {account['description']}")
            self.stdout.write("-"*40)
        
        self.stdout.write("\n" + self.style.WARNING("  :"))
        self.stdout.write("-     ")
        self.stdout.write("-       ")
        self.stdout.write("-   ''  \n")