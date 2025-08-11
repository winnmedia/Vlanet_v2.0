#!/usr/bin/env python3
"""
VideoPlanet Django Integration Automated Test Suite
Quality Assurance Comprehensive Testing Framework
"""

import os
import sys
import time
import json
import asyncio
import requests
import threading
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = os.environ.get('TEST_BASE_URL', 'https://videoplanet.up.railway.app')
LOCAL_URL = os.environ.get('LOCAL_URL', 'http://localhost:8000')
TEST_MODE = os.environ.get('TEST_MODE', 'production')  # production, staging, local

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    category: str
    status: str  # PASS, FAIL, ERROR, SKIP
    duration: float
    message: str
    details: Dict = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class QualityAssuranceTestSuite:
    """Comprehensive QA Test Suite for Django Integration"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = []
        self.start_time = None
        self.session = requests.Session()
        
    def run_all_tests(self) -> Dict:
        """Execute all test categories"""
        self.start_time = time.time()
        logger.info(f"Starting QA Test Suite for {self.base_url}")
        
        test_categories = [
            ('Functional', self.run_functional_tests),
            ('Performance', self.run_performance_tests),
            ('Security', self.run_security_tests),
            ('Reliability', self.run_reliability_tests),
            ('Integration', self.run_integration_tests),
        ]
        
        for category, test_func in test_categories:
            logger.info(f"Running {category} tests...")
            try:
                test_func()
            except Exception as e:
                logger.error(f"Error in {category} tests: {e}")
                self.results.append(TestResult(
                    test_name=f"{category}_Suite",
                    category=category,
                    status="ERROR",
                    duration=0,
                    message=str(e)
                ))
        
        return self.generate_report()
    
    # ============= FUNCTIONAL TESTS =============
    
    def run_functional_tests(self):
        """Test core functionality"""
        
        # Test 1: Health Check Response
        result = self._test_health_check()
        self.results.append(result)
        
        # Test 2: API Ready Check
        result = self._test_ready_endpoint()
        self.results.append(result)
        
        # Test 3: CORS Headers
        result = self._test_cors_headers()
        self.results.append(result)
        
        # Test 4: API Proxy Functionality
        result = self._test_api_proxy()
        self.results.append(result)
        
        # Test 5: Error Handling
        result = self._test_error_handling()
        self.results.append(result)
    
    def _test_health_check(self) -> TestResult:
        """Test health check endpoint"""
        start = time.time()
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            duration = time.time() - start
            
            if response.status_code == 200:
                return TestResult(
                    test_name="Health Check",
                    category="Functional",
                    status="PASS",
                    duration=duration,
                    message="Health check successful",
                    details={"status_code": response.status_code, "response_time_ms": duration * 1000}
                )
            else:
                return TestResult(
                    test_name="Health Check",
                    category="Functional",
                    status="FAIL",
                    duration=duration,
                    message=f"Unexpected status code: {response.status_code}",
                    details={"status_code": response.status_code}
                )
        except Exception as e:
            return TestResult(
                test_name="Health Check",
                category="Functional",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    def _test_ready_endpoint(self) -> TestResult:
        """Test Django readiness"""
        start = time.time()
        try:
            response = self.session.get(f"{self.base_url}/ready", timeout=10)
            duration = time.time() - start
            
            if response.status_code == 200:
                return TestResult(
                    test_name="Django Ready Check",
                    category="Functional",
                    status="PASS",
                    duration=duration,
                    message="Django is ready",
                    details={"response": response.text}
                )
            elif response.status_code == 503:
                return TestResult(
                    test_name="Django Ready Check",
                    category="Functional",
                    status="FAIL",
                    duration=duration,
                    message="Django not ready",
                    details={"response": response.text}
                )
            else:
                return TestResult(
                    test_name="Django Ready Check",
                    category="Functional",
                    status="FAIL",
                    duration=duration,
                    message=f"Unexpected status: {response.status_code}"
                )
        except Exception as e:
            return TestResult(
                test_name="Django Ready Check",
                category="Functional",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    def _test_cors_headers(self) -> TestResult:
        """Test CORS configuration"""
        start = time.time()
        try:
            headers = {
                'Origin': 'https://vlanet.net',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            response = self.session.options(f"{self.base_url}/api/test", headers=headers, timeout=5)
            duration = time.time() - start
            
            cors_headers = {
                'allow_origin': response.headers.get('Access-Control-Allow-Origin'),
                'allow_methods': response.headers.get('Access-Control-Allow-Methods'),
                'allow_headers': response.headers.get('Access-Control-Allow-Headers'),
                'allow_credentials': response.headers.get('Access-Control-Allow-Credentials'),
            }
            
            # Check for security issue: wildcard CORS
            if cors_headers['allow_origin'] == '*':
                return TestResult(
                    test_name="CORS Security Check",
                    category="Functional",
                    status="FAIL",
                    duration=duration,
                    message="CRITICAL: CORS allows all origins (security risk)",
                    details=cors_headers
                )
            
            return TestResult(
                test_name="CORS Security Check",
                category="Functional",
                status="PASS",
                duration=duration,
                message="CORS properly configured",
                details=cors_headers
            )
        except Exception as e:
            return TestResult(
                test_name="CORS Security Check",
                category="Functional",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    def _test_api_proxy(self) -> TestResult:
        """Test API proxy functionality"""
        start = time.time()
        try:
            # Try to access a simple API endpoint
            response = self.session.get(f"{self.base_url}/api/health/", timeout=10)
            duration = time.time() - start
            
            if response.status_code < 500:
                return TestResult(
                    test_name="API Proxy",
                    category="Functional",
                    status="PASS",
                    duration=duration,
                    message="API proxy working",
                    details={"status_code": response.status_code}
                )
            else:
                return TestResult(
                    test_name="API Proxy",
                    category="Functional",
                    status="FAIL",
                    duration=duration,
                    message=f"API proxy error: {response.status_code}",
                    details={"status_code": response.status_code, "response": response.text[:200]}
                )
        except Exception as e:
            return TestResult(
                test_name="API Proxy",
                category="Functional",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    def _test_error_handling(self) -> TestResult:
        """Test error handling for invalid endpoints"""
        start = time.time()
        try:
            response = self.session.get(f"{self.base_url}/invalid/endpoint", timeout=5)
            duration = time.time() - start
            
            if response.status_code == 404:
                return TestResult(
                    test_name="Error Handling",
                    category="Functional",
                    status="PASS",
                    duration=duration,
                    message="Proper 404 handling",
                    details={"status_code": response.status_code}
                )
            else:
                return TestResult(
                    test_name="Error Handling",
                    category="Functional",
                    status="FAIL",
                    duration=duration,
                    message=f"Unexpected error handling: {response.status_code}",
                    details={"status_code": response.status_code}
                )
        except Exception as e:
            return TestResult(
                test_name="Error Handling",
                category="Functional",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    # ============= PERFORMANCE TESTS =============
    
    def run_performance_tests(self):
        """Test performance characteristics"""
        
        # Test 1: Health Check Latency
        result = self._test_health_check_latency()
        self.results.append(result)
        
        # Test 2: Concurrent Requests
        result = self._test_concurrent_requests()
        self.results.append(result)
        
        # Test 3: Sustained Load
        result = self._test_sustained_load()
        self.results.append(result)
        
        # Test 4: Memory Usage Pattern
        result = self._test_memory_pattern()
        self.results.append(result)
    
    def _test_health_check_latency(self) -> TestResult:
        """Test health check response time"""
        latencies = []
        start = time.time()
        
        try:
            for _ in range(10):
                req_start = time.time()
                response = self.session.get(f"{self.base_url}/health", timeout=5)
                latency = (time.time() - req_start) * 1000  # Convert to ms
                latencies.append(latency)
            
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            min_latency = min(latencies)
            
            if avg_latency < 100:  # Target: < 100ms
                status = "PASS"
                message = f"Average latency: {avg_latency:.2f}ms"
            else:
                status = "FAIL"
                message = f"High latency: {avg_latency:.2f}ms (target: <100ms)"
            
            return TestResult(
                test_name="Health Check Latency",
                category="Performance",
                status=status,
                duration=time.time() - start,
                message=message,
                details={
                    "avg_latency_ms": avg_latency,
                    "max_latency_ms": max_latency,
                    "min_latency_ms": min_latency,
                    "samples": len(latencies)
                }
            )
        except Exception as e:
            return TestResult(
                test_name="Health Check Latency",
                category="Performance",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    def _test_concurrent_requests(self) -> TestResult:
        """Test handling of concurrent requests"""
        start = time.time()
        concurrent_count = 50
        success_count = 0
        error_count = 0
        
        def make_request():
            try:
                response = requests.get(f"{self.base_url}/health", timeout=10)
                return response.status_code == 200
            except:
                return False
        
        try:
            with ThreadPoolExecutor(max_workers=concurrent_count) as executor:
                futures = [executor.submit(make_request) for _ in range(concurrent_count)]
                for future in as_completed(futures):
                    if future.result():
                        success_count += 1
                    else:
                        error_count += 1
            
            success_rate = success_count / concurrent_count
            
            if success_rate >= 0.95:  # Target: 95% success
                status = "PASS"
                message = f"Success rate: {success_rate*100:.1f}%"
            else:
                status = "FAIL"
                message = f"Low success rate: {success_rate*100:.1f}% (target: ≥95%)"
            
            return TestResult(
                test_name="Concurrent Requests",
                category="Performance",
                status=status,
                duration=time.time() - start,
                message=message,
                details={
                    "total_requests": concurrent_count,
                    "successful": success_count,
                    "failed": error_count,
                    "success_rate": success_rate
                }
            )
        except Exception as e:
            return TestResult(
                test_name="Concurrent Requests",
                category="Performance",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    def _test_sustained_load(self) -> TestResult:
        """Test sustained load handling"""
        start = time.time()
        duration_seconds = 30
        request_interval = 0.1  # 10 requests per second
        
        success_count = 0
        error_count = 0
        latencies = []
        
        try:
            end_time = time.time() + duration_seconds
            while time.time() < end_time:
                req_start = time.time()
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=5)
                    if response.status_code == 200:
                        success_count += 1
                    else:
                        error_count += 1
                    latencies.append((time.time() - req_start) * 1000)
                except:
                    error_count += 1
                
                time.sleep(request_interval)
            
            total_requests = success_count + error_count
            success_rate = success_count / total_requests if total_requests > 0 else 0
            avg_latency = sum(latencies) / len(latencies) if latencies else 0
            
            if success_rate >= 0.99 and avg_latency < 200:
                status = "PASS"
                message = f"Sustained load handled well"
            else:
                status = "FAIL"
                message = f"Performance degradation under load"
            
            return TestResult(
                test_name="Sustained Load",
                category="Performance",
                status=status,
                duration=time.time() - start,
                message=message,
                details={
                    "duration_seconds": duration_seconds,
                    "total_requests": total_requests,
                    "success_rate": success_rate,
                    "avg_latency_ms": avg_latency
                }
            )
        except Exception as e:
            return TestResult(
                test_name="Sustained Load",
                category="Performance",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    def _test_memory_pattern(self) -> TestResult:
        """Test for memory leaks (requires local access)"""
        if TEST_MODE != 'local':
            return TestResult(
                test_name="Memory Pattern",
                category="Performance",
                status="SKIP",
                duration=0,
                message="Memory testing requires local access"
            )
        
        # This would require psutil and local process access
        return TestResult(
            test_name="Memory Pattern",
            category="Performance",
            status="SKIP",
            duration=0,
            message="Memory pattern testing not implemented for remote hosts"
        )
    
    # ============= SECURITY TESTS =============
    
    def run_security_tests(self):
        """Test security configurations"""
        
        # Test 1: CORS Wildcard Check
        result = self._test_cors_wildcard()
        self.results.append(result)
        
        # Test 2: Security Headers
        result = self._test_security_headers()
        self.results.append(result)
        
        # Test 3: SQL Injection
        result = self._test_sql_injection()
        self.results.append(result)
        
        # Test 4: XSS Prevention
        result = self._test_xss_prevention()
        self.results.append(result)
    
    def _test_cors_wildcard(self) -> TestResult:
        """Check for CORS wildcard vulnerability"""
        start = time.time()
        try:
            headers = {'Origin': 'https://evil-site.com'}
            response = self.session.get(f"{self.base_url}/api/health", headers=headers, timeout=5)
            duration = time.time() - start
            
            allow_origin = response.headers.get('Access-Control-Allow-Origin')
            
            if allow_origin == '*' or allow_origin == 'https://evil-site.com':
                return TestResult(
                    test_name="CORS Wildcard Check",
                    category="Security",
                    status="FAIL",
                    duration=duration,
                    message="CRITICAL: CORS accepts any origin",
                    details={"allow_origin": allow_origin}
                )
            else:
                return TestResult(
                    test_name="CORS Wildcard Check",
                    category="Security",
                    status="PASS",
                    duration=duration,
                    message="CORS properly restricted",
                    details={"allow_origin": allow_origin}
                )
        except Exception as e:
            return TestResult(
                test_name="CORS Wildcard Check",
                category="Security",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    def _test_security_headers(self) -> TestResult:
        """Check for security headers"""
        start = time.time()
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            duration = time.time() - start
            
            required_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
                'X-XSS-Protection': '1',
            }
            
            missing_headers = []
            incorrect_headers = []
            
            for header, expected in required_headers.items():
                actual = response.headers.get(header)
                if not actual:
                    missing_headers.append(header)
                elif isinstance(expected, list):
                    if actual not in expected:
                        incorrect_headers.append(f"{header}: {actual} (expected one of {expected})")
                elif actual != expected:
                    incorrect_headers.append(f"{header}: {actual} (expected {expected})")
            
            if not missing_headers and not incorrect_headers:
                return TestResult(
                    test_name="Security Headers",
                    category="Security",
                    status="PASS",
                    duration=duration,
                    message="All security headers present",
                    details={"headers": dict(response.headers)}
                )
            else:
                return TestResult(
                    test_name="Security Headers",
                    category="Security",
                    status="FAIL",
                    duration=duration,
                    message="Security headers missing or incorrect",
                    details={
                        "missing": missing_headers,
                        "incorrect": incorrect_headers
                    }
                )
        except Exception as e:
            return TestResult(
                test_name="Security Headers",
                category="Security",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    def _test_sql_injection(self) -> TestResult:
        """Basic SQL injection test"""
        start = time.time()
        try:
            # Try basic SQL injection patterns
            payloads = [
                "1' OR '1'='1",
                "1; DROP TABLE users--",
                "admin'--"
            ]
            
            vulnerable = False
            for payload in payloads:
                response = self.session.get(
                    f"{self.base_url}/api/test",
                    params={"id": payload},
                    timeout=5
                )
                # Check for SQL error messages in response
                if any(err in response.text.lower() for err in ['sql', 'syntax', 'query']):
                    vulnerable = True
                    break
            
            if not vulnerable:
                return TestResult(
                    test_name="SQL Injection",
                    category="Security",
                    status="PASS",
                    duration=time.time() - start,
                    message="No SQL injection vulnerability detected",
                    details={"payloads_tested": len(payloads)}
                )
            else:
                return TestResult(
                    test_name="SQL Injection",
                    category="Security",
                    status="FAIL",
                    duration=time.time() - start,
                    message="Potential SQL injection vulnerability",
                    details={"vulnerable_payload": payload}
                )
        except Exception as e:
            return TestResult(
                test_name="SQL Injection",
                category="Security",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    def _test_xss_prevention(self) -> TestResult:
        """Test XSS prevention"""
        start = time.time()
        try:
            xss_payload = "<script>alert('XSS')</script>"
            response = self.session.get(
                f"{self.base_url}/api/test",
                params={"q": xss_payload},
                timeout=5
            )
            
            # Check if payload is reflected without encoding
            if xss_payload in response.text:
                return TestResult(
                    test_name="XSS Prevention",
                    category="Security",
                    status="FAIL",
                    duration=time.time() - start,
                    message="XSS payload not encoded",
                    details={"reflected": True}
                )
            else:
                return TestResult(
                    test_name="XSS Prevention",
                    category="Security",
                    status="PASS",
                    duration=time.time() - start,
                    message="XSS properly prevented",
                    details={"reflected": False}
                )
        except Exception as e:
            return TestResult(
                test_name="XSS Prevention",
                category="Security",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    # ============= RELIABILITY TESTS =============
    
    def run_reliability_tests(self):
        """Test system reliability"""
        
        # Test 1: Retry Logic
        result = self._test_retry_logic()
        self.results.append(result)
        
        # Test 2: Timeout Handling
        result = self._test_timeout_handling()
        self.results.append(result)
        
        # Test 3: Error Recovery
        result = self._test_error_recovery()
        self.results.append(result)
    
    def _test_retry_logic(self) -> TestResult:
        """Test retry mechanisms"""
        # This would require simulating failures
        return TestResult(
            test_name="Retry Logic",
            category="Reliability",
            status="SKIP",
            duration=0,
            message="Retry logic testing requires failure injection"
        )
    
    def _test_timeout_handling(self) -> TestResult:
        """Test timeout handling"""
        start = time.time()
        try:
            # Use a very short timeout
            with self.session.get(f"{self.base_url}/api/slow", timeout=0.001) as response:
                return TestResult(
                    test_name="Timeout Handling",
                    category="Reliability",
                    status="FAIL",
                    duration=time.time() - start,
                    message="Timeout not triggered as expected"
                )
        except requests.Timeout:
            return TestResult(
                test_name="Timeout Handling",
                category="Reliability",
                status="PASS",
                duration=time.time() - start,
                message="Timeout properly handled"
            )
        except Exception as e:
            return TestResult(
                test_name="Timeout Handling",
                category="Reliability",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    def _test_error_recovery(self) -> TestResult:
        """Test error recovery capabilities"""
        start = time.time()
        try:
            # Make multiple requests to test recovery
            errors = 0
            successes = 0
            
            for _ in range(10):
                try:
                    response = self.session.get(f"{self.base_url}/health", timeout=5)
                    if response.status_code == 200:
                        successes += 1
                    else:
                        errors += 1
                except:
                    errors += 1
                time.sleep(1)
            
            recovery_rate = successes / (successes + errors)
            
            if recovery_rate >= 0.9:
                return TestResult(
                    test_name="Error Recovery",
                    category="Reliability",
                    status="PASS",
                    duration=time.time() - start,
                    message=f"Good recovery rate: {recovery_rate*100:.1f}%",
                    details={"successes": successes, "errors": errors}
                )
            else:
                return TestResult(
                    test_name="Error Recovery",
                    category="Reliability",
                    status="FAIL",
                    duration=time.time() - start,
                    message=f"Poor recovery rate: {recovery_rate*100:.1f}%",
                    details={"successes": successes, "errors": errors}
                )
        except Exception as e:
            return TestResult(
                test_name="Error Recovery",
                category="Reliability",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    # ============= INTEGRATION TESTS =============
    
    def run_integration_tests(self):
        """Test system integration"""
        
        # Test 1: Database Connectivity
        result = self._test_database_connectivity()
        self.results.append(result)
        
        # Test 2: End-to-End Flow
        result = self._test_end_to_end_flow()
        self.results.append(result)
    
    def _test_database_connectivity(self) -> TestResult:
        """Test database connectivity through API"""
        start = time.time()
        try:
            # Try to access an endpoint that requires DB
            response = self.session.get(f"{self.base_url}/api/projects/", timeout=10)
            duration = time.time() - start
            
            if response.status_code in [200, 401, 403]:  # Auth required is OK
                return TestResult(
                    test_name="Database Connectivity",
                    category="Integration",
                    status="PASS",
                    duration=duration,
                    message="Database connection working",
                    details={"status_code": response.status_code}
                )
            elif response.status_code >= 500:
                return TestResult(
                    test_name="Database Connectivity",
                    category="Integration",
                    status="FAIL",
                    duration=duration,
                    message="Database connection error",
                    details={"status_code": response.status_code}
                )
            else:
                return TestResult(
                    test_name="Database Connectivity",
                    category="Integration",
                    status="PASS",
                    duration=duration,
                    message="Database endpoint accessible",
                    details={"status_code": response.status_code}
                )
        except Exception as e:
            return TestResult(
                test_name="Database Connectivity",
                category="Integration",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    def _test_end_to_end_flow(self) -> TestResult:
        """Test complete request flow"""
        start = time.time()
        try:
            # Test a complete flow: health -> ready -> api
            flow_steps = [
                ('Health Check', '/health'),
                ('Ready Check', '/ready'),
                ('API Access', '/api/health/')
            ]
            
            all_passed = True
            failed_step = None
            
            for step_name, endpoint in flow_steps:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code >= 500:
                    all_passed = False
                    failed_step = step_name
                    break
            
            if all_passed:
                return TestResult(
                    test_name="End-to-End Flow",
                    category="Integration",
                    status="PASS",
                    duration=time.time() - start,
                    message="Complete flow successful",
                    details={"steps_completed": len(flow_steps)}
                )
            else:
                return TestResult(
                    test_name="End-to-End Flow",
                    category="Integration",
                    status="FAIL",
                    duration=time.time() - start,
                    message=f"Flow failed at: {failed_step}",
                    details={"failed_step": failed_step}
                )
        except Exception as e:
            return TestResult(
                test_name="End-to-End Flow",
                category="Integration",
                status="ERROR",
                duration=time.time() - start,
                message=str(e)
            )
    
    # ============= REPORTING =============
    
    def generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        total_duration = time.time() - self.start_time
        
        # Calculate statistics
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        errors = sum(1 for r in self.results if r.status == "ERROR")
        skipped = sum(1 for r in self.results if r.status == "SKIP")
        
        # Group by category
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        # Calculate category scores
        category_scores = {}
        for category, results in categories.items():
            cat_passed = sum(1 for r in results if r.status == "PASS")
            cat_total = len([r for r in results if r.status != "SKIP"])
            if cat_total > 0:
                category_scores[category] = (cat_passed / cat_total) * 100
            else:
                category_scores[category] = 0
        
        # Overall score
        overall_score = (passed / (total_tests - skipped)) * 100 if (total_tests - skipped) > 0 else 0
        
        # Identify critical issues
        critical_issues = [
            r for r in self.results 
            if r.status == "FAIL" and "CRITICAL" in r.message
        ]
        
        report = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "test_mode": TEST_MODE,
                "total_duration_seconds": total_duration
            },
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "pass_rate": f"{overall_score:.1f}%",
                "overall_score": overall_score
            },
            "category_scores": category_scores,
            "critical_issues": [asdict(issue) for issue in critical_issues],
            "results": [asdict(r) for r in self.results],
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check for critical security issues
        cors_issues = [r for r in self.results if "CORS" in r.test_name and r.status == "FAIL"]
        if cors_issues:
            recommendations.append("CRITICAL: Fix CORS configuration immediately - currently allows all origins")
        
        # Check performance issues
        perf_issues = [r for r in self.results if r.category == "Performance" and r.status == "FAIL"]
        if perf_issues:
            recommendations.append("HIGH: Optimize performance - response times exceeding targets")
        
        # Check reliability issues
        reliability_issues = [r for r in self.results if r.category == "Reliability" and r.status == "FAIL"]
        if reliability_issues:
            recommendations.append("HIGH: Implement proper error recovery mechanisms")
        
        # Check for missing tests
        skipped_tests = [r for r in self.results if r.status == "SKIP"]
        if len(skipped_tests) > 5:
            recommendations.append("MEDIUM: Enable more comprehensive testing in local environment")
        
        if not recommendations:
            recommendations.append("System is performing within acceptable parameters")
        
        return recommendations
    
    def save_report(self, filepath: str = None):
        """Save report to file"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"qa_test_report_{timestamp}.json"
        
        report = self.generate_report()
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Report saved to {filepath}")
        return filepath
    
    def print_summary(self):
        """Print test summary to console"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("QA TEST SUITE RESULTS")
        print("="*60)
        print(f"Target: {self.base_url}")
        print(f"Timestamp: {report['metadata']['timestamp']}")
        print(f"Duration: {report['metadata']['total_duration_seconds']:.2f} seconds")
        print("\n" + "-"*60)
        print("SUMMARY")
        print("-"*60)
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Errors: {report['summary']['errors']}")
        print(f"Skipped: {report['summary']['skipped']}")
        print(f"Pass Rate: {report['summary']['pass_rate']}")
        print(f"Overall Score: {report['summary']['overall_score']:.1f}/100")
        
        print("\n" + "-"*60)
        print("CATEGORY SCORES")
        print("-"*60)
        for category, score in report['category_scores'].items():
            status = "" if score >= 80 else "" if score >= 60 else ""
            print(f"{status} {category}: {score:.1f}%")
        
        if report['critical_issues']:
            print("\n" + "-"*60)
            print(" CRITICAL ISSUES")
            print("-"*60)
            for issue in report['critical_issues']:
                print(f"- {issue['test_name']}: {issue['message']}")
        
        print("\n" + "-"*60)
        print("RECOMMENDATIONS")
        print("-"*60)
        for rec in report['recommendations']:
            print(f"• {rec}")
        
        print("\n" + "="*60)


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='VideoPlanet QA Test Suite')
    parser.add_argument('--url', default=BASE_URL, help='Base URL to test')
    parser.add_argument('--mode', default=TEST_MODE, choices=['production', 'staging', 'local'])
    parser.add_argument('--output', help='Output file path for report')
    parser.add_argument('--categories', nargs='+', help='Specific test categories to run')
    
    args = parser.parse_args()
    
    # Initialize test suite
    suite = QualityAssuranceTestSuite(base_url=args.url)
    
    # Run tests
    if args.categories:
        # Run specific categories
        logger.info(f"Running specific categories: {args.categories}")
        # Implementation for specific categories would go here
    else:
        # Run all tests
        suite.run_all_tests()
    
    # Generate and save report
    output_file = suite.save_report(args.output)
    
    # Print summary
    suite.print_summary()
    
    # Return exit code based on results
    report = suite.generate_report()
    if report['summary']['overall_score'] >= 80:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()