#!/usr/bin/env python3
"""
VideoPlanet   
      
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = 'http://localhost:8000/api'

class VideoPlanetTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.project_id = None
        self.planning_id = None
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
    
    def log_result(self, test_name, success, error=None):
        self.results['total'] += 1
        if success:
            self.results['passed'] += 1
            print(f" {test_name}: ")
        else:
            self.results['failed'] += 1
            print(f" {test_name}:  - {error}")
        
        self.results['details'].append({
            'test': test_name,
            'status': 'PASS' if success else 'FAIL',
            'error': error
        })
    
    def test_login(self):
        """ """
        try:
            response = requests.post(f'{BASE_URL}/users/login/', 
                json={
                    'email': 'ceo@winnmedia.co.kr',
                    'password': 'Qwerasdf!234'
                }
            )
            
            if response.status_code == 200:
                self.token = response.json().get('vridge_session')
                self.user_id = response.json().get('user_id')
                self.log_result('', True)
                return True
            else:
                self.log_result('', False, response.text)
                return False
        except Exception as e:
            self.log_result('', False, str(e))
            return False
    
    def test_project_creation(self):
        """  """
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(f'{BASE_URL}/projects/create/', 
                headers=headers,
                json={
                    'name': f'  {datetime.now().timestamp()}',
                    'description': '  ',
                    'manager': ' ',
                    'consumer': ' ',
                    'color': '#1631F8',
                    'process': []
                }
            )
            
            if response.status_code == 200:
                self.project_id = response.json().get('project_id')
                self.log_result(' ', True)
                return True
            else:
                self.log_result(' ', False, response.text)
                return False
        except Exception as e:
            self.log_result(' ', False, str(e))
            return False
    
    def test_ai_planning(self):
        """AI   """
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            # 1. AI  
            response = requests.post(f'{BASE_URL}/video-planning/ai/quick-suggestions/', 
                headers=headers,
                json={
                    'project_type': 'youtube',
                    'main_topic': ' ',
                    'target_audience': '20-30',
                    'duration': '5'
                }
            )
            
            if response.status_code != 200:
                self.log_result('AI  ', False, response.text)
                return False
            
            self.log_result('AI  ', True)
            
            # 2. AI   
            response = requests.post(f'{BASE_URL}/video-planning/ai/generate-full-planning/', 
                headers=headers,
                json={
                    'projectType': 'youtube',
                    'duration': '5',
                    'targetAudience': '20-30',
                    'mainTopic': ' ',
                    'keyMessage': '   ',
                    'desiredMood': '',
                    'enableProOptions': True,
                    'colorTone': 'natural',
                    'aspectRatio': '16:9',
                    'cameraType': 'dslr',
                    'lensType': '35mm',
                    'cameraMovement': 'static'
                }
            )
            
            if response.status_code != 200:
                self.log_result('AI   ', False, response.text)
                return False
            
            self.log_result('AI   ', True)
            return True
            
        except Exception as e:
            self.log_result('AI  ', False, str(e))
            return False
    
    def test_planning_save(self):
        """  """
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(f'{BASE_URL}/video-planning/save/', 
                headers=headers,
                json={
                    'title': '  ',
                    'planning_text': '  ',
                    'stories': [
                        {'phase': '', 'content': ''},
                        {'phase': '', 'content': ''},
                        {'phase': '', 'content': ''},
                        {'phase': '', 'content': ''}
                    ],
                    'scenes': [],
                    'shots': [],
                    'storyboards': []
                }
            )
            
            if response.status_code == 201:
                self.planning_id = response.json()['data']['planning_id']
                self.log_result(' ', True)
                return True
            else:
                self.log_result(' ', False, response.text)
                return False
        except Exception as e:
            self.log_result(' ', False, str(e))
            return False
    
    def test_pdf_export(self):
        """PDF  """
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(f'{BASE_URL}/video-planning/export/pdf/', 
                headers=headers,
                json={
                    'planning_data': {
                        'title': 'PDF ',
                        'planning': ' ',
                        'stories': [],
                        'scenes': []
                    },
                    'use_enhanced_layout': True
                }
            )
            
            if response.status_code == 200 and len(response.content) > 1000:
                self.log_result('PDF ', True)
                return True
            else:
                self.log_result('PDF ', False, f': {response.status_code}')
                return False
        except Exception as e:
            self.log_result('PDF ', False, str(e))
            return False
    
    def test_feedback(self):
        """ """
        try:
            if not self.project_id:
                self.log_result(' ', False, ' ID ')
                return False
            
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(f'{BASE_URL}/projects/{self.project_id}/feedback/comments/', 
                headers=headers,
                json={
                    'content': '  ',
                    'feedback_type': 'comment'
                }
            )
            
            if response.status_code in [200, 201]:
                self.log_result(' ', True)
                return True
            else:
                self.log_result(' ', False, response.text)
                return False
        except Exception as e:
            self.log_result(' ', False, str(e))
            return False
    
    def test_profile_update(self):
        """  """
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.patch(f'{BASE_URL}/users/profile/update/', 
                headers=headers,
                json={
                    'username': 'CEO'
                }
            )
            
            if response.status_code == 200:
                self.log_result(' ', True)
                return True
            else:
                self.log_result(' ', False, response.text)
                return False
        except Exception as e:
            self.log_result(' ', False, str(e))
            return False
    
    def run_all_tests(self):
        """  """
        print("=" * 50)
        print("VideoPlanet   ")
        print("=" * 50)
        
        #   
        if self.test_login():
            self.test_project_creation()
            self.test_ai_planning()
            self.test_planning_save()
            self.test_pdf_export()
            self.test_feedback()
            self.test_profile_update()
        
        #  
        print("\n" + "=" * 50)
        print("  ")
        print("=" * 50)
        print(f" : {self.results['total']}")
        print(f": {self.results['passed']}")
        print(f": {self.results['failed']}")
        print(f": {(self.results['passed'] / self.results['total'] * 100):.1f}%")
        
        if self.results['failed'] > 0:
            print("\n :")
            for detail in self.results['details']:
                if detail['status'] == 'FAIL':
                    print(f"- {detail['test']}: {detail['error']}")
        
        #  JSON  
        with open('comprehensive_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print("\n  comprehensive_test_results.json .")

if __name__ == '__main__':
    tester = VideoPlanetTester()
    tester.run_all_tests()