#!/usr/bin/env python3
"""
   
-   
-  
-  
"""

import os
import sys
import subprocess
import datetime
import json
from pathlib import Path

# Django    
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

import django
django.setup()

from django.core.management import call_command
from django.db import connection
from django.conf import settings


class SafeMigration:
    def __init__(self):
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = Path('backups') / 'migrations'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def check_pending_migrations(self):
        """   """
        print("\n    ...")
        
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        call_command('showmigrations', '--plan', stdout=out)
        output = out.getvalue()
        
        pending = []
        for line in output.split('\n'):
            if '[ ]' in line:
                pending.append(line.strip())
        
        if pending:
            print(f"\n     {len(pending)}:")
            for migration in pending[:10]:  #  10 
                print(f"  - {migration}")
            if len(pending) > 10:
                print(f"  ...  {len(pending) - 10}")
        else:
            print("    .")
        
        return pending
    
    def backup_database(self):
        """ """
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
            return self._backup_sqlite()
        elif 'postgresql' in settings.DATABASES['default']['ENGINE']:
            return self._backup_postgresql()
        else:
            print("     .")
            return None
    
    def _backup_sqlite(self):
        """SQLite """
        print("\n SQLite   ...")
        
        db_path = settings.DATABASES['default']['NAME']
        backup_path = self.backup_dir / f'db_backup_{self.timestamp}.sqlite3'
        
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"  : {backup_path}")
            return backup_path
        except Exception as e:
            print(f"  : {e}")
            return None
    
    def _backup_postgresql(self):
        """PostgreSQL """
        print("\n PostgreSQL   ...")
        
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            print(" DATABASE_URL  .")
            return None
        
        backup_path = self.backup_dir / f'db_backup_{self.timestamp}.sql'
        
        try:
            # pg_dump  
            cmd = f'pg_dump "{db_url}" > "{backup_path}"'
            subprocess.run(cmd, shell=True, check=True)
            
            # 
            subprocess.run(f'gzip "{backup_path}"', shell=True, check=True)
            backup_path = Path(str(backup_path) + '.gz')
            
            print(f"  : {backup_path}")
            return backup_path
        except subprocess.CalledProcessError as e:
            print(f"  : {e}")
            return None
    
    def simulate_migrations(self):
        """  (  )"""
        print("\n  ...")
        
        try:
            # sqlmigrate SQL 
            from django.core.management import call_command
            from io import StringIO
            
            out = StringIO()
            call_command('showmigrations', '--plan', stdout=out)
            plan = out.getvalue()
            
            #   
            pending_migrations = []
            for line in plan.split('\n'):
                if '[ ]' in line and ' ' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        app = parts[1].split('.')[0]
                        migration = parts[1].split('.')[-1]
                        pending_migrations.append((app, migration))
            
            if not pending_migrations:
                print("   .")
                return True
            
            print(f"\n    :")
            for app, migration in pending_migrations[:5]:  #  5 
                print(f"  - {app}: {migration}")
                
                # SQL 
                try:
                    out = StringIO()
                    call_command('sqlmigrate', app, migration, stdout=out)
                    sql = out.getvalue()
                    if sql:
                        print(f"    SQL  ( 200):")
                        print(f"    {sql[:200]}...")
                except Exception:
                    pass
            
            if len(pending_migrations) > 5:
                print(f"  ...  {len(pending_migrations) - 5}")
            
            return True
            
        except Exception as e:
            print(f"  : {e}")
            return False
    
    def apply_migrations(self, fake=False):
        """ """
        print(f"\n  {'(fake)' if fake else ''}  ...")
        
        try:
            if fake:
                call_command('migrate', '--fake')
            else:
                call_command('migrate')
            
            print("   !")
            return True
            
        except Exception as e:
            print(f"   : {e}")
            return False
    
    def verify_migrations(self):
        """  """
        print("\n    ...")
        
        pending = self.check_pending_migrations()
        
        if not pending:
            print("    !")
            
            #   
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM django_migrations")
                    count = cursor.fetchone()[0]
                    print(f"  {count}   .")
            except Exception:
                pass
            
            return True
        else:
            print("     .")
            return False
    
    def rollback_to_backup(self, backup_path):
        """ """
        print(f"\n⏪   : {backup_path}")
        
        if not backup_path or not Path(backup_path).exists():
            print("     .")
            return False
        
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
            try:
                import shutil
                db_path = settings.DATABASES['default']['NAME']
                shutil.copy2(backup_path, db_path)
                print("  !")
                return True
            except Exception as e:
                print(f"  : {e}")
                return False
        else:
            print("  PostgreSQL    .")
            print(f"   psql $DATABASE_URL < {backup_path}")
            return False
    
    def run(self, skip_backup=False, fake=False, auto_yes=False):
        """  """
        print("=" * 80)
        print("  VideoPlanet  ")
        print("=" * 80)
        
        # 1.   
        pending = self.check_pending_migrations()
        if not pending:
            print("\n    .")
            return True
        
        # 2. 
        backup_path = None
        if not skip_backup:
            backup_path = self.backup_database()
            if not backup_path and not auto_yes:
                response = input("\n    ? (y/N): ")
                if response.lower() != 'y':
                    print("  ")
                    return False
        
        # 3. 
        if not self.simulate_migrations():
            print("    .")
            return False
        
        # 4.  
        if not auto_yes:
            print("\n" + "=" * 80)
            print("    ?")
            print("      .")
            if backup_path:
                print(f"    : {backup_path}")
            print("=" * 80)
            
            response = input("? (y/N): ")
            if response.lower() != 'y':
                print("  ")
                return False
        
        # 5.  
        if not self.apply_migrations(fake=fake):
            print("\n  !")
            if backup_path:
                print("     :")
                print(f"   python manage.py dbbackup --restore --input-path={backup_path}")
            return False
        
        # 6. 
        if not self.verify_migrations():
            print("\n     ")
            return False
        
        print("\n   !")
        return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description=' Django ')
    parser.add_argument('--skip-backup', action='store_true', 
                       help='   (!)')
    parser.add_argument('--fake', action='store_true',
                       help=' SQL     ')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='    yes')
    
    args = parser.parse_args()
    
    migration = SafeMigration()
    success = migration.run(
        skip_backup=args.skip_backup,
        fake=args.fake,
        auto_yes=args.yes
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()