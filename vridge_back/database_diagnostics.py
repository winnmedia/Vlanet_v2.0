#!/usr/bin/env python3
"""
Database Diagnostics Tool
DATABASE_URL 파싱, 검증 및 연결 테스트 도구
"""

import os
import sys
import json
import time
import logging
import psycopg2
import psycopg2.extras
from urllib.parse import urlparse
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class DatabaseDiagnostics:
    """데이터베이스 진단 도구"""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database_url_check": {},
            "connection_test": {},
            "basic_queries": {},
            "performance_test": {},
            "error_details": []
        }
    
    def run_full_diagnostics(self) -> Dict[str, Any]:
        """전체 진단 실행"""
        logger.info("=" * 70)
        logger.info("DATABASE DIAGNOSTICS - FULL ANALYSIS")
        logger.info("=" * 70)
        
        try:
            # 1. DATABASE_URL 검증
            logger.info("1. Checking DATABASE_URL...")
            self.check_database_url()
            
            # 2. 연결 테스트
            logger.info("2. Testing database connection...")
            self.test_connection()
            
            # 3. 기본 쿼리 테스트
            logger.info("3. Running basic queries...")
            self.test_basic_queries()
            
            # 4. 성능 테스트
            logger.info("4. Running performance tests...")
            self.test_performance()
            
            logger.info("=" * 70)
            logger.info("✅ DIAGNOSTICS COMPLETED")
            logger.info("=" * 70)
            
        except Exception as e:
            error_msg = f"Diagnostics failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results["error_details"].append({
                "stage": "full_diagnostics",
                "error": error_msg,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return self.results
    
    def check_database_url(self) -> Dict[str, Any]:
        """DATABASE_URL 검증"""
        try:
            if not self.database_url:
                raise ValueError("DATABASE_URL environment variable is not set")
            
            # URL 파싱
            parsed = urlparse(self.database_url)
            
            url_info = {
                "exists": True,
                "scheme": parsed.scheme,
                "hostname": parsed.hostname,
                "port": parsed.port,
                "database": parsed.path.lstrip('/') if parsed.path else None,
                "username": parsed.username,
                "password_set": bool(parsed.password),
                "full_url_length": len(self.database_url),
                "is_postgresql": parsed.scheme.startswith('postgres')
            }
            
            # 검증
            validation = {
                "valid_scheme": parsed.scheme in ['postgresql', 'postgres'],
                "has_hostname": bool(parsed.hostname),
                "has_port": bool(parsed.port),
                "has_database": bool(parsed.path and parsed.path != '/'),
                "has_credentials": bool(parsed.username and parsed.password)
            }
            
            self.results["database_url_check"] = {
                "status": "success",
                "url_info": url_info,
                "validation": validation,
                "all_valid": all(validation.values())
            }
            
            logger.info(f"✅ DATABASE_URL: {parsed.scheme}://{parsed.username}:***@{parsed.hostname}:{parsed.port}{parsed.path}")
            logger.info(f"   Validation: {validation}")
            
        except Exception as e:
            error_msg = f"DATABASE_URL check failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results["database_url_check"] = {
                "status": "error",
                "error": error_msg
            }
            self.results["error_details"].append({
                "stage": "database_url_check",
                "error": error_msg,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return self.results["database_url_check"]
    
    def test_connection(self) -> Dict[str, Any]:
        """데이터베이스 연결 테스트"""
        if not self.database_url:
            error_msg = "Cannot test connection: DATABASE_URL not available"
            self.results["connection_test"] = {"status": "skipped", "error": error_msg}
            logger.warning(f"⚠️ {error_msg}")
            return self.results["connection_test"]
        
        try:
            start_time = time.time()
            
            # 연결 시도
            logger.info("   Attempting connection...")
            conn = psycopg2.connect(self.database_url)
            
            connection_time = time.time() - start_time
            
            # 연결 정보 수집
            with conn.cursor() as cursor:
                # PostgreSQL 버전
                cursor.execute("SELECT version();")
                pg_version = cursor.fetchone()[0]
                
                # 현재 데이터베이스
                cursor.execute("SELECT current_database();")
                current_db = cursor.fetchone()[0]
                
                # 현재 사용자
                cursor.execute("SELECT current_user;")
                current_user = cursor.fetchone()[0]
                
                # 연결 상태
                cursor.execute("SELECT pg_backend_pid();")
                backend_pid = cursor.fetchone()[0]
            
            conn.close()
            
            self.results["connection_test"] = {
                "status": "success",
                "connection_time_ms": round(connection_time * 1000, 2),
                "postgresql_version": pg_version.split(',')[0],  # 첫 번째 부분만
                "current_database": current_db,
                "current_user": current_user,
                "backend_pid": backend_pid,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Connection successful in {connection_time*1000:.1f}ms")
            logger.info(f"   Database: {current_db}, User: {current_user}")
            
        except psycopg2.OperationalError as e:
            error_msg = f"Connection failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results["connection_test"] = {
                "status": "failed",
                "error": error_msg,
                "error_type": "operational"
            }
            self.results["error_details"].append({
                "stage": "connection_test",
                "error": error_msg,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            error_msg = f"Unexpected connection error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results["connection_test"] = {
                "status": "error",
                "error": error_msg,
                "error_type": "unexpected"
            }
            self.results["error_details"].append({
                "stage": "connection_test",
                "error": error_msg,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return self.results["connection_test"]
    
    def test_basic_queries(self) -> Dict[str, Any]:
        """기본 쿼리 테스트"""
        if self.results["connection_test"].get("status") != "success":
            error_msg = "Cannot run queries: Connection test failed"
            self.results["basic_queries"] = {"status": "skipped", "error": error_msg}
            logger.warning(f"⚠️ {error_msg}")
            return self.results["basic_queries"]
        
        try:
            conn = psycopg2.connect(self.database_url)
            queries_results = {}
            
            test_queries = [
                ("current_timestamp", "SELECT current_timestamp;"),
                ("database_size", "SELECT pg_size_pretty(pg_database_size(current_database()));"),
                ("table_count", "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"),
                ("connection_count", "SELECT count(*) FROM pg_stat_activity;"),
                ("version_info", "SELECT version();")
            ]
            
            with conn.cursor() as cursor:
                for query_name, query in test_queries:
                    try:
                        start_time = time.time()
                        cursor.execute(query)
                        result = cursor.fetchone()
                        execution_time = time.time() - start_time
                        
                        queries_results[query_name] = {
                            "status": "success",
                            "result": str(result[0]) if result else None,
                            "execution_time_ms": round(execution_time * 1000, 2)
                        }
                        logger.info(f"   ✅ {query_name}: {result[0] if result else 'No result'}")
                        
                    except Exception as e:
                        error_msg = f"Query {query_name} failed: {str(e)}"
                        queries_results[query_name] = {
                            "status": "failed",
                            "error": error_msg
                        }
                        logger.error(f"   ❌ {error_msg}")
            
            conn.close()
            
            successful_queries = sum(1 for q in queries_results.values() if q["status"] == "success")
            total_queries = len(queries_results)
            
            self.results["basic_queries"] = {
                "status": "completed",
                "queries": queries_results,
                "summary": {
                    "successful": successful_queries,
                    "total": total_queries,
                    "success_rate": round((successful_queries / total_queries) * 100, 1)
                }
            }
            
            logger.info(f"✅ Basic queries: {successful_queries}/{total_queries} successful")
            
        except Exception as e:
            error_msg = f"Basic queries test failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results["basic_queries"] = {
                "status": "error",
                "error": error_msg
            }
            self.results["error_details"].append({
                "stage": "basic_queries",
                "error": error_msg,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return self.results["basic_queries"]
    
    def test_performance(self) -> Dict[str, Any]:
        """성능 테스트"""
        if self.results["connection_test"].get("status") != "success":
            error_msg = "Cannot run performance test: Connection test failed"
            self.results["performance_test"] = {"status": "skipped", "error": error_msg}
            logger.warning(f"⚠️ {error_msg}")
            return self.results["performance_test"]
        
        try:
            conn = psycopg2.connect(self.database_url)
            
            # 간단한 성능 테스트
            performance_results = {}
            
            # 1. 연결 시간 측정 (10회)
            connection_times = []
            for i in range(10):
                start_time = time.time()
                test_conn = psycopg2.connect(self.database_url)
                connection_time = time.time() - start_time
                connection_times.append(connection_time * 1000)  # ms로 변환
                test_conn.close()
            
            performance_results["connection_performance"] = {
                "avg_time_ms": round(sum(connection_times) / len(connection_times), 2),
                "min_time_ms": round(min(connection_times), 2),
                "max_time_ms": round(max(connection_times), 2),
                "samples": len(connection_times)
            }
            
            # 2. 쿼리 실행 시간 측정
            with conn.cursor() as cursor:
                query_times = []
                for i in range(5):
                    start_time = time.time()
                    cursor.execute("SELECT 1;")
                    cursor.fetchone()
                    query_time = time.time() - start_time
                    query_times.append(query_time * 1000)
                
                performance_results["query_performance"] = {
                    "avg_time_ms": round(sum(query_times) / len(query_times), 2),
                    "min_time_ms": round(min(query_times), 2),
                    "max_time_ms": round(max(query_times), 2),
                    "samples": len(query_times)
                }
            
            conn.close()
            
            self.results["performance_test"] = {
                "status": "completed",
                "results": performance_results,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Performance test completed")
            logger.info(f"   Avg connection: {performance_results['connection_performance']['avg_time_ms']:.1f}ms")
            logger.info(f"   Avg query: {performance_results['query_performance']['avg_time_ms']:.1f}ms")
            
        except Exception as e:
            error_msg = f"Performance test failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results["performance_test"] = {
                "status": "error",
                "error": error_msg
            }
            self.results["error_details"].append({
                "stage": "performance_test",
                "error": error_msg,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return self.results["performance_test"]
    
    def save_results(self, filename: Optional[str] = None) -> str:
        """진단 결과를 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"database_diagnostics_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Results saved to: {filename}")
            return filename
            
        except Exception as e:
            error_msg = f"Failed to save results: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return ""
    
    def print_summary(self):
        """진단 결과 요약 출력"""
        logger.info("\n" + "=" * 50)
        logger.info("DIAGNOSTIC SUMMARY")
        logger.info("=" * 50)
        
        # DATABASE_URL 체크
        url_check = self.results.get("database_url_check", {})
        if url_check.get("status") == "success":
            logger.info("✅ DATABASE_URL: Valid")
        else:
            logger.info("❌ DATABASE_URL: Invalid or missing")
        
        # 연결 테스트
        conn_test = self.results.get("connection_test", {})
        if conn_test.get("status") == "success":
            logger.info(f"✅ Connection: Success ({conn_test.get('connection_time_ms', 0)}ms)")
        else:
            logger.info("❌ Connection: Failed")
        
        # 기본 쿼리
        queries = self.results.get("basic_queries", {})
        if queries.get("status") == "completed":
            summary = queries.get("summary", {})
            logger.info(f"✅ Basic Queries: {summary.get('successful', 0)}/{summary.get('total', 0)} successful")
        else:
            logger.info("❌ Basic Queries: Failed or skipped")
        
        # 성능 테스트
        perf = self.results.get("performance_test", {})
        if perf.get("status") == "completed":
            logger.info("✅ Performance Test: Completed")
        else:
            logger.info("❌ Performance Test: Failed or skipped")
        
        # 에러 목록
        errors = self.results.get("error_details", [])
        if errors:
            logger.info(f"\n⚠️ Errors encountered: {len(errors)}")
            for error in errors:
                logger.info(f"   - {error['stage']}: {error['error']}")
        
        logger.info("=" * 50)


def main():
    """메인 함수"""
    try:
        diagnostics = DatabaseDiagnostics()
        
        # 전체 진단 실행
        results = diagnostics.run_full_diagnostics()
        
        # 결과 저장
        saved_file = diagnostics.save_results()
        
        # 요약 출력
        diagnostics.print_summary()
        
        # 결과에 따른 종료 코드
        has_critical_errors = (
            results.get("database_url_check", {}).get("status") != "success" or
            results.get("connection_test", {}).get("status") != "success"
        )
        
        if has_critical_errors:
            logger.error("❌ Critical database issues detected!")
            sys.exit(1)
        else:
            logger.info("✅ Database diagnostics completed successfully")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"❌ Diagnostics failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()