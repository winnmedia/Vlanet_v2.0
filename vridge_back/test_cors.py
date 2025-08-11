#!/usr/bin/env python3
"""
CORS  
Railway   CORS   .
"""
import requests
import json
import sys
from urllib.parse import urljoin


def test_cors(backend_url="https://videoplanet.up.railway.app", frontend_origin="https://vlanet.net"):
    """CORS   """
    
    print(f" CORS  ")
    print(f"   Backend: {backend_url}")
    print(f"   Frontend Origin: {frontend_origin}")
    print("-" * 50)
    
    #   
    endpoints = [
        "/api/health/",
        "/api/auth/check-email/",
        "/api/auth/check-nickname/",
        "/api/users/login/",
        "/api/debug/cors/",
    ]
    
    results = []
    
    for endpoint in endpoints:
        url = urljoin(backend_url, endpoint)
        print(f"\n Testing: {endpoint}")
        
        # 1. OPTIONS   (Preflight)
        print(f"   1⃣ OPTIONS Request...")
        try:
            response = requests.options(
                url,
                headers={
                    "Origin": frontend_origin,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "content-type,authorization",
                },
                timeout=10
            )
            
            cors_headers = {
                "Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                "Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials"),
                "Max-Age": response.headers.get("Access-Control-Max-Age"),
            }
            
            if response.status_code in [200, 204]:
                print(f"       OPTIONS Success (Status: {response.status_code})")
                for key, value in cors_headers.items():
                    if value:
                        print(f"         {key}: {value[:50]}..." if len(str(value)) > 50 else f"         {key}: {value}")
            else:
                print(f"       OPTIONS Failed (Status: {response.status_code})")
                
        except Exception as e:
            print(f"       OPTIONS Error: {str(e)}")
        
        # 2. GET  
        print(f"   2⃣ GET Request...")
        try:
            response = requests.get(
                url,
                headers={
                    "Origin": frontend_origin,
                },
                timeout=10
            )
            
            cors_origin = response.headers.get("Access-Control-Allow-Origin")
            cors_credentials = response.headers.get("Access-Control-Allow-Credentials")
            
            if cors_origin:
                print(f"       GET CORS Headers Present")
                print(f"         Allow-Origin: {cors_origin}")
                print(f"         Allow-Credentials: {cors_credentials}")
            else:
                print(f"        GET No CORS Headers (Status: {response.status_code})")
                
        except Exception as e:
            print(f"       GET Error: {str(e)}")
        
        # 3. POST   ( )
        if endpoint in ["/api/auth/check-email/", "/api/users/login/"]:
            print(f"   3⃣ POST Request...")
            try:
                test_data = {
                    "email": "test@example.com" if "email" in endpoint else None,
                    "nickname": "testuser" if "nickname" in endpoint else None,
                    "password": "testpass123" if "login" in endpoint else None,
                }
                # None  
                test_data = {k: v for k, v in test_data.items() if v is not None}
                
                response = requests.post(
                    url,
                    headers={
                        "Origin": frontend_origin,
                        "Content-Type": "application/json",
                    },
                    json=test_data,
                    timeout=10
                )
                
                cors_origin = response.headers.get("Access-Control-Allow-Origin")
                cors_credentials = response.headers.get("Access-Control-Allow-Credentials")
                
                if cors_origin:
                    print(f"       POST CORS Headers Present")
                    print(f"         Allow-Origin: {cors_origin}")
                    print(f"         Allow-Credentials: {cors_credentials}")
                    print(f"         Response Status: {response.status_code}")
                else:
                    print(f"       POST No CORS Headers (Status: {response.status_code})")
                    
            except Exception as e:
                print(f"       POST Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("  !")
    print("=" * 50)


def test_local():
    """  """
    print("\n   ")
    test_cors(
        backend_url="http://localhost:8000",
        frontend_origin="http://localhost:3000"
    )


def test_production():
    """  """
    print("\n   ")
    test_cors(
        backend_url="https://videoplanet.up.railway.app",
        frontend_origin="https://vlanet.net"
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "local":
            test_local()
        elif sys.argv[1] == "production":
            test_production()
        else:
            print("Usage: python test_cors.py [local|production]")
    else:
        #   
        test_production()