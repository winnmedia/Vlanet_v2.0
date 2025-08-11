#!/usr/bin/env python3
"""
   
Django      .
"""
import os
import sys
import django
from pathlib import Path

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_railway')
sys.path.insert(0, str(Path(__file__).resolve().parent))

print("    ...\n")

try:
    django.setup()
    print(" Django  \n")
except Exception as e:
    print(f" Django  : {e}")
    print("       .\n")

#   
def check_migration_directories():
    """     """
    print("   :")
    print("-" * 50)
    
    apps = ['users', 'projects', 'feedbacks', 'video_planning', 'video_analysis', 'admin_dashboard']
    migration_status = {}
    
    for app in apps:
        app_path = Path(app)
        migration_path = app_path / 'migrations'
        
        if not app_path.exists():
            print(f" {app}:    ")
            migration_status[app] = {'exists': False, 'files': []}
            continue
            
        if not migration_path.exists():
            print(f"  {app}: migrations  ")
            migration_status[app] = {'exists': False, 'files': []}
            continue
            
        #   
        migration_files = sorted([
            f.name for f in migration_path.glob('*.py')
            if f.name != '__init__.py' and not f.name.endswith('pyc')
        ])
        
        # __init__.py 
        init_file = migration_path / '__init__.py'
        if not init_file.exists():
            print(f"  {app}: __init__.py   ( )")
            # __init__.py 
            init_file.touch()
            print(f"   → __init__.py ")
        
        #    
        empty_files = []
        for file in migration_files:
            file_path = migration_path / file
            if file_path.stat().st_size == 0:
                empty_files.append(file)
        
        if migration_files:
            print(f" {app}: {len(migration_files)}  ")
            for file in migration_files[:3]:  #  3 
                print(f"   - {file}")
            if len(migration_files) > 3:
                print(f"   ...  {len(migration_files)-3}")
            if empty_files:
                print(f"      : {', '.join(empty_files)}")
        else:
            print(f"  {app}:   ")
            
        migration_status[app] = {
            'exists': True,
            'files': migration_files,
            'empty_files': empty_files
        }
    
    return migration_status

def check_migration_dependencies():
    """  """
    print("\n\n   :")
    print("-" * 50)
    
    try:
        from django.db.migrations.loader import MigrationLoader
        from django.db import connection
        
        loader = MigrationLoader(connection)
        
        #   
        unapplied = []
        for app_label, migration_name in loader.graph.nodes:
            if (app_label, migration_name) not in loader.applied_migrations:
                unapplied.append(f"{app_label}.{migration_name}")
        
        if unapplied:
            print(f"   : {len(unapplied)}")
            for migration in unapplied[:10]:  #  10 
                print(f"   - {migration}")
            if len(unapplied) > 10:
                print(f"   ...  {len(unapplied)-10}")
        else:
            print("   ")
            
        #  
        conflicts = loader.detect_conflicts()
        if conflicts:
            print(f"\n   :")
            for app, migrations in conflicts.items():
                print(f"   {app}: {migrations}")
        else:
            print("   ")
            
    except Exception as e:
        print(f"    : {e}")
        print("     .")

def generate_migration_commands():
    """   """
    print("\n\n    :")
    print("-" * 50)
    
    commands = [
        "# 1.    ",
        "python3 manage.py makemigrations users",
        "python3 manage.py makemigrations projects", 
        "python3 manage.py makemigrations feedbacks",
        "python3 manage.py makemigrations video_planning",
        "python3 manage.py makemigrations video_analysis",
        "python3 manage.py makemigrations admin_dashboard",
        "",
        "# 2.   ",
        "python3 manage.py showmigrations",
        "",
        "# 3.  ",
        "python3 manage.py migrate",
        "",
        "# 4.    ( )",
        "python3 manage.py migrate contenttypes",
        "python3 manage.py migrate auth",
        "python3 manage.py migrate users",
        "python3 manage.py migrate projects",
        "python3 manage.py migrate feedbacks",
        "",
        "# 5.   (!)",
        "python3 manage.py migrate --fake-initial",
    ]
    
    for cmd in commands:
        print(cmd)

def create_ensure_migrations_command():
    """ensure_migrations   """
    print("\n\n ensure_migrations  :")
    print("-" * 50)
    
    # management/commands  
    for app in ['users', 'projects', 'feedbacks']:
        cmd_dir = Path(app) / 'management' / 'commands'
        if not cmd_dir.exists():
            cmd_dir.mkdir(parents=True, exist_ok=True)
            (cmd_dir.parent / '__init__.py').touch()
            (cmd_dir / '__init__.py').touch()
            print(f" {app}/management/commands  ")

def main():
    """  """
    # 1.   
    migration_status = check_migration_directories()
    
    # 2.   
    check_migration_dependencies()
    
    # 3.   
    generate_migration_commands()
    
    # 4. ensure_migrations  
    create_ensure_migrations_command()
    
    #  
    print("\n\n :")
    print("-" * 50)
    
    total_apps = len(migration_status)
    apps_with_migrations = sum(1 for app, status in migration_status.items() 
                              if status['exists'] and status['files'])
    apps_with_empty = sum(1 for app, status in migration_status.items() 
                         if status.get('empty_files'))
    
    print(f"  : {total_apps}")
    print(f"  : {apps_with_migrations}")
    print(f"    : {apps_with_empty}")
    
    if apps_with_empty > 0:
        print("\n        .")
    
    print("\n  !")

if __name__ == "__main__":
    main()