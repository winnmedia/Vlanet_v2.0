"""
VideoPlanet    
   .
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from django.test import Client, override_settings
from django.urls import reverse
from django.db import transaction
from users.models import User
from projects.models import Project
import json
import time
from datetime import datetime

class Command(BaseCommand):
    help = 'VideoPlanet      '

    def __init__(self):
        super().__init__()
        self.client = Client()
        self.test_results = {
            'auth': {'passed': [], 'failed': []},
            'project': {'passed': [], 'failed': []},
            'feedback': {'passed': [], 'failed': []},
            'planning': {'passed': [], 'failed': []},
            'navigation': {'passed': [], 'failed': []},
            'general': {'passed': [], 'failed': []}
        }
        self.start_time = time.time()
        
    def add_result(self, category, test_name, passed, details=''):
        result = {
            'test': test_name,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        if passed:
            self.test_results[category]['passed'].append(result)
            status = ''
        else:
            self.test_results[category]['failed'].append(result)
            status = ''
            
        self.stdout.write(f"{status} [{category.upper()}] {test_name}: {details}")

    def test_authentication_system(self):
        """  """
        self.stdout.write(self.style.SUCCESS('\n 1.   '))
        
        #   
        try:
            user = User.objects.get(email='test@example.com')
            self.add_result('auth', '   ', True, f': {user.email}')
        except User.DoesNotExist:
            self.add_result('auth', '   ', False, '  ')
            return
        
        #  
        if user.check_password('testpassword'):
            self.add_result('auth', '  ', True, ' ')
        else:
            self.add_result('auth', '  ', False, ' ')
        
        # Django  
        auth_user = authenticate(email='test@example.com', password='testpassword')
        if auth_user:
            self.add_result('auth', 'Django  ', True, f' : {auth_user.email}')
        else:
            self.add_result('auth', 'Django  ', False, ' ')
        
        # API  
        login_data = {
            'email': 'test@example.com',
            'password': 'testpassword'
        }
        
        try:
            response = self.client.post('/api/users/login/',
                                      data=json.dumps(login_data),
                                      content_type='application/json')
            
            if response.status_code == 200:
                response_data = response.json()
                if 'access' in response_data:
                    self.access_token = response_data['access']
                    self.add_result('auth', 'API ', True, f'  : {len(self.access_token)}')
                elif 'vridge_session' in response_data:
                    self.access_token = response_data['vridge_session']
                    self.add_result('auth', 'API ', True, f'  : {len(self.access_token)}')
                else:
                    self.add_result('auth', 'API ', False, f' : {response_data}')
            else:
                self.add_result('auth', 'API ', False, f' : {response.status_code}, : {response.content}')
        except Exception as e:
            self.add_result('auth', 'API ', False, f' : {str(e)}')

    def test_project_management(self):
        """  """
        self.stdout.write(self.style.SUCCESS('\n 2.   '))
        
        if not hasattr(self, 'access_token'):
            self.add_result('project', '  ', False, '    ')
            return
        
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        
        #   
        try:
            response = self.client.get('/api/projects/', **headers)
            if response.status_code == 200:
                data = response.json()
                project_count = len(data.get('results', data)) if isinstance(data, dict) else len(data)
                self.add_result('project', '  ', True, f'{project_count}  ')
            else:
                self.add_result('project', '  ', False, f': {response.status_code}')
        except Exception as e:
            self.add_result('project', '  ', False, f': {str(e)}')
        
        #   
        project_data = {
            'name': f'   {int(time.time())}',
            'manager': ' ',
            'consumer': ' ',
            'description': '  ',
            'color': '#1631F8',
            'process_data': [{
                'name': '',
                'startDate': datetime.now().isoformat(),
                'endDate': datetime.now().isoformat()
            }]
        }
        
        try:
            response = self.client.post('/api/projects/create/',
                                      data=json.dumps(project_data),
                                      content_type='application/json',
                                      **headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.add_result('project', ' ', True, f'  : {data.get("project_id", "ID ")}')
            else:
                self.add_result('project', ' ', False, f': {response.status_code}, : {response.content}')
        except Exception as e:
            self.add_result('project', ' ', False, f': {str(e)}')
        
        #   
        try:
            response = self.client.get('/api/projects/frameworks/', **headers)
            if response.status_code == 200:
                data = response.json()
                framework_count = len(data) if isinstance(data, list) else len(data.keys())
                self.add_result('project', ' ', True, f'{framework_count}   ')
            else:
                self.add_result('project', ' ', False, f': {response.status_code}')
        except Exception as e:
            self.add_result('project', ' ', False, f': {str(e)}')

    def test_user_management(self):
        """  """
        self.stdout.write(self.style.SUCCESS('\n 3.   '))
        
        if not hasattr(self, 'access_token'):
            self.add_result('navigation', '  ', False, '    ')
            return
        
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        
        #   
        try:
            response = self.client.get('/api/users/me/', **headers)
            if response.status_code == 200:
                data = response.json()
                self.add_result('navigation', '  ', True, f": {data.get('nickname', data.get('email'))}")
            else:
                self.add_result('navigation', '  ', False, f': {response.status_code}')
        except Exception as e:
            self.add_result('navigation', '  ', False, f': {str(e)}')
        
        #  
        try:
            response = self.client.get('/api/users/notifications/', **headers)
            if response.status_code == 200:
                data = response.json()
                notification_count = len(data) if isinstance(data, list) else 0
                self.add_result('navigation', ' ', True, f'{notification_count} ')
            else:
                self.add_result('navigation', ' ', False, f': {response.status_code}')
        except Exception as e:
            self.add_result('navigation', ' ', False, f': {str(e)}')
        
        # 
        try:
            response = self.client.get('/api/users/mypage/', **headers)
            if response.status_code == 200:
                self.add_result('navigation', '', True, '   ')
            else:
                self.add_result('navigation', '', False, f': {response.status_code}')
        except Exception as e:
            self.add_result('navigation', '', False, f': {str(e)}')

    def test_feedback_system(self):
        """  """
        self.stdout.write(self.style.SUCCESS('\n 4.   '))
        
        if not hasattr(self, 'access_token'):
            self.add_result('feedback', '  ', False, '    ')
            return
        
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        
        #     ( ID 1 )
        try:
            response = self.client.get('/api/projects/1/feedback/', **headers)
            if response.status_code == 200:
                data = response.json()
                feedback_count = len(data.get('results', data)) if isinstance(data, dict) else len(data)
                self.add_result('feedback', '  ', True, f'{feedback_count} ')
            else:
                self.add_result('feedback', '  ', False, f': {response.status_code}')
        except Exception as e:
            self.add_result('feedback', '  ', False, f': {str(e)}')

    def test_video_planning(self):
        """  """
        self.stdout.write(self.style.SUCCESS('\n 5.   '))
        
        if not hasattr(self, 'access_token'):
            self.add_result('planning', '  ', False, '    ')
            return
        
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        
        #    
        try:
            response = self.client.get('/api/video-planning/', **headers)
            if response.status_code == 200:
                data = response.json()
                planning_count = len(data) if isinstance(data, list) else 0
                self.add_result('planning', '  ', True, f'{planning_count}  ')
            else:
                self.add_result('planning', '  ', False, f': {response.status_code}')
        except Exception as e:
            self.add_result('planning', '  ', False, f': {str(e)}')

    def test_api_health(self):
        """API  """
        self.stdout.write(self.style.SUCCESS('\n 6. API  '))
        
        #  
        try:
            response = self.client.get('/api/health/')
            if response.status_code == 200:
                data = response.json()
                self.add_result('general', 'API ', True, f": {data.get('status', 'unknown')}")
            else:
                self.add_result('general', 'API ', False, f' : {response.status_code}')
        except Exception as e:
            self.add_result('general', 'API ', False, f': {str(e)}')
        
        #   
        try:
            user_count = User.objects.count()
            project_count = Project.objects.count()
            self.add_result('general', ' ', True, f': {user_count}, : {project_count}')
        except Exception as e:
            self.add_result('general', ' ', False, f'DB : {str(e)}')

    def generate_report(self):
        """  """
        end_time = time.time()
        duration = round(end_time - self.start_time, 2)
        
        total_passed = sum(len(cat['passed']) for cat in self.test_results.values())
        total_failed = sum(len(cat['failed']) for cat in self.test_results.values())
        total_tests = total_passed + total_failed
        success_rate = round((total_passed / total_tests * 100), 1) if total_tests > 0 else 0
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('    '))
        self.stdout.write('='*60)
        self.stdout.write(f' : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write(f' : {total_tests}')
        self.stdout.write(f': {total_passed}')
        self.stdout.write(f': {total_failed}')
        self.stdout.write(f': {success_rate}%')
        self.stdout.write(f' : {duration}')
        self.stdout.write('='*60)
        
        #  
        for category, results in self.test_results.items():
            passed_count = len(results['passed'])
            failed_count = len(results['failed'])
            total_cat = passed_count + failed_count
            
            if total_cat > 0:
                cat_rate = round((passed_count / total_cat * 100), 1)
                self.stdout.write(f'\n {category.upper()}: {passed_count}/{total_cat} ({cat_rate}%)')
                
                for test in results['passed']:
                    self.stdout.write(f'   {test["test"]}: {test["details"]}')
                
                for test in results['failed']:
                    self.stdout.write(self.style.ERROR(f'   {test["test"]}: {test["details"]}'))
        
        # 
        if success_rate >= 95:
            conclusion = ' :    !'
        elif success_rate >= 85:
            conclusion = ' :       .'
        elif success_rate >= 70:
            conclusion = ' :        .'
        else:
            conclusion = ' :       .'
        
        self.stdout.write(f'\n  : {conclusion}')
        
        return {
            'success_rate': success_rate,
            'total_tests': total_tests,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'duration': duration,
            'results': self.test_results
        }

    @override_settings(ALLOWED_HOSTS=['*'])
    def handle(self, *args, **options):
        """ """
        self.stdout.write(self.style.SUCCESS(' VideoPlanet    '))
        self.stdout.write('='*60)
        
        try:
            #   
            self.test_authentication_system()
            self.test_project_management()
            self.test_user_management()
            self.test_feedback_system()
            self.test_video_planning() 
            self.test_api_health()
            
            #   
            report = self.generate_report()
            
            self.stdout.write(f'\n   !')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'    : {str(e)}'))
            raise