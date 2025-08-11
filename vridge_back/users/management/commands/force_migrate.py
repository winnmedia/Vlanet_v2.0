from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Force create missing tables and columns'

    def handle(self, *args, **options):
        self.stdout.write('   ...')
        
        with connection.cursor() as cursor:
            # 1. users_notification  
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users_notification (
                        id SERIAL PRIMARY KEY,
                        created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        recipient_id INTEGER NOT NULL REFERENCES users_user(id),
                        notification_type VARCHAR(50) NOT NULL,
                        title VARCHAR(200) NOT NULL,
                        message TEXT NOT NULL,
                        project_id INTEGER,
                        invitation_id INTEGER,
                        is_read BOOLEAN DEFAULT FALSE,
                        read_at TIMESTAMP WITH TIME ZONE,
                        extra_data JSONB DEFAULT '{}'::jsonb
                    );
                """)
                self.stdout.write(self.style.SUCCESS(' users_notification  '))
                
                #  
                cursor.execute("CREATE INDEX IF NOT EXISTS users_notification_recipient_created ON users_notification(recipient_id, created DESC);")
                cursor.execute("CREATE INDEX IF NOT EXISTS users_notification_recipient_read ON users_notification(recipient_id, is_read);")
                cursor.execute("CREATE INDEX IF NOT EXISTS users_notification_type ON users_notification(notification_type);")
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'users_notification : {e}'))
            
            # 2. email_verified  
            try:
                cursor.execute("""
                    ALTER TABLE users_user 
                    ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
                """)
                self.stdout.write(self.style.SUCCESS(' email_verified  '))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'email_verified : {e}'))
            
            # 3. email_verified_at  
            try:
                cursor.execute("""
                    ALTER TABLE users_user 
                    ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE;
                """)
                self.stdout.write(self.style.SUCCESS(' email_verified_at  '))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'email_verified_at : {e}'))
            
            # 4. friend_code  
            try:
                cursor.execute("""
                    ALTER TABLE users_user 
                    ADD COLUMN IF NOT EXISTS friend_code VARCHAR(20) UNIQUE;
                """)
                self.stdout.write(self.style.SUCCESS(' friend_code  '))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'friend_code : {e}'))
            
            # 5. users_recentinvitation  
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users_recentinvitation (
                        id SERIAL PRIMARY KEY,
                        created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        inviter_id INTEGER NOT NULL REFERENCES users_user(id),
                        invitee_email VARCHAR(254) NOT NULL,
                        invitee_name VARCHAR(100),
                        project_name VARCHAR(200) NOT NULL,
                        invitation_count INTEGER DEFAULT 1 CHECK (invitation_count >= 0),
                        last_invited_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(inviter_id, invitee_email)
                    );
                """)
                self.stdout.write(self.style.SUCCESS(' users_recentinvitation  '))
                
                #  
                cursor.execute("CREATE INDEX IF NOT EXISTS users_recentinvitation_inviter ON users_recentinvitation(inviter_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS users_recentinvitation_last_invited ON users_recentinvitation(last_invited_at DESC);")
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'users_recentinvitation : {e}'))
            
            # 6. users_friendship  
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users_friendship (
                        id SERIAL PRIMARY KEY,
                        created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        from_user_id INTEGER NOT NULL REFERENCES users_user(id),
                        to_user_id INTEGER NOT NULL REFERENCES users_user(id),
                        status VARCHAR(20) DEFAULT 'pending',
                        is_blocked BOOLEAN DEFAULT FALSE,
                        blocked_by_id INTEGER REFERENCES users_user(id),
                        UNIQUE(from_user_id, to_user_id)
                    );
                """)
                self.stdout.write(self.style.SUCCESS(' users_friendship  '))
                
                #  
                cursor.execute("CREATE INDEX IF NOT EXISTS users_friendship_from_user ON users_friendship(from_user_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS users_friendship_to_user ON users_friendship(to_user_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS users_friendship_status ON users_friendship(status);")
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'users_friendship : {e}'))
        
        # 7.  
        self.stdout.write('\n  ...')
        call_command('migrate', '--noinput')
        
        self.stdout.write(self.style.SUCCESS('\n   !'))