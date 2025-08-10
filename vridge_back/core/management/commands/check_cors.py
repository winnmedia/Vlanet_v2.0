"""
Django 관리 명령어: CORS 설정 확인
사용법: python manage.py check_cors
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import json


class Command(BaseCommand):
    help = 'Check and display CORS configuration'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('CORS Configuration Check'))
        self.stdout.write(self.style.SUCCESS('=' * 60 + '\n'))
        
        # 1. 미들웨어 확인
        self.stdout.write(self.style.WARNING('1. Middleware Configuration:'))
        cors_middlewares = []
        for i, middleware in enumerate(settings.MIDDLEWARE):
            if 'cors' in middleware.lower() or 'options' in middleware.lower():
                status = '✅' if 'solution' in middleware else '⚠️'
                self.stdout.write(f'   [{i:2d}] {status} {middleware}')
                cors_middlewares.append(middleware)
        
        if not cors_middlewares:
            self.stdout.write(self.style.ERROR('   ❌ No CORS middleware found!'))
        
        # 2. CORS 설정 확인
        self.stdout.write(self.style.WARNING('\n2. CORS Settings:'))
        
        cors_settings = {
            'CORS_ALLOW_ALL_ORIGINS': getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', None),
            'CORS_ALLOWED_ORIGINS': getattr(settings, 'CORS_ALLOWED_ORIGINS', None),
            'CORS_ALLOW_CREDENTIALS': getattr(settings, 'CORS_ALLOW_CREDENTIALS', None),
            'CORS_ALLOW_HEADERS': getattr(settings, 'CORS_ALLOW_HEADERS', None),
            'CORS_ALLOW_METHODS': getattr(settings, 'CORS_ALLOW_METHODS', None),
            'CORS_EXPOSE_HEADERS': getattr(settings, 'CORS_EXPOSE_HEADERS', None),
            'CORS_PREFLIGHT_MAX_AGE': getattr(settings, 'CORS_PREFLIGHT_MAX_AGE', None),
        }
        
        for key, value in cors_settings.items():
            if value is not None:
                if isinstance(value, (list, tuple)) and len(value) > 3:
                    value_str = f'{value[:3]}... ({len(value)} items)'
                else:
                    value_str = str(value)
                self.stdout.write(f'   {key}: {value_str}')
        
        # 3. CSRF 설정 확인
        self.stdout.write(self.style.WARNING('\n3. CSRF Settings:'))
        csrf_origins = getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])
        if csrf_origins:
            for origin in csrf_origins[:5]:
                self.stdout.write(f'   ✅ {origin}')
            if len(csrf_origins) > 5:
                self.stdout.write(f'   ... and {len(csrf_origins) - 5} more')
        else:
            self.stdout.write(self.style.ERROR('   ❌ No CSRF trusted origins configured'))
        
        # 4. 허용된 호스트 확인
        self.stdout.write(self.style.WARNING('\n4. Allowed Hosts:'))
        for host in settings.ALLOWED_HOSTS[:5]:
            self.stdout.write(f'   ✅ {host}')
        if len(settings.ALLOWED_HOSTS) > 5:
            self.stdout.write(f'   ... and {len(settings.ALLOWED_HOSTS) - 5} more')
        
        # 5. 권장사항
        self.stdout.write(self.style.WARNING('\n5. Recommendations:'))
        
        if 'config.cors_solution.RailwayCORSMiddleware' in settings.MIDDLEWARE:
            self.stdout.write(self.style.SUCCESS('   ✅ Using new RailwayCORSMiddleware - Good!'))
        else:
            self.stdout.write(self.style.ERROR('   ❌ Not using RailwayCORSMiddleware - Consider switching'))
        
        if 'config.cors_solution.OptionsHandlerMiddleware' in settings.MIDDLEWARE:
            index = settings.MIDDLEWARE.index('config.cors_solution.OptionsHandlerMiddleware')
            if index == 0:
                self.stdout.write(self.style.SUCCESS('   ✅ OptionsHandlerMiddleware is first - Good!'))
            else:
                self.stdout.write(self.style.ERROR(f'   ⚠️ OptionsHandlerMiddleware at position {index} - Should be first!'))
        else:
            self.stdout.write(self.style.ERROR('   ❌ OptionsHandlerMiddleware not found - Add it!'))
        
        if 'corsheaders.middleware.CorsMiddleware' in settings.MIDDLEWARE:
            self.stdout.write(self.style.WARNING('   ⚠️ django-cors-headers middleware still active - Consider removing'))
        
        # 6. 테스트 URL
        self.stdout.write(self.style.WARNING('\n6. Test URLs:'))
        self.stdout.write('   You can test CORS with these commands:')
        self.stdout.write(self.style.SUCCESS('   curl -X OPTIONS https://videoplanet.up.railway.app/api/health/ \\'))
        self.stdout.write(self.style.SUCCESS('        -H "Origin: https://vlanet.net" \\'))
        self.stdout.write(self.style.SUCCESS('        -H "Access-Control-Request-Method: POST" \\'))
        self.stdout.write(self.style.SUCCESS('        -H "Access-Control-Request-Headers: content-type" -v'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('Check Complete'))
        self.stdout.write(self.style.SUCCESS('=' * 60 + '\n'))