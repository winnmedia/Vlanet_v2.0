#!/usr/bin/env python3
"""
Test Railway Architecture Locally
==================================
Validates the health check and routing system works correctly.
"""

import requests
import time
import subprocess
import sys
import os
import signal

def test_health_beacon():
    """Test the standalone health beacon"""
    print("\n=== Testing Health Beacon ===")
    
    # Start health beacon
    proc = subprocess.Popen(
        ["python3", "health_beacon.py"],
        env={**os.environ, "PORT": "8000"}
    )
    
    time.sleep(2)  # Wait for server to start
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("✓ Health Beacon test passed")
    except Exception as e:
        print(f"✗ Health Beacon test failed: {e}")
    finally:
        proc.terminate()
        proc.wait()

def test_railway_router():
    """Test the railway router"""
    print("\n=== Testing Railway Router ===")
    
    # Start railway router
    proc = subprocess.Popen(
        ["python3", "railway_router.py"],
        env={**os.environ, "PORT": "8001"}
    )
    
    time.sleep(2)  # Wait for server to start
    
    try:
        # Test health endpoint
        print("\n1. Testing health check (should be instant):")
        start = time.time()
        response = requests.get("http://localhost:8001/health")
        elapsed = time.time() - start
        print(f"  Status: {response.status_code}")
        print(f"  Response time: {elapsed:.3f}s")
        print(f"  Django ready: {response.json().get('django_ready', False)}")
        assert response.status_code == 200
        assert elapsed < 0.1  # Should be instant
        print("  ✓ Health check passed")
        
        # Test CORS preflight
        print("\n2. Testing CORS preflight:")
        response = requests.options("http://localhost:8001/api/test")
        print(f"  Status: {response.status_code}")
        assert response.status_code == 200
        print("  ✓ CORS preflight passed")
        
        # Test 404 for unknown path
        print("\n3. Testing 404 response:")
        response = requests.get("http://localhost:8001/unknown")
        print(f"  Status: {response.status_code}")
        assert response.status_code == 404
        print("  ✓ 404 handling passed")
        
        print("\n✓ All Railway Router tests passed")
        
    except Exception as e:
        print(f"✗ Railway Router test failed: {e}")
    finally:
        proc.terminate()
        proc.wait()

def main():
    """Run all tests"""
    print("=" * 50)
    print("Railway Architecture Test Suite")
    print("=" * 50)
    
    test_health_beacon()
    test_railway_router()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("- Health Beacon: Simple, zero-dependency health check")
    print("- Railway Router: Smart routing with Django lazy loading")
    print("Use 'railway_router.py' for production deployment")
    print("=" * 50)

if __name__ == "__main__":
    main()