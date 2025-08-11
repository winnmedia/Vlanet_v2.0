#!/usr/bin/env python3
"""
Django      
VideoPlanning/Calendar/ProjectCreate/feedback API  
"""

import json
import os
import requests
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any, List

class ModelGenerator:
    def __init__(self, base_url="https://videoplanet.up.railway.app"):
        self.base_url = base_url
        self.models = {}
        self.api_endpoints = []
        
    def analyze_existing_apis(self):
        """  URL   API  """
        # VideoPlanning  API
        video_planning_apis = [
            "/api/video-planning/generate/structure/",
            "/api/video-planning/generate/story/", 
            "/api/video-planning/generate/scenes/",
            "/api/video-planning/generate/shots/",
            "/api/video-planning/generate/storyboards/",
            "/api/video-planning/save/",
            "/api/video-planning/list/",
            "/api/video-planning/recent/"
        ]
        
        # Projects  API  
        project_apis = [
            "/api/projects/",
            "/api/projects/list/",
            "/api/projects/create/",
            "/api/projects/atomic-create/"
        ]
        
        # Feedbacks  API
        feedback_apis = [
            "/api/feedbacks/",
            "/api/feedbacks/list/",
            "/api/feedbacks/create/"
        ]
        
        # Users  API
        user_apis = [
            "/api/users/profile/",
            "/api/users/login/",
            "/api/users/register/"
        ]
        
        # Video Analysis  API
        video_analysis_apis = [
            "/api/video-analysis/analyze/",
            "/api/video-analysis/result/",
            "/api/video-analysis/teacher/"
        ]
        
        self.api_endpoints = (video_planning_apis + project_apis + 
                            feedback_apis + user_apis + video_analysis_apis)
        
    def get_sample_data(self):
        """    """
        sample_data = {
            "VideoPlanning": {
                "id": 1,
                "title": "  ",
                "planning_text": "  .       .",
                "stories": [
                    {
                        "title": "",
                        "summary": "  .",
                        "stage": "",
                        "stage_name": ""
                    }
                ],
                "selected_story": {
                    "title": " ",
                    "summary": "  "
                },
                "scenes": [
                    {
                        "location": "", 
                        "time_of_day": "",
                        "description": "  ",
                        "characters": ["", ""],
                        "mood": ""
                    }
                ],
                "shots": [
                    {
                        "shot_size": "",
                        "description": " ",
                        "camera_angle": "",
                        "duration": "3"
                    }
                ],
                "storyboards": [
                    {
                        "description": " ",
                        "image_url": "https://example.com/image.png",
                        "frame_number": 1
                    }
                ],
                "is_completed": False,
                "current_step": 1,
                "created_at": "2023-12-07T10:00:00Z",
                "updated_at": "2023-12-07T10:00:00Z"
            },
            
            "Project": {
                "id": 1,
                "name": " ",
                "manager": " ",
                "consumer": "",
                "description": " .     .",
                "color": "#4318FF",
                "tone_manner": " ",
                "genre": " ",
                "concept": " ",
                "created": "2023-12-07T10:00:00Z",
                "updated": "2023-12-07T10:00:00Z"
            },
            
            "Feedback": {
                "id": 1,
                "title": " ",
                "url": "https://example.com/video.mp4",
                "description": " .      .",
                "status": "active",
                "is_public": True,
                "created_at": "2023-12-07T10:00:00Z"
            },
            
            "User": {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "first_name": "",
                "last_name": "",
                "is_active": True,
                "is_staff": False,
                "date_joined": "2023-12-07T10:00:00Z"
            },
            
            "VideoAnalysisResult": {
                "id": 1,
                "video_id": "12345",
                "analysis_status": "completed",
                "twelve_labs_video_id": "tl_video_123",
                "index_id": "idx_123",
                "analysis_data": {
                    "summary": "  ",
                    "highlights": ["  1", "  2"],
                    "transcript": "  "
                },
                "created_at": "2023-12-07T10:00:00Z"
            },
            
            "AIFeedbackItem": {
                "id": 1,
                "feedback_type": "technical",
                "confidence": 0.95,
                "teacher_personality": "professional",
                "feedback_content": "AI   .",
                "created_at": "2023-12-07T10:00:00Z"
            },
            
            "IdempotencyRecord": {
                "id": 1,
                "idempotency_key": "unique_key_123",
                "project_id": 1,
                "request_data": "  JSON",
                "status": "completed",
                "created_at": "2023-12-07T10:00:00Z"
            }
        }
        return sample_data
        
    def infer_field_type(self, key: str, value: Any) -> str:
        """   Django   """
        if isinstance(value, bool):
            return "models.BooleanField(default=False)"
        elif isinstance(value, int):
            if key in ['id', 'pk']:
                return "models.AutoField(primary_key=True)"
            return "models.IntegerField(null=True, blank=True)"
        elif isinstance(value, float):
            return "models.FloatField(null=True, blank=True)"
        elif isinstance(value, str):
            if key in ['created_at', 'updated_at', 'date_joined']:
                return "models.DateTimeField(auto_now_add=True)"
            elif key == 'updated_at':
                return "models.DateTimeField(auto_now=True)"
            elif 'email' in key.lower():
                return "models.EmailField(max_length=254, null=True, blank=True)"
            elif 'url' in key.lower():
                return "models.URLField(max_length=500, null=True, blank=True)"
            elif len(str(value)) > 255:
                return "models.TextField(null=True, blank=True)"
            else:
                return "models.CharField(max_length=255, null=True, blank=True)"
        elif isinstance(value, (list, dict)):
            return "models.JSONField(default=dict, null=True, blank=True)"
        else:
            return "models.JSONField(default=dict, null=True, blank=True)"
    
    def generate_models(self):
        """   Django  """
        sample_data = self.get_sample_data()
        
        for model_name, fields_data in sample_data.items():
            fields = {}
            for key, value in fields_data.items():
                if key != 'id':  # id  
                    fields[key] = self.infer_field_type(key, value)
            self.models[model_name] = fields
            
    def write_models_file(self):
        """models_from_spec.py  """
        output_path = Path("app")
        output_path.mkdir(exist_ok=True)
        
        models_content = '''"""
VideoPlanning/Calendar/ProjectCreate/Feedback API   Django 
"""
from django.db import models
from django.contrib.auth.models import User

'''
        
        for model_name, fields in self.models.items():
            models_content += f"\nclass {model_name}FromSpec(models.Model):\n"
            models_content += f'    """API    {model_name} """\n'
            
            # id  Django   
            for field_name, field_type in fields.items():
                models_content += f"    {field_name} = {field_type}\n"
            
            models_content += f"\n    class Meta:\n"
            models_content += f"        db_table = '{model_name.lower()}_from_spec'\n"
            models_content += f"        verbose_name = '{model_name} (API )'\n"
            models_content += f"        verbose_name_plural = '{model_name}s (API )'\n"
            models_content += f"        ordering = ['-id']\n"
            
            models_content += f"\n    def __str__(self):\n"
            if 'title' in fields:
                models_content += f"        return self.title or str(self.pk)\n"
            elif 'name' in fields:
                models_content += f"        return self.name or str(self.pk)\n"
            else:
                models_content += f"        return f'{model_name}({{self.pk}})'\n"
            
            models_content += "\n"
            
        models_file = output_path / "models_from_spec.py"
        models_file.write_text(models_content)
        print(f"   : {models_file}")
        
    def write_migration_files(self):
        """  """
        output_dir = Path("migrations_from_spec")
        output_dir.mkdir(exist_ok=True)
        
        # __init__.py  
        (output_dir / "__init__.py").write_text("")
        
        migration_number = 1
        for model_name, fields in self.models.items():
            migration_content = f'''# Generated migration for {model_name}FromSpec
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    
    operations = [
        migrations.CreateModel(
            name='{model_name}FromSpec',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
'''
            
            for field_name, field_type in fields.items():
                migration_content += f"                ('{field_name}', {field_type}),\n"
            
            migration_content += '''            ],
            options={
                'db_table': \'''' + model_name.lower() + '''_from_spec\',
                'verbose_name': \'''' + model_name + ''' (API )\',
                'verbose_name_plural': \'''' + model_name + '''s (API )\',
                'ordering': ['-id'],
            },
        ),
    ]
'''
            
            migration_file = output_dir / f"{migration_number:04d}_create_{model_name.lower()}_from_spec.py"
            migration_file.write_text(migration_content)
            print(f"   : {migration_file}")
            migration_number += 1
            
    def generate_usage_guide(self):
        """  """
        guide_content = f'''# Django      

##  

### 1.  
- `app/models_from_spec.py` - API   Django 

### 2.  
- `migrations_from_spec/`  {len(self.models)}   

##  

'''
        for model_name, fields in self.models.items():
            guide_content += f"\n### {model_name}FromSpec\n"
            guide_content += f"- : `{model_name.lower()}_from_spec`\n"
            guide_content += f"-  : {len(fields)}\n"
            guide_content += "-  :\n"
            for field_name, field_type in fields.items():
                guide_content += f"  - `{field_name}`: {field_type}\n"
        
        guide_content += '''

##  

### 1. Django   
```python
# settings.py INSTALLED_APPS 'app' 
INSTALLED_APPS = [
    # ...  
    'app',
]
```

### 2.  
```bash
#    migrations  
cp migrations_from_spec/*.py your_app/migrations/

#  
python manage.py migrate
```

### 3.   
```python
from app.models_from_spec import VideoplanningFromSpec, ProjectFromSpec

#  
planning = VideoplanningFromSpec.objects.create(
    title="  ",
    planning_text=" ..."
)

#  
all_plannings = VideoplanningFromSpec.objects.all()
```

## 
-   API     
-        
- Foreign Key Many-to-Many    
'''
        
        guide_file = Path("API_MODELS_GUIDE.md")
        guide_file.write_text(guide_content)
        print(f"   : {guide_file}")

def main():
    print(" Django      ")
    print("=" * 60)
    
    generator = ModelGenerator()
    
    print(" API   ...")
    generator.analyze_existing_apis()
    
    print("      ...")
    generator.generate_models()
    
    print(" Django    ...")
    generator.write_models_file()
    
    print("    ...")
    generator.write_migration_files()
    
    print("    ...")
    generator.generate_usage_guide()
    
    print("\n" + "=" * 60)
    print(" Django     !")
    print(f"  {len(generator.models)}  ")
    print("  :")
    print("   - app/models_from_spec.py")
    print("   - migrations_from_spec/*.py")
    print("   - API_MODELS_GUIDE.md")

if __name__ == "__main__":
    main()