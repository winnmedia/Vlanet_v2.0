#!/usr/bin/env python3
"""
Railway 배포 모니터링 및 헬스체크 스크립트
배포 후 새로운 회원가입 시스템이 제대로 작동하는지 확인합니다.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Tuple


class RailwayDeploymentMonitor:
    """Railway 배포 모니터링 클래스"""
    
    def __init__(self, railway_url: str = None):
        # Railway URL을 여기에 설정하세요
        self.railway_url = railway_url or "https://your-railway-app.railway.app"
        self.test_results = []
        
        # 테스트용 데이터
        timestamp = int(time.time())
        self.test_data = {
            'email': f'railway_test_{timestamp}@example.com',
            'nickname': f'railwaytest_{timestamp}',
            'password': 'TestPassword123!',
            'full_name': 'Railway 테스트',
            'company': 'Railway Test Company',
            'position': 'Deployment Monitor',
            'phone': '010-0000-0000'
        }
        
    def log_test(self, test_name: str, success: bool, message: str, details: Dict = None):
        """테스트 결과 로깅"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'test_name': test_name,
            'success': success,
            'message': message,
            'details': details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2, ensure_ascii=False)}")
    
    def make_request(self, endpoint: str, method: str = 'POST', data: Dict = None) -> Tuple[bool, Dict]:
        """API 요청 실행"""
        url = f"{self.railway_url}/api/auth{endpoint}"
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Railway-Deployment-Monitor/1.0'
            }
            
            if method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)
            
            # 응답 처리
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {'error': 'Invalid JSON response', 'text': response.text}
            
            return True, {
                'status_code': response.status_code,
                'data': response_data,
                'headers': dict(response.headers)
            }
            
        except requests.exceptions.RequestException as e:
            return False, {'error': str(e)}
    
    def test_basic_health(self):
        """기본 헬스체크"""
        try:
            response = requests.get(f"{self.railway_url}/health/", timeout=10)
            if response.status_code == 200:
                self.log_test(
                    "Railway 헬스체크", 
                    True, 
                    "Railway 애플리케이션이 정상적으로 실행 중입니다.",
                    {"status_code": response.status_code, "response": response.json()}
                )
                return True
            else:
                self.log_test(
                    "Railway 헬스체크", 
                    False, 
                    f"헬스체크 실패: HTTP {response.status_code}",
                    {"status_code": response.status_code, "text": response.text}
                )
                return False
        except Exception as e:
            self.log_test("Railway 헬스체크", False, f"헬스체크 요청 실패: {str(e)}")
            return False
    
    def test_enhanced_signup_endpoints(self):
        """Enhanced signup 엔드포인트 테스트"""
        print("\n🔸 Enhanced Signup API 엔드포인트 테스트")
        
        # 1. 이메일 체크 및 인증 코드 발송
        success, response = self.make_request('/check-email-verify/', data={
            'email': self.test_data['email']
        })
        
        if success and response['status_code'] == 200:
            data = response['data']
            if data.get('success') and data.get('available'):
                self.log_test(
                    "이메일 체크 & 인증 코드 발송", 
                    True, 
                    "API 엔드포인트가 정상 작동합니다.",
                    data
                )
            else:
                self.log_test(
                    "이메일 체크 & 인증 코드 발송", 
                    False, 
                    "예상과 다른 응답 구조",
                    data
                )
        else:
            self.log_test(
                "이메일 체크 & 인증 코드 발송", 
                False, 
                f"API 호출 실패: {response}"
            )
        
        # 2. 닉네임 체크
        success, response = self.make_request('/check-nickname/', data={
            'nickname': self.test_data['nickname']
        })
        
        if success and response['status_code'] == 200:
            data = response['data']
            if data.get('success'):
                self.log_test(
                    "닉네임 중복 체크", 
                    True, 
                    "API 엔드포인트가 정상 작동합니다.",
                    data
                )
            else:
                self.log_test(
                    "닉네임 중복 체크", 
                    False, 
                    "예상과 다른 응답 구조",
                    data
                )
        else:
            self.log_test(
                "닉네임 중복 체크", 
                False, 
                f"API 호출 실패: {response}"
            )
    
    def test_cors_configuration(self):
        """CORS 설정 테스트"""
        try:
            # OPTIONS 요청으로 CORS 헤더 확인
            response = requests.options(
                f"{self.railway_url}/api/auth/check-email-verify/",
                headers={
                    'Origin': 'https://v-planet.vercel.app',
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type'
                },
                timeout=10
            )
            
            cors_headers = {
                'access-control-allow-origin': response.headers.get('Access-Control-Allow-Origin'),
                'access-control-allow-methods': response.headers.get('Access-Control-Allow-Methods'),
                'access-control-allow-headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            if response.status_code in [200, 204] and cors_headers['access-control-allow-origin']:
                self.log_test(
                    "CORS 설정", 
                    True, 
                    "CORS가 올바르게 설정되었습니다.",
                    cors_headers
                )
            else:
                self.log_test(
                    "CORS 설정", 
                    False, 
                    f"CORS 설정 문제: HTTP {response.status_code}",
                    cors_headers
                )
                
        except Exception as e:
            self.log_test("CORS 설정", False, f"CORS 테스트 실패: {str(e)}")
    
    def test_database_connectivity(self):
        """데이터베이스 연결 테스트 (간접적)"""
        # 닉네임 체크 API를 통해 DB 연결 상태 확인
        success, response = self.make_request('/check-nickname/', data={
            'nickname': f'db_test_{int(time.time())}'
        })
        
        if success and response['status_code'] == 200:
            self.log_test(
                "데이터베이스 연결", 
                True, 
                "데이터베이스 연결이 정상입니다.",
                {"api_response": response['data']}
            )
        else:
            self.log_test(
                "데이터베이스 연결", 
                False, 
                "데이터베이스 연결에 문제가 있을 수 있습니다.",
                response
            )
    
    def monitor_deployment(self):
        """전체 배포 모니터링 실행"""
        print("🚀 Railway 배포 모니터링 시작")
        print(f"대상 URL: {self.railway_url}")
        print("=" * 60)
        
        # 1. 기본 헬스체크
        health_ok = self.test_basic_health()
        if not health_ok:
            print("\n❌ 기본 헬스체크 실패로 인해 추가 테스트를 건너뜁니다.")
            self.print_summary()
            return False
        
        # 2. Enhanced signup API 테스트
        self.test_enhanced_signup_endpoints()
        
        # 3. CORS 설정 테스트
        print("\n🔸 CORS 설정 테스트")
        self.test_cors_configuration()
        
        # 4. 데이터베이스 연결 테스트
        print("\n🔸 데이터베이스 연결 테스트")
        self.test_database_connectivity()
        
        # 결과 요약
        self.print_summary()
        
        # 성공률 확인
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return success_rate >= 80  # 80% 이상 성공률을 요구
    
    def print_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("📊 Railway 배포 모니터링 결과 요약")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests} ✅")
        print(f"실패: {failed_tests} ❌")
        print(f"성공률: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 실패한 테스트:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        # 배포 상태 판정
        success_rate = (passed_tests/total_tests*100) if total_tests > 0 else 0
        if success_rate >= 80:
            print(f"\n🎉 배포 성공! Enhanced signup 시스템이 Railway에서 정상 작동합니다.")
        else:
            print(f"\n⚠️ 배포에 문제가 있을 수 있습니다. 실패한 테스트를 확인해주세요.")
        
        # JSON 결과 파일 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'railway_deployment_monitor_{timestamp}.json'
        
        monitor_summary = {
            'railway_url': self.railway_url,
            'test_data': self.test_data,
            'results': self.test_results,
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': success_rate,
                'deployment_status': 'SUCCESS' if success_rate >= 80 else 'ISSUES_DETECTED'
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(monitor_summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 상세 결과가 {filename}에 저장되었습니다.")


def main():
    """메인 실행 함수"""
    print("Railway URL을 입력해주세요 (예: https://your-app.railway.app):")
    railway_url = input().strip()
    
    if not railway_url:
        print("❌ Railway URL이 입력되지 않았습니다.")
        return
    
    if not railway_url.startswith('http'):
        railway_url = f"https://{railway_url}"
    
    monitor = RailwayDeploymentMonitor(railway_url)
    success = monitor.monitor_deployment()
    
    if success:
        print("\n✅ Railway 배포 모니터링 완료!")
    else:
        print("\n🔧 배포에 문제가 발견되었습니다. 로그를 확인해주세요.")


if __name__ == "__main__":
    main()