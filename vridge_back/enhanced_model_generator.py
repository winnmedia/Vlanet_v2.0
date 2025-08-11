#!/usr/bin/env python3
"""
Enhanced Django      
HAR   OpenAPI      
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Any, List, Union
import re

class EnhancedModelGenerator:
    def __init__(self):
        self.models = {}
        self.field_analysis = defaultdict(lambda: defaultdict(list))
        self.endpoint_patterns = {}
        
    def load_har_file(self, har_path: str):
        """HAR   API  """
        try:
            with open(har_path, 'r', encoding='utf-8') as f:
                har_data = json.load(f)
            
            print(f" HAR  : {har_path}")
            return self.analyze_har_data(har_data)
        except FileNotFoundError:
            print(f" HAR    : {har_path}")
            return False
        except json.JSONDecodeError:
            print(f" HAR   : {har_path}")
            return False
    
    def load_openapi_spec(self, spec_path: str):
        """OpenAPI    """
        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                spec_data = json.load(f)
            
            print(f" OpenAPI  : {spec_path}")
            return self.analyze_openapi_spec(spec_data)
        except FileNotFoundError:
            print(f" OpenAPI     : {spec_path}")
            return False
        except json.JSONDecodeError:
            print(f" OpenAPI   : {spec_path}")
            return False
    
    def analyze_har_data(self, har_data: dict):
        """HAR  API   """
        entries = har_data.get('log', {}).get('entries', [])
        api_count = 0
        
        for entry in entries:
            request = entry.get('request', {})
            response = entry.get('response', {})
            
            url = request.get('url', '')
            method = request.get('method', 'GET')
            
            # /api/   
            if '/api/' not in url:
                continue
                
            api_count += 1
            
            # URL   
            api_path = url.split('/api/')[-1].strip('/')
            endpoint_base = api_path.split('/')[0] if '/' in api_path else api_path
            
            #   
            content = response.get('content', {})
            text = content.get('text', '')
            
            if text:
                try:
                    response_data = json.loads(text)
                    self.analyze_response_data(endpoint_base, response_data, method)
                except json.JSONDecodeError:
                    continue
        
        print(f"  API : {api_count}")
        return api_count > 0
    
    def analyze_openapi_spec(self, spec_data: dict):
        """OpenAPI    """
        components = spec_data.get('components', {})
        schemas = components.get('schemas', {})
        
        for schema_name, schema_def in schemas.items():
            properties = schema_def.get('properties', {})
            
            model_fields = {}
            for field_name, field_def in properties.items():
                field_type = self.openapi_type_to_django_field(field_def)
                model_fields[field_name] = field_type
            
            if model_fields:
                self.models[schema_name] = model_fields
        
        print(f" OpenAPI  {len(self.models)}  ")
        return len(self.models) > 0
    
    def analyze_response_data(self, endpoint: str, data: Any, method: str):
        """     """
        model_name = self.endpoint_to_model_name(endpoint)
        
        # data data.data  
        actual_data = data
        if isinstance(data, dict):
            if 'data' in data and isinstance(data['data'], (dict, list)):
                actual_data = data['data']
            elif 'results' in data and isinstance(data['results'], list):
                actual_data = data['results']
        
        #      
        if isinstance(actual_data, list) and len(actual_data) > 0:
            actual_data = actual_data[0]
        
        #   
        if isinstance(actual_data, dict):
            for field_name, field_value in actual_data.items():
                if field_name != 'id':  # id  
                    field_type = self.infer_django_field_type(field_name, field_value)
                    self.field_analysis[model_name][field_name].append(field_type)
    
    def endpoint_to_model_name(self, endpoint: str) -> str:
        """  """
        #    CamelCase 
        endpoint = endpoint.rstrip('s')  #   
        endpoint = endpoint.replace('-', '_').replace('_', ' ')
        return ''.join(word.capitalize() for word in endpoint.split())
    
    def infer_django_field_type(self, field_name: str, value: Any) -> str:
        """   Django    ( )"""
        field_name_lower = field_name.lower()
        
        #      
        if isinstance(value, bool):
            return "models.BooleanField(default=False)"
        elif isinstance(value, int):
            if 'id' in field_name_lower and field_name_lower != 'id':
                return "models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)"
            return "models.IntegerField(null=True, blank=True)"
        elif isinstance(value, float):
            if 'confidence' in field_name_lower or 'score' in field_name_lower:
                return "models.FloatField(null=True, blank=True, help_text='0.0-1.0 ')"
            return "models.FloatField(null=True, blank=True)"
        elif isinstance(value, str):
            # /  
            if any(pattern in field_name_lower for pattern in ['created', 'updated', 'date', 'time']):
                if 'created' in field_name_lower:
                    return "models.DateTimeField(auto_now_add=True)"
                elif 'updated' in field_name_lower:
                    return "models.DateTimeField(auto_now=True)"
                else:
                    return "models.DateTimeField(null=True, blank=True)"
            
            #  
            elif 'email' in field_name_lower:
                return "models.EmailField(max_length=254, null=True, blank=True)"
            
            # URL 
            elif any(pattern in field_name_lower for pattern in ['url', 'link', 'href']):
                return "models.URLField(max_length=500, null=True, blank=True)"
            
            # / 
            elif any(pattern in field_name_lower for pattern in ['status', 'state', 'type', 'mode']):
                return f"models.CharField(max_length=50, null=True, blank=True, help_text='{field_name} ')"
            
            #     
            elif len(str(value)) > 500:
                return "models.TextField(null=True, blank=True)"
            elif len(str(value)) > 255:
                return "models.CharField(max_length=500, null=True, blank=True)"
            else:
                return "models.CharField(max_length=255, null=True, blank=True)"
        
        elif isinstance(value, (list, dict)):
            return "models.JSONField(default=dict, null=True, blank=True)"
        else:
            return "models.JSONField(default=dict, null=True, blank=True)"
    
    def openapi_type_to_django_field(self, field_def: dict) -> str:
        """OpenAPI   Django  """
        field_type = field_def.get('type', 'string')
        field_format = field_def.get('format', '')
        
        if field_type == 'boolean':
            return "models.BooleanField(default=False)"
        elif field_type == 'integer':
            return "models.IntegerField(null=True, blank=True)"
        elif field_type == 'number':
            return "models.FloatField(null=True, blank=True)"
        elif field_type == 'string':
            if field_format == 'date-time':
                return "models.DateTimeField(null=True, blank=True)"
            elif field_format == 'email':
                return "models.EmailField(max_length=254, null=True, blank=True)"
            elif field_format == 'uri':
                return "models.URLField(max_length=500, null=True, blank=True)"
            else:
                max_length = field_def.get('maxLength', 255)
                if max_length > 255:
                    return "models.TextField(null=True, blank=True)"
                return f"models.CharField(max_length={max_length}, null=True, blank=True)"
        elif field_type in ['array', 'object']:
            return "models.JSONField(default=dict, null=True, blank=True)"
        else:
            return "models.JSONField(default=dict, null=True, blank=True)"
    
    def consolidate_field_types(self):
        """     """
        for model_name, fields in self.field_analysis.items():
            consolidated_fields = {}
            
            for field_name, type_list in fields.items():
                #     
                type_counter = Counter(type_list)
                most_common_type = type_counter.most_common(1)[0][0]
                consolidated_fields[field_name] = most_common_type
            
            if consolidated_fields:
                self.models[model_name] = consolidated_fields
    
    def write_enhanced_models_file(self):
        """ Django   """
        output_path = Path("app_enhanced")
        output_path.mkdir(exist_ok=True)
        
        models_content = '''"""
HAR/OpenAPI    Enhanced Django 
        
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

'''
        
        for model_name, fields in self.models.items():
            models_content += f"\nclass {model_name}Enhanced(models.Model):\n"
            models_content += f'    """API    Enhanced {model_name} """\n'
            
            #  
            for field_name, field_type in fields.items():
                #   
                if 'JSONField' in field_type:
                    models_content += f"    {field_name} = {field_type}  #   \n"
                elif 'confidence' in field_name.lower():
                    models_content += f"    {field_name} = {field_type}  # AI  \n"
                else:
                    models_content += f"    {field_name} = {field_type}\n"
            
            # Meta 
            models_content += f"\n    class Meta:\n"
            models_content += f"        db_table = '{model_name.lower()}_enhanced'\n"
            models_content += f"        verbose_name = '{model_name} (Enhanced)'\n"
            models_content += f"        verbose_name_plural = '{model_name}s (Enhanced)'\n"
            models_content += f"        ordering = ['-id']\n"
            
            #   ( )
            index_fields = []
            for field_name in fields.keys():
                if any(pattern in field_name.lower() for pattern in ['status', 'type', 'created', 'updated']):
                    index_fields.append(f"'{field_name}'")
            
            if index_fields:
                models_content += f"        indexes = [\n"
                for field in index_fields:
                    models_content += f"            models.Index(fields=[{field}]),\n"
                models_content += f"        ]\n"
            
            # __str__ 
            models_content += f"\n    def __str__(self):\n"
            str_fields = ['title', 'name', 'username', 'email']
            str_field = None
            for field in str_fields:
                if field in fields:
                    str_field = field
                    break
            
            if str_field:
                models_content += f"        return self.{str_field} or f'{model_name}({{self.pk}})'\n"
            else:
                models_content += f"        return f'{model_name}({{self.pk}})'\n"
            
            #  
            if 'created_at' in fields or 'updated_at' in fields:
                models_content += f"\n    @property\n"
                models_content += f"    def age_in_days(self):\n"
                models_content += f"        \"\"\"  \"\"\"\n"
                models_content += f"        from django.utils import timezone\n"
                if 'created_at' in fields:
                    models_content += f"        return (timezone.now() - self.created_at).days\n"
                else:
                    models_content += f"        return (timezone.now() - self.updated_at).days\n"
            
            models_content += "\n"
        
        models_file = output_path / "models_enhanced.py"
        models_file.write_text(models_content)
        print(f" Enhanced   : {models_file}")
        
    def write_enhanced_migrations(self):
        """   """
        output_dir = Path("migrations_enhanced")
        output_dir.mkdir(exist_ok=True)
        
        # __init__.py  
        (output_dir / "__init__.py").write_text("")
        
        migration_number = 1
        for model_name, fields in self.models.items():
            migration_content = f'''# Enhanced migration for {model_name}Enhanced
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    
    operations = [
        migrations.CreateModel(
            name='{model_name}Enhanced',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
'''
            
            for field_name, field_type in fields.items():
                migration_content += f"                ('{field_name}', {field_type}),\n"
            
            migration_content += '''            ],
            options={
                'db_table': \'''' + model_name.lower() + '''_enhanced\',
                'verbose_name': \'''' + model_name + ''' (Enhanced)\',
                'verbose_name_plural': \'''' + model_name + '''s (Enhanced)\',
                'ordering': ['-id'],
            },
        ),
'''
            
            #  
            index_fields = []
            for field_name in fields.keys():
                if any(pattern in field_name.lower() for pattern in ['status', 'type', 'created', 'updated']):
                    index_fields.append(field_name)
            
            if index_fields:
                for field_name in index_fields:
                    migration_content += f'''        migrations.AddIndex(
            model_name='{model_name.lower()}enhanced',
            index=models.Index(fields=['{field_name}'], name='{model_name.lower()}_{field_name}_idx'),
        ),
'''
            
            migration_content += "    ]\n"
            
            migration_file = output_dir / f"{migration_number:04d}_create_{model_name.lower()}_enhanced.py"
            migration_file.write_text(migration_content)
            print(f" Enhanced   : {migration_file}")
            migration_number += 1

def main():
    print(" Enhanced Django      ")
    print("=" * 70)
    
    generator = EnhancedModelGenerator()
    
    #   
    har_file = Path("api_traffic.har")
    openapi_file = Path("openapi.json")
    
    has_input = False
    
    if har_file.exists():
        print(" HAR  ,  ...")
        if generator.load_har_file(str(har_file)):
            has_input = True
    
    if openapi_file.exists():
        print(" OpenAPI  ,  ...")
        if generator.load_openapi_spec(str(openapi_file)):
            has_input = True
    
    if not has_input:
        print("  HAR  OpenAPI    .")
        print("    ...")
        
        #    
        generator.field_analysis = {
            'VideoPlanning': {
                'title': ['models.CharField(max_length=255, null=True, blank=True)'],
                'description': ['models.TextField(null=True, blank=True)'],
                'status': ["models.CharField(max_length=50, null=True, blank=True, help_text='status ')"],
                'created_at': ['models.DateTimeField(auto_now_add=True)']
            },
            'Project': {
                'name': ['models.CharField(max_length=255, null=True, blank=True)'],
                'description': ['models.TextField(null=True, blank=True)'],
                'manager': ['models.CharField(max_length=255, null=True, blank=True)'],
                'created_at': ['models.DateTimeField(auto_now_add=True)']
            }
        }
    
    print("    ...")
    generator.consolidate_field_types()
    
    print(" Enhanced Django    ...")
    generator.write_enhanced_models_file()
    
    print(" Enhanced    ...")
    generator.write_enhanced_migrations()
    
    print("\n" + "=" * 70)
    print(" Enhanced Django     !")
    print(f"  {len(generator.models)} Enhanced  ")
    print("  :")
    print("   - app_enhanced/models_enhanced.py")
    print("   - migrations_enhanced/*.py")
    
    # HAR   
    print("\n HAR   :")
    print("1.     (F12)")
    print("2. Network  ")
    print("3.  API  ")
    print("4. Network    → 'Save all as HAR with content'")
    print("5. 'api_traffic.har'  ")

if __name__ == "__main__":
    main()