#!/usr/bin/env python3
"""
Quick QA Test for Django Integration
Focus on critical issues only
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://videoplanet.up.railway.app"

def run_critical_tests():
    """Run only critical tests quickly"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "base_url": BASE_URL,
        "tests": []
    }
    
    print("🔍 Running Critical QA Tests...")
    print("="*50)
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        duration = (time.time() - start) * 1000
        
        test_result = {
            "name": "Health Check",
            "status": "PASS" if response.status_code == 200 else "FAIL",
            "duration_ms": duration,
            "details": {"status_code": response.status_code}
        }
        results["tests"].append(test_result)
        print(f"   ✅ Health Check: {test_result['status']} ({duration:.2f}ms)")
    except Exception as e:
        results["tests"].append({
            "name": "Health Check",
            "status": "ERROR",
            "error": str(e)
        })
        print(f"   ❌ Health Check: ERROR - {e}")
    
    # Test 2: CORS Security
    print("2. Testing CORS Security...")
    try:
        headers = {'Origin': 'https://evil-site.com'}
        response = requests.get(f"{BASE_URL}/api/health", headers=headers, timeout=5)
        allow_origin = response.headers.get('Access-Control-Allow-Origin', '')
        
        is_vulnerable = allow_origin == '*' or allow_origin == 'https://evil-site.com'
        
        test_result = {
            "name": "CORS Security",
            "status": "FAIL" if is_vulnerable else "PASS",
            "critical": is_vulnerable,
            "details": {
                "allow_origin": allow_origin,
                "vulnerability": "CORS allows all origins" if is_vulnerable else "CORS properly restricted"
            }
        }
        results["tests"].append(test_result)
        
        if is_vulnerable:
            print(f"   🔴 CORS Security: CRITICAL VULNERABILITY - Allows all origins!")
        else:
            print(f"   ✅ CORS Security: PASS - Properly restricted")
    except Exception as e:
        results["tests"].append({
            "name": "CORS Security",
            "status": "ERROR",
            "error": str(e)
        })
        print(f"   ❌ CORS Security: ERROR - {e}")
    
    # Test 3: Django Ready
    print("3. Testing Django Readiness...")
    try:
        response = requests.get(f"{BASE_URL}/ready", timeout=10)
        
        test_result = {
            "name": "Django Ready",
            "status": "PASS" if response.status_code == 200 else "FAIL",
            "details": {
                "status_code": response.status_code,
                "response": response.text[:100]
            }
        }
        results["tests"].append(test_result)
        
        if response.status_code == 200:
            print(f"   ✅ Django Ready: PASS")
        else:
            print(f"   ⚠️  Django Ready: {response.status_code} - {response.text[:50]}")
    except Exception as e:
        results["tests"].append({
            "name": "Django Ready",
            "status": "ERROR",
            "error": str(e)
        })
        print(f"   ❌ Django Ready: ERROR - {e}")
    
    # Test 4: API Proxy
    print("4. Testing API Proxy...")
    try:
        response = requests.get(f"{BASE_URL}/api/health/", timeout=10)
        
        test_result = {
            "name": "API Proxy",
            "status": "PASS" if response.status_code < 500 else "FAIL",
            "details": {"status_code": response.status_code}
        }
        results["tests"].append(test_result)
        
        if response.status_code < 500:
            print(f"   ✅ API Proxy: PASS ({response.status_code})")
        else:
            print(f"   ❌ API Proxy: FAIL - Server Error {response.status_code}")
    except Exception as e:
        results["tests"].append({
            "name": "API Proxy",
            "status": "ERROR",
            "error": str(e)
        })
        print(f"   ❌ API Proxy: ERROR - {e}")
    
    # Test 5: Security Headers
    print("5. Testing Security Headers...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        
        security_headers = {
            'X-Content-Type-Options': response.headers.get('X-Content-Type-Options'),
            'X-Frame-Options': response.headers.get('X-Frame-Options'),
            'X-XSS-Protection': response.headers.get('X-XSS-Protection'),
        }
        
        missing = [k for k, v in security_headers.items() if not v]
        
        test_result = {
            "name": "Security Headers",
            "status": "FAIL" if missing else "PASS",
            "details": {
                "headers": security_headers,
                "missing": missing
            }
        }
        results["tests"].append(test_result)
        
        if missing:
            print(f"   ⚠️  Security Headers: Missing {', '.join(missing)}")
        else:
            print(f"   ✅ Security Headers: All present")
    except Exception as e:
        results["tests"].append({
            "name": "Security Headers",
            "status": "ERROR",
            "error": str(e)
        })
        print(f"   ❌ Security Headers: ERROR - {e}")
    
    # Test 6: Performance Check
    print("6. Testing Performance...")
    try:
        latencies = []
        for _ in range(5):
            start = time.time()
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            latency = (time.time() - start) * 1000
            latencies.append(latency)
        
        avg_latency = sum(latencies) / len(latencies)
        
        test_result = {
            "name": "Performance",
            "status": "PASS" if avg_latency < 200 else "FAIL",
            "details": {
                "avg_latency_ms": avg_latency,
                "max_latency_ms": max(latencies),
                "min_latency_ms": min(latencies)
            }
        }
        results["tests"].append(test_result)
        
        if avg_latency < 200:
            print(f"   ✅ Performance: PASS (avg: {avg_latency:.2f}ms)")
        else:
            print(f"   ⚠️  Performance: High latency (avg: {avg_latency:.2f}ms)")
    except Exception as e:
        results["tests"].append({
            "name": "Performance",
            "status": "ERROR",
            "error": str(e)
        })
        print(f"   ❌ Performance: ERROR - {e}")
    
    # Calculate summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for t in results["tests"] if t["status"] == "PASS")
    failed = sum(1 for t in results["tests"] if t["status"] == "FAIL")
    errors = sum(1 for t in results["tests"] if t["status"] == "ERROR")
    total = len(results["tests"])
    
    results["summary"] = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "pass_rate": (passed / total * 100) if total > 0 else 0
    }
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Errors: {errors} ⚠️")
    print(f"Pass Rate: {results['summary']['pass_rate']:.1f}%")
    
    # Critical issues
    critical_issues = [t for t in results["tests"] if t.get("critical")]
    if critical_issues:
        print("\n🚨 CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"   - {issue['name']}: {issue['details'].get('vulnerability', 'Critical failure')}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if any(t["name"] == "CORS Security" and t.get("critical") for t in results["tests"]):
        print("   1. 🔴 CRITICAL: Fix CORS configuration immediately")
    if any(t["name"] == "Security Headers" and t["status"] == "FAIL" for t in results["tests"]):
        print("   2. ⚠️  HIGH: Add missing security headers")
    if any(t["name"] == "Performance" and t["status"] == "FAIL" for t in results["tests"]):
        print("   3. ⚠️  MEDIUM: Optimize response times")
    
    if results["summary"]["pass_rate"] == 100:
        print("   ✅ All tests passed! System is healthy.")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"qa_quick_test_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Full results saved to: {filename}")
    
    return results

if __name__ == "__main__":
    run_critical_tests()