#!/usr/bin/env python3
"""
Integrated Health Check and Diagnostics Tool
통합 헬스체크 및 진단 도구 - DB 독립적 헬스체크 + DB 진단
"""

import os
import sys
import json
import time
import logging
import argparse
import multiprocessing
from datetime import datetime, timezone
from pathlib import Path

# 프로젝트 경로 설정
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class IntegratedHealthDiagnostics:
    """통합 헬스체크 및 진단 도구"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": self._get_environment_info(),
            "health_servers": {},
            "database_diagnostics": {},
            "recommendations": [],
            "summary": {}
        }
    
    def _get_environment_info(self):
        """환경 정보 수집"""
        env_info = {
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
            "working_directory": os.getcwd(),
            "railway_environment": os.environ.get('RAILWAY_ENVIRONMENT'),
            "port": os.environ.get('PORT', '8000'),
            "database_url_exists": bool(os.environ.get('DATABASE_URL')),
            "available_cores": multiprocessing.cpu_count(),
        }
        
        # Django 설정 확인
        try:
            import django
            env_info["django_version"] = django.get_version()
            env_info["django_available"] = True
        except ImportError:
            env_info["django_available"] = False
        
        return env_info
    
    def test_db_independent_server(self):
        """DB 독립적 헬스체크 서버 테스트"""
        logger.info("Testing DB Independent Health Server...")
        
        try:
            # 서버 임포트 및 초기화 테스트
            from db_independent_health import DatabaseIndependentHealthServer
            
            server = DatabaseIndependentHealthServer(port=0)  # 포트 0으로 테스트
            
            self.results["health_servers"]["db_independent"] = {
                "status": "available",
                "description": "Pure Python HTTP server, no dependencies",
                "startup_time_estimate": "< 1 second",
                "database_dependency": False,
                "django_dependency": False
            }
            
            logger.info("✅ DB Independent Server: Available")
            
        except Exception as e:
            error_msg = f"DB Independent Server failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results["health_servers"]["db_independent"] = {
                "status": "failed",
                "error": error_msg
            }
    
    def test_minimal_django_server(self):
        """최소 Django 헬스체크 서버 테스트"""
        logger.info("Testing Minimal Django Health Server...")
        
        try:
            # Django 최소 설정 테스트
            os.environ['DJANGO_SETTINGS_MODULE'] = 'minimal_health_settings'
            
            import django
            from django.core.wsgi import get_wsgi_application
            
            # Django 설정 로드 테스트
            django.setup()
            app = get_wsgi_application()
            
            self.results["health_servers"]["minimal_django"] = {
                "status": "available",
                "description": "Minimal Django with in-memory SQLite",
                "startup_time_estimate": "2-3 seconds",
                "database_dependency": False,  # 메모리 SQLite 사용
                "django_dependency": True,
                "django_version": django.get_version()
            }
            
            logger.info("✅ Minimal Django Server: Available")
            
        except Exception as e:
            error_msg = f"Minimal Django Server failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results["health_servers"]["minimal_django"] = {
                "status": "failed",
                "error": error_msg
            }
    
    def test_database_diagnostics(self):
        """데이터베이스 진단 테스트"""
        logger.info("Running Database Diagnostics...")
        
        try:
            from database_diagnostics import DatabaseDiagnostics
            
            db_diagnostics = DatabaseDiagnostics()
            
            # URL 체크만 실행 (연결 테스트는 제외)
            url_check = db_diagnostics.check_database_url()
            
            self.results["database_diagnostics"] = {
                "tool_available": True,
                "database_url_check": url_check,
                "connection_test": "not_performed",
                "note": "Full diagnostics available via database_diagnostics.py"
            }
            
            logger.info("✅ Database Diagnostics Tool: Available")
            
        except Exception as e:
            error_msg = f"Database diagnostics failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results["database_diagnostics"] = {
                "tool_available": False,
                "error": error_msg
            }
    
    def generate_recommendations(self):
        """권장사항 생성"""
        recommendations = []
        
        # 환경별 권장사항
        if self.results["environment"]["railway_environment"]:
            recommendations.append({
                "category": "Railway Deployment",
                "priority": "HIGH",
                "recommendation": "Use minimal Django server for fastest startup and reliability"
            })
        else:
            recommendations.append({
                "category": "Local Development",
                "priority": "MEDIUM",
                "recommendation": "Use DB independent server for development without DB setup"
            })
        
        # DB 연결 상황별 권장사항
        if self.results["environment"]["database_url_exists"]:
            recommendations.append({
                "category": "Database",
                "priority": "MEDIUM",
                "recommendation": "Run full database diagnostics to ensure connection stability"
            })
        else:
            recommendations.append({
                "category": "Database",
                "priority": "HIGH",
                "recommendation": "DATABASE_URL not configured - health checks will work but main app won't"
            })
        
        # 서버 가용성별 권장사항
        available_servers = [
            name for name, config in self.results["health_servers"].items()
            if config.get("status") == "available"
        ]
        
        if len(available_servers) > 1:
            recommendations.append({
                "category": "Redundancy",
                "priority": "LOW",
                "recommendation": f"Multiple health servers available: {', '.join(available_servers)}"
            })
        elif len(available_servers) == 1:
            recommendations.append({
                "category": "Reliability",
                "priority": "MEDIUM",
                "recommendation": f"Single health server available: {available_servers[0]}"
            })
        else:
            recommendations.append({
                "category": "Critical",
                "priority": "CRITICAL",
                "recommendation": "No health servers available - deployment will fail"
            })
        
        self.results["recommendations"] = recommendations
    
    def generate_summary(self):
        """요약 생성"""
        available_servers = sum(
            1 for config in self.results["health_servers"].values()
            if config.get("status") == "available"
        )
        
        db_diagnostics_available = self.results["database_diagnostics"].get("tool_available", False)
        
        critical_issues = [
            rec for rec in self.results["recommendations"]
            if rec.get("priority") == "CRITICAL"
        ]
        
        self.results["summary"] = {
            "health_servers_available": available_servers,
            "database_diagnostics_available": db_diagnostics_available,
            "database_url_configured": self.results["environment"]["database_url_exists"],
            "critical_issues": len(critical_issues),
            "deployment_ready": available_servers > 0 and len(critical_issues) == 0,
            "recommended_server": self._get_recommended_server()
        }
    
    def _get_recommended_server(self):
        """권장 서버 결정"""
        if self.results["environment"]["railway_environment"]:
            # Railway 환경에서는 minimal Django 권장
            if self.results["health_servers"].get("minimal_django", {}).get("status") == "available":
                return "minimal_django"
            elif self.results["health_servers"].get("db_independent", {}).get("status") == "available":
                return "db_independent"
        else:
            # 로컬 환경에서는 DB 독립적 서버 권장
            if self.results["health_servers"].get("db_independent", {}).get("status") == "available":
                return "db_independent"
            elif self.results["health_servers"].get("minimal_django", {}).get("status") == "available":
                return "minimal_django"
        
        return "none"
    
    def run_full_diagnostics(self):
        """전체 진단 실행"""
        logger.info("=" * 70)
        logger.info("INTEGRATED HEALTH CHECK AND DIAGNOSTICS")
        logger.info("=" * 70)
        
        try:
            # 1. 환경 정보
            logger.info("1. Environment Information")
            env = self.results["environment"]
            logger.info(f"   Python: {env['python_version']}")
            logger.info(f"   Platform: {env['platform']}")
            logger.info(f"   Railway: {env['railway_environment'] or 'Not detected'}")
            logger.info(f"   Database URL: {'Configured' if env['database_url_exists'] else 'Not configured'}")
            
            # 2. 헬스체크 서버 테스트
            logger.info("\n2. Health Check Servers")
            self.test_db_independent_server()
            self.test_minimal_django_server()
            
            # 3. 데이터베이스 진단
            logger.info("\n3. Database Diagnostics")
            self.test_database_diagnostics()
            
            # 4. 권장사항 생성
            logger.info("\n4. Generating Recommendations")
            self.generate_recommendations()
            
            # 5. 요약 생성
            self.generate_summary()
            
            logger.info("\n" + "=" * 70)
            logger.info("DIAGNOSTICS COMPLETED")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"❌ Diagnostics failed: {str(e)}")
            raise
        
        return self.results
    
    def print_summary_report(self):
        """요약 리포트 출력"""
        summary = self.results["summary"]
        
        logger.info("\n" + "=" * 50)
        logger.info("SUMMARY REPORT")
        logger.info("=" * 50)
        
        # 전반적 상태
        if summary["deployment_ready"]:
            logger.info("✅ DEPLOYMENT READY")
        else:
            logger.info("❌ DEPLOYMENT NOT READY")
        
        # 세부 정보
        logger.info(f"Health Servers Available: {summary['health_servers_available']}")
        logger.info(f"Database Diagnostics: {'Available' if summary['database_diagnostics_available'] else 'Not Available'}")
        logger.info(f"Database URL: {'Configured' if summary['database_url_configured'] else 'Not Configured'}")
        
        if summary["critical_issues"] > 0:
            logger.info(f"⚠️ Critical Issues: {summary['critical_issues']}")
        
        # 권장 서버
        recommended = summary["recommended_server"]
        if recommended != "none":
            logger.info(f"✅ Recommended Server: {recommended}")
        else:
            logger.info("❌ No suitable server available")
        
        # 권장사항
        if self.results["recommendations"]:
            logger.info("\nRECOMMENDATIONS:")
            for rec in self.results["recommendations"]:
                priority_emoji = {
                    "CRITICAL": "🚨",
                    "HIGH": "⚠️",
                    "MEDIUM": "ℹ️",
                    "LOW": "💡"
                }.get(rec["priority"], "•")
                
                logger.info(f"  {priority_emoji} [{rec['priority']}] {rec['category']}: {rec['recommendation']}")
        
        logger.info("=" * 50)
    
    def save_report(self, filename=None):
        """진단 리포트 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_diagnostics_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Report saved to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Failed to save report: {str(e)}")
            return None


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="Integrated Health Check and Diagnostics")
    parser.add_argument('--save', '-s', action='store_true', help='Save detailed report to file')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode (less output)')
    parser.add_argument('--output', '-o', help='Output filename for report')
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    try:
        diagnostics = IntegratedHealthDiagnostics()
        
        # 전체 진단 실행
        results = diagnostics.run_full_diagnostics()
        
        # 요약 리포트 출력
        diagnostics.print_summary_report()
        
        # 파일 저장
        if args.save or args.output:
            diagnostics.save_report(args.output)
        
        # 종료 코드 결정
        if results["summary"]["deployment_ready"]:
            logger.info("✅ All systems ready for deployment")
            sys.exit(0)
        else:
            logger.error("❌ Issues detected - review recommendations")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Diagnostics failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()