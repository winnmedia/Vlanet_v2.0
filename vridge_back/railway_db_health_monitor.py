#!/usr/bin/env python3
"""
Railway 프로덕션 데이터베이스 헬스 모니터링 시스템
Victoria - DBRE (Database Reliability Engineer)

- 실시간 연결 상태 모니터링
- 자동 복구 메커니즘
- 연결 풀 최적화
- 성능 메트릭 수집
"""

import os
import sys
import time
import logging
import traceback
from datetime import datetime, timedelta
from threading import Thread, Event
import django
from django.db import connections, transaction
from django.core.management.base import BaseCommand

# Railway 설정 강제
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/railway_db_health.log', mode='a')
    ]
)
logger = logging.getLogger('railway_db_health')

class RailwayDatabaseHealthMonitor:
    """Railway 데이터베이스 헬스 모니터"""
    
    def __init__(self):
        self.is_running = False
        self.stop_event = Event()
        self.last_health_check = None
        self.connection_errors = 0
        self.max_connection_errors = 5
        self.health_check_interval = 30  # 30초마다 체크
        
        # 성능 메트릭
        self.metrics = {
            'connection_time': [],
            'query_time': [],
            'error_count': 0,
            'last_error': None,
            'uptime_start': datetime.now()
        }
    
    def setup_django(self):
        """Django 환경 설정"""
        try:
            django.setup()
            logger.info("Django 환경 설정 완료")
            return True
        except Exception as e:
            logger.error(f"Django 환경 설정 실패: {e}")
            return False
    
    def test_connection(self, alias='default', timeout=10):
        """데이터베이스 연결 테스트"""
        try:
            start_time = time.time()
            
            connection = connections[alias]
            
            # 기존 연결이 있다면 재사용 방지를 위해 닫기
            if connection.connection:
                connection.close()
            
            # 새 연결로 테스트
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 as health_check, NOW() as current_time")
                result = cursor.fetchone()
                
            connection_time = (time.time() - start_time) * 1000
            self.metrics['connection_time'].append(connection_time)
            
            # 메트릭 리스트 크기 제한 (최근 100개만 유지)
            if len(self.metrics['connection_time']) > 100:
                self.metrics['connection_time'].pop(0)
            
            logger.debug(f"데이터베이스 연결 성공 ({connection_time:.2f}ms)")
            return True, connection_time
            
        except Exception as e:
            self.metrics['error_count'] += 1
            self.metrics['last_error'] = str(e)
            logger.error(f"데이터베이스 연결 실패: {e}")
            return False, None
    
    def test_query_performance(self):
        """쿼리 성능 테스트"""
        try:
            start_time = time.time()
            
            # 실제 users 테이블 쿼리
            from users.models import User
            user_count = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            
            query_time = (time.time() - start_time) * 1000
            self.metrics['query_time'].append(query_time)
            
            if len(self.metrics['query_time']) > 100:
                self.metrics['query_time'].pop(0)
            
            logger.debug(f"쿼리 성능 테스트 완료 ({query_time:.2f}ms) - 사용자: {user_count}, 활성: {active_users}")
            return True, query_time, {'total_users': user_count, 'active_users': active_users}
            
        except Exception as e:
            logger.error(f"쿼리 성능 테스트 실패: {e}")
            return False, None, None
    
    def check_migration_status(self):
        """마이그레이션 상태 확인"""
        try:
            from django.db import connection
            
            with connection.cursor() as cursor:
                # 최근 마이그레이션 확인
                cursor.execute("""
                    SELECT app, name, applied 
                    FROM django_migrations 
                    WHERE app = 'users' 
                    ORDER BY applied DESC 
                    LIMIT 5
                """)
                recent_migrations = cursor.fetchall()
                
                logger.debug(f"최근 마이그레이션 {len(recent_migrations)}개 확인됨")
                return True, recent_migrations
                
        except Exception as e:
            logger.error(f"마이그레이션 상태 확인 실패: {e}")
            return False, None
    
    def repair_connections(self):
        """연결 복구 시도"""
        logger.info("데이터베이스 연결 복구 시도 중...")
        
        try:
            # 모든 연결 닫기
            for alias in connections:
                connections[alias].close()
            
            # 연결 재시도
            time.sleep(2)  # 잠깐 대기
            
            success, connection_time = self.test_connection()
            if success:
                self.connection_errors = 0
                logger.info(f"데이터베이스 연결 복구 성공 ({connection_time:.2f}ms)")
                return True
            else:
                logger.error("데이터베이스 연결 복구 실패")
                return False
                
        except Exception as e:
            logger.error(f"연결 복구 중 오류: {e}")
            return False
    
    def get_health_status(self):
        """전체 헬스 상태 반환"""
        try:
            # 연결 테스트
            connection_ok, connection_time = self.test_connection()
            
            # 쿼리 성능 테스트
            query_ok, query_time, query_stats = self.test_query_performance()
            
            # 마이그레이션 상태
            migration_ok, migrations = self.check_migration_status()
            
            # 전체 상태 계산
            overall_health = all([connection_ok, query_ok, migration_ok])
            
            # 평균 성능 계산
            avg_connection_time = sum(self.metrics['connection_time'][-10:]) / len(self.metrics['connection_time'][-10:]) if self.metrics['connection_time'] else 0
            avg_query_time = sum(self.metrics['query_time'][-10:]) / len(self.metrics['query_time'][-10:]) if self.metrics['query_time'] else 0
            
            uptime = datetime.now() - self.metrics['uptime_start']
            
            health_report = {
                'status': 'healthy' if overall_health else 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': int(uptime.total_seconds()),
                'connection': {
                    'status': 'ok' if connection_ok else 'error',
                    'time_ms': connection_time,
                    'avg_time_ms': round(avg_connection_time, 2)
                },
                'queries': {
                    'status': 'ok' if query_ok else 'error',
                    'time_ms': query_time,
                    'avg_time_ms': round(avg_query_time, 2),
                    'stats': query_stats
                },
                'migrations': {
                    'status': 'ok' if migration_ok else 'error',
                    'recent_count': len(migrations) if migrations else 0
                },
                'errors': {
                    'total_count': self.metrics['error_count'],
                    'connection_errors': self.connection_errors,
                    'last_error': self.metrics['last_error']
                }
            }
            
            return health_report
            
        except Exception as e:
            logger.error(f"헬스 상태 확인 실패: {e}")
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def health_check_loop(self):
        """헬스체크 루프"""
        logger.info("데이터베이스 헬스체크 루프 시작")
        
        while not self.stop_event.is_set():
            try:
                health_status = self.get_health_status()
                
                if health_status['status'] == 'healthy':
                    if self.connection_errors > 0:
                        logger.info("데이터베이스 상태 복구됨")
                        self.connection_errors = 0
                else:
                    self.connection_errors += 1
                    logger.warning(f"데이터베이스 헬스체크 실패 ({self.connection_errors}/{self.max_connection_errors})")
                    
                    # 최대 오류 횟수 도달 시 복구 시도
                    if self.connection_errors >= self.max_connection_errors:
                        if self.repair_connections():
                            self.connection_errors = 0
                        else:
                            logger.critical("데이터베이스 복구 실패 - 서비스 재시작 필요할 수 있음")
                
                self.last_health_check = datetime.now()
                
                # 주기적으로 상태 로그 출력
                if int(time.time()) % 300 == 0:  # 5분마다
                    logger.info(f"데이터베이스 상태: {health_status['status']} | "
                              f"연결: {health_status['connection']['avg_time_ms']:.1f}ms | "
                              f"쿼리: {health_status['queries']['avg_time_ms']:.1f}ms | "
                              f"오류: {health_status['errors']['total_count']}")
                
            except Exception as e:
                logger.error(f"헬스체크 루프 오류: {e}")
                traceback.print_exc()
            
            # 다음 체크까지 대기
            self.stop_event.wait(self.health_check_interval)
        
        logger.info("데이터베이스 헬스체크 루프 종료")
    
    def start_monitoring(self):
        """모니터링 시작"""
        if self.is_running:
            logger.warning("모니터링이 이미 실행 중입니다")
            return
        
        if not self.setup_django():
            logger.error("Django 설정 실패 - 모니터링 시작 불가")
            return
        
        self.is_running = True
        self.stop_event.clear()
        
        # 백그라운드 스레드로 헬스체크 시작
        health_thread = Thread(target=self.health_check_loop, daemon=True)
        health_thread.start()
        
        logger.info("데이터베이스 헬스 모니터링 시작됨")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.stop_event.set()
        logger.info("데이터베이스 헬스 모니터링 중지됨")

class Command(BaseCommand):
    """Django 관리 명령어로 실행 가능"""
    help = 'Railway 데이터베이스 헬스 모니터링 실행'
    
    def add_arguments(self, parser):
        parser.add_argument('--duration', type=int, default=0, 
                          help='모니터링 실행 시간 (초, 0=무한정)')
        parser.add_argument('--interval', type=int, default=30,
                          help='헬스체크 간격 (초)')
    
    def handle(self, *args, **options):
        monitor = RailwayDatabaseHealthMonitor()
        monitor.health_check_interval = options['interval']
        
        try:
            monitor.start_monitoring()
            
            if options['duration'] > 0:
                self.stdout.write(f"{options['duration']}초 동안 모니터링 실행...")
                time.sleep(options['duration'])
                monitor.stop_monitoring()
            else:
                self.stdout.write("무한 모니터링 시작 (Ctrl+C로 중지)")
                while True:
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            self.stdout.write("\n모니터링 중지 요청됨")
            monitor.stop_monitoring()
        except Exception as e:
            self.stdout.write(f"오류 발생: {e}")
            monitor.stop_monitoring()

def main():
    """직접 실행 시 사용"""
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # 테스트 모드
        monitor = RailwayDatabaseHealthMonitor()
        if monitor.setup_django():
            health_status = monitor.get_health_status()
            print(f"데이터베이스 상태: {health_status}")
        return
    
    # 대화형 모드
    monitor = RailwayDatabaseHealthMonitor()
    
    try:
        print("Railway 데이터베이스 헬스 모니터링 시작")
        print("종료하려면 Ctrl+C를 누르세요")
        
        monitor.start_monitoring()
        
        while True:
            time.sleep(60)  # 1분마다 상태 확인
            if monitor.last_health_check:
                elapsed = datetime.now() - monitor.last_health_check
                if elapsed > timedelta(seconds=120):  # 2분 이상 응답 없음
                    logger.warning("헬스체크가 응답하지 않습니다")
                    
    except KeyboardInterrupt:
        print("\n모니터링 중지 중...")
        monitor.stop_monitoring()
        print("모니터링이 중지되었습니다")

if __name__ == "__main__":
    main()