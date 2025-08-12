#!/usr/bin/env python3
"""
Railway Database Monitor
Railway 환경에서의 데이터베이스 모니터링 및 진단 도구
"""

import os
import sys
import json
import time
import logging
import signal
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from database_diagnostics import DatabaseDiagnostics


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class RailwayDBMonitor:
    """Railway 환경 데이터베이스 모니터"""
    
    def __init__(self):
        self.is_running = False
        self.monitor_thread = None
        self.diagnostics = DatabaseDiagnostics()
        self.monitoring_interval = 60  # 60초마다 체크
        self.results_history = []
        self.max_history = 100  # 최대 100개 기록 보관
    
    def start_monitoring(self):
        """모니터링 시작"""
        logger.info("=" * 60)
        logger.info("RAILWAY DATABASE MONITOR - STARTING")
        logger.info("=" * 60)
        
        self.is_running = True
        
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # 초기 진단
        logger.info("Running initial database diagnostics...")
        self._run_diagnostics_cycle()
        
        # 모니터링 스레드 시작
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info(f"✅ Monitoring started (interval: {self.monitoring_interval}s)")
        
        try:
            # 메인 스레드는 대기
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        self._stop_monitoring()
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        last_check = time.time()
        
        while self.is_running:
            try:
                current_time = time.time()
                
                if current_time - last_check >= self.monitoring_interval:
                    logger.info("-" * 40)
                    logger.info(f"Running scheduled diagnostic check...")
                    self._run_diagnostics_cycle()
                    last_check = current_time
                
                time.sleep(5)  # 5초마다 체크
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(10)
    
    def _run_diagnostics_cycle(self):
        """진단 사이클 실행"""
        try:
            start_time = time.time()
            
            # 새로운 진단 인스턴스 생성 (기존 결과 초기화)
            cycle_diagnostics = DatabaseDiagnostics()
            
            # 기본 체크만 실행 (빠른 체크)
            cycle_diagnostics.check_database_url()
            cycle_diagnostics.test_connection()
            
            # 연결이 성공한 경우에만 추가 테스트
            if cycle_diagnostics.results["connection_test"].get("status") == "success":
                cycle_diagnostics.test_basic_queries()
            
            execution_time = time.time() - start_time
            
            # 결과 요약
            result_summary = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "execution_time_ms": round(execution_time * 1000, 2),
                "database_url_ok": cycle_diagnostics.results["database_url_check"].get("status") == "success",
                "connection_ok": cycle_diagnostics.results["connection_test"].get("status") == "success",
                "queries_ok": cycle_diagnostics.results["basic_queries"].get("status") == "completed",
                "errors": len(cycle_diagnostics.results.get("error_details", []))
            }
            
            # 히스토리에 추가
            self.results_history.append(result_summary)
            if len(self.results_history) > self.max_history:
                self.results_history.pop(0)
            
            # 상태 로깅
            status_emoji = "✅" if result_summary["connection_ok"] else "❌"
            logger.info(f"{status_emoji} Check completed in {execution_time*1000:.1f}ms")
            
            if result_summary["errors"] > 0:
                logger.warning(f"⚠️ {result_summary['errors']} errors detected")
            
            # 에러가 있는 경우 상세 로그
            if cycle_diagnostics.results.get("error_details"):
                logger.info("Recent errors:")
                for error in cycle_diagnostics.results["error_details"][-3:]:  # 최근 3개만
                    logger.info(f"   - {error['stage']}: {error['error']}")
            
        except Exception as e:
            logger.error(f"Diagnostics cycle failed: {str(e)}")
            
            error_summary = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "execution_time_ms": -1,
                "database_url_ok": False,
                "connection_ok": False,
                "queries_ok": False,
                "errors": 1,
                "cycle_error": str(e)
            }
            self.results_history.append(error_summary)
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러"""
        logger.info(f"\n🛑 Received signal {signum}, shutting down...")
        self.is_running = False
    
    def _stop_monitoring(self):
        """모니터링 중단"""
        self.is_running = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            logger.info("Waiting for monitoring thread to stop...")
            self.monitor_thread.join(timeout=5)
        
        # 최종 리포트 생성
        self._generate_final_report()
        
        logger.info("✅ Database monitoring stopped")
    
    def _generate_final_report(self):
        """최종 리포트 생성"""
        if not self.results_history:
            logger.info("No monitoring data to report")
            return
        
        logger.info("\n" + "=" * 60)
        logger.info("MONITORING FINAL REPORT")
        logger.info("=" * 60)
        
        total_checks = len(self.results_history)
        successful_connections = sum(1 for r in self.results_history if r.get("connection_ok", False))
        total_errors = sum(r.get("errors", 0) for r in self.results_history)
        
        # 평균 실행 시간 계산 (유효한 값만)
        valid_times = [r["execution_time_ms"] for r in self.results_history if r["execution_time_ms"] > 0]
        avg_execution_time = sum(valid_times) / len(valid_times) if valid_times else 0
        
        logger.info(f"Total checks: {total_checks}")
        logger.info(f"Successful connections: {successful_connections}/{total_checks} ({successful_connections/total_checks*100:.1f}%)")
        logger.info(f"Total errors: {total_errors}")
        logger.info(f"Average execution time: {avg_execution_time:.1f}ms")
        
        # 최근 상태
        if self.results_history:
            latest = self.results_history[-1]
            status = "✅ Healthy" if latest.get("connection_ok", False) else "❌ Unhealthy"
            logger.info(f"Latest status: {status}")
        
        # 히스토리 파일 저장
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_file = f"railway_db_monitor_{timestamp}.json"
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "monitoring_summary": {
                        "total_checks": total_checks,
                        "successful_connections": successful_connections,
                        "success_rate": successful_connections/total_checks*100 if total_checks > 0 else 0,
                        "total_errors": total_errors,
                        "average_execution_time_ms": round(avg_execution_time, 2)
                    },
                    "history": self.results_history
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Monitoring history saved to: {history_file}")
            
        except Exception as e:
            logger.error(f"Failed to save monitoring history: {str(e)}")
        
        logger.info("=" * 60)
    
    def run_single_check(self):
        """단일 체크 실행 (모니터링 없이)"""
        logger.info("=" * 60)
        logger.info("RAILWAY DATABASE SINGLE CHECK")
        logger.info("=" * 60)
        
        diagnostics = DatabaseDiagnostics()
        results = diagnostics.run_full_diagnostics()
        
        # 결과 저장
        diagnostics.save_results()
        diagnostics.print_summary()
        
        return results
    
    def check_railway_environment(self):
        """Railway 환경 체크"""
        logger.info("=" * 60)
        logger.info("RAILWAY ENVIRONMENT CHECK")
        logger.info("=" * 60)
        
        railway_vars = [
            'RAILWAY_ENVIRONMENT',
            'RAILWAY_PROJECT_ID',
            'RAILWAY_SERVICE_ID',
            'RAILWAY_DEPLOYMENT_ID',
            'RAILWAY_REPLICA_ID',
            'DATABASE_URL',
            'DATABASE_PRIVATE_URL',
            'PORT'
        ]
        
        env_info = {}
        for var in railway_vars:
            value = os.environ.get(var)
            if value:
                if 'DATABASE' in var:
                    # DATABASE URL 마스킹
                    from urllib.parse import urlparse
                    try:
                        parsed = urlparse(value)
                        masked = f"{parsed.scheme}://***:***@{parsed.hostname}:{parsed.port}{parsed.path}"
                        env_info[var] = masked
                    except:
                        env_info[var] = "***MASKED***"
                else:
                    env_info[var] = value
            else:
                env_info[var] = "not set"
        
        logger.info("Railway Environment Variables:")
        for var, value in env_info.items():
            logger.info(f"  {var}: {value}")
        
        # Railway 환경인지 확인
        is_railway = bool(os.environ.get('RAILWAY_ENVIRONMENT'))
        logger.info(f"\nRunning in Railway: {'Yes' if is_railway else 'No'}")
        
        if is_railway:
            logger.info(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')}")
        
        logger.info("=" * 60)
        
        return env_info


def main():
    """메인 함수"""
    try:
        monitor = RailwayDBMonitor()
        
        # 명령행 인자 처리
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == 'monitor':
                # 연속 모니터링
                monitor.start_monitoring()
            elif command == 'check':
                # 단일 체크
                monitor.run_single_check()
            elif command == 'env':
                # 환경 체크
                monitor.check_railway_environment()
            else:
                logger.error(f"Unknown command: {command}")
                logger.info("Usage: python railway_db_monitor.py [monitor|check|env]")
                sys.exit(1)
        else:
            # 기본값: 단일 체크
            monitor.run_single_check()
            
    except Exception as e:
        logger.error(f"❌ Monitor failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()