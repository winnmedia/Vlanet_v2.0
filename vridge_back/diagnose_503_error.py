#!/usr/bin/env python3
"""
Django 503     
Railway  Django     .
"""
import os
import sys
import importlib
import traceback
from pathlib import Path

#  
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")

def check_environment():
    """    """
    print_header("1.  ")
    
    critical_vars = {
        'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE', 'Not Set'),
        'SECRET_KEY': 'Set' if os.environ.get('SECRET_KEY') else 'Not Set',
        'DATABASE_URL': 'Set' if os.environ.get('DATABASE_URL') else 'Not Set',
        'DEBUG': os.environ.get('DEBUG', 'Not Set'),
        'ALLOWED_HOSTS': os.environ.get('ALLOWED_HOSTS', 'Not Set'),
        'CORS_ALLOWED_ORIGINS': os.environ.get('CORS_ALLOWED_ORIGINS', 'Not Set'),
    }
    
    all_set = True
    for var, value in critical_vars.items():
        if value in ['Not Set', '']:
            print(f"{Colors.RED} {var}: {value}{Colors.ENDC}")
            all_set = False
        else:
            print(f"{Colors.GREEN} {var}: {value}{Colors.ENDC}")
    
    return all_set

def check_python_path():
    """Python    """
    print_header("2. Python  ")
    
    print(f"Python : {sys.version}")
    print(f"Python  : {sys.executable}")
    print(f"\nPython :")
    for i, path in enumerate(sys.path[:5]):
        print(f"  {i}: {path}")
    
    #   
    project_root = Path(__file__).resolve().parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        print(f"\n{Colors.YELLOW}    sys.path : {project_root}{Colors.ENDC}")
    
    return True

def check_django_settings():
    """Django    """
    print_header("3. Django   ")
    
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings_railway')
    print(f" : {settings_module}")
    
    try:
        #    
        settings = importlib.import_module(settings_module)
        print(f"{Colors.GREEN}    {Colors.ENDC}")
        
        #   
        important_settings = ['SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS', 'DATABASES', 'INSTALLED_APPS']
        for setting in important_settings:
            if hasattr(settings, setting):
                value = getattr(settings, setting)
                if setting == 'SECRET_KEY':
                    value = value[:20] + '...' if value else 'Not Set'
                elif setting == 'DATABASES':
                    value = 'Configured' if value else 'Not Configured'
                elif isinstance(value, list) and len(value) > 3:
                    value = f"{len(value)} items"
                print(f"  - {setting}: {value}")
            else:
                print(f"  {Colors.RED} {setting}: Not Found{Colors.ENDC}")
        
        return True
        
    except ImportError as e:
        print(f"{Colors.RED}    : {e}{Colors.ENDC}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"{Colors.RED}    : {e}{Colors.ENDC}")
        traceback.print_exc()
        return False

def check_database_config():
    """  """
    print_header("4.   ")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_railway')
        import django
        django.setup()
        
        from django.conf import settings
        from django.db import connection
        
        #   
        db_config = settings.DATABASES.get('default', {})
        print(f" : {db_config.get('ENGINE', 'Not Set')}")
        print(f" : {db_config.get('NAME', 'Not Set')}")
        
        #  
        print("\n  ...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"{Colors.GREEN}   {Colors.ENDC}")
            return True
            
    except Exception as e:
        print(f"{Colors.RED}   : {e}{Colors.ENDC}")
        traceback.print_exc()
        return False

def check_installed_apps():
    """INSTALLED_APPS    """
    print_header("5. Django  ")
    
    try:
        from django.conf import settings
        
        print("INSTALLED_APPS:")
        project_apps = [app for app in settings.INSTALLED_APPS if not app.startswith('django.')]
        
        for app in project_apps:
            try:
                importlib.import_module(app)
                print(f"{Colors.GREEN}   {app}{Colors.ENDC}")
            except ImportError as e:
                print(f"{Colors.RED}   {app}: {e}{Colors.ENDC}")
                
                #     
                app_path = Path(app.replace('.', '/'))
                if not app_path.exists():
                    print(f"     →   : {app_path}")
                    
        return True
        
    except Exception as e:
        print(f"{Colors.RED}   : {e}{Colors.ENDC}")
        return False

def check_middleware():
    """  """
    print_header("6.  ")
    
    try:
        from django.conf import settings
        
        print("MIDDLEWARE:")
        for middleware in settings.MIDDLEWARE:
            try:
                #    
                if '.' in middleware:
                    module_path, class_name = middleware.rsplit('.', 1)
                    module = importlib.import_module(module_path)
                    middleware_class = getattr(module, class_name)
                    print(f"{Colors.GREEN}   {middleware}{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}   {middleware}: {e}{Colors.ENDC}")
                
        return True
        
    except Exception as e:
        print(f"{Colors.RED}   : {e}{Colors.ENDC}")
        return False

def simulate_django_startup():
    """Django  """
    print_header("7. Django  ")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_railway')
        
        print("Django  ...")
        import django
        django.setup()
        
        print(f"{Colors.GREEN} Django  !{Colors.ENDC}")
        
        #   
        from django.apps import apps
        print(f"\n  : {len(apps.get_app_configs())}")
        
        #  
        all_models = apps.get_models()
        print(f"  : {len(all_models)}")
        
        return True
        
    except Exception as e:
        print(f"{Colors.RED} Django  : {e}{Colors.ENDC}")
        traceback.print_exc()
        return False

def generate_solution():
    """  """
    print_header("8.  ")
    
    print(f"{Colors.BOLD} Django 503   :{Colors.ENDC}\n")
    
    print("1. **   ** (config/settings_minimal.py)")
    print("   -   Django    ")
    print("   -       ")
    
    print("\n2. **  ** (start_minimal.sh)")
    print("   -   ")
    print("   -   ")
    
    print("\n3. **Railway  **")
    print("   - Procfile  : gunicorn config.wsgi")
    print("   - railway.json  Procfile ")
    
    print("\n4. ** **")
    print("   -   ")
    print("   -    ")

def main():
    """  """
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("Django 503    ")
    print(f" : {Colors.ENDC}")
    
    results = {
        "": check_environment(),
        "Python ": check_python_path(),
        "Django ": check_django_settings(),
        "": check_database_config(),
        " ": check_installed_apps(),
        "": check_middleware(),
        "Django ": simulate_django_startup(),
    }
    
    #  
    print_header("  ")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f" : {total}")
    print(f"{Colors.GREEN}: {passed}{Colors.ENDC}")
    print(f"{Colors.RED}: {total - passed}{Colors.ENDC}")
    
    print("\n :")
    for check, result in results.items():
        if not result:
            print(f"  {Colors.RED} {check}{Colors.ENDC}")
    
    #  
    generate_solution()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)