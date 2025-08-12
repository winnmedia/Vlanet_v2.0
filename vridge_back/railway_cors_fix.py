#!/usr/bin/env python
"""
Railway CORS Configuration Checker
Verifies and fixes CORS settings for Railway production deployment
"""
import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
django.setup()

from django.conf import settings


def check_cors_configuration():
    """Check and report CORS configuration"""
    print("=" * 60)
    print("Railway CORS Configuration Check")
    print("=" * 60)
    
    # Check CORS settings
    print("\n1. CORS Settings:")
    print(f"   - CORS_ALLOW_ALL_ORIGINS: {getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', 'NOT SET')}")
    print(f"   - CORS_ALLOW_CREDENTIALS: {getattr(settings, 'CORS_ALLOW_CREDENTIALS', 'NOT SET')}")
    
    # Check allowed origins
    print("\n2. Allowed Origins:")
    allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
    for origin in allowed_origins[:5]:  # Show first 5
        print(f"   - {origin}")
    if len(allowed_origins) > 5:
        print(f"   ... and {len(allowed_origins) - 5} more")
    
    # Check regex patterns
    print("\n3. Origin Regex Patterns:")
    regex_patterns = getattr(settings, 'CORS_ALLOWED_ORIGIN_REGEXES', [])
    for pattern in regex_patterns:
        print(f"   - {pattern}")
    
    # Check middleware order
    print("\n4. Middleware Order:")
    middleware = settings.MIDDLEWARE
    cors_index = -1
    error_index = -1
    
    for i, mw in enumerate(middleware):
        if 'corsheaders.middleware.CorsMiddleware' in mw:
            cors_index = i
            print(f"   [{i}] CORS Middleware: {mw}")
        elif 'GlobalErrorHandlingMiddleware' in mw:
            error_index = i
            print(f"   [{i}] Error Middleware: {mw}")
        elif 'GuaranteedCORSMiddleware' in mw:
            print(f"   [{i}] Guaranteed CORS: {mw}")
    
    # Verify order
    print("\n5. Middleware Order Check:")
    if cors_index < error_index:
        print("   ✓ CORS middleware is before error handling (CORRECT)")
    else:
        print("   ✗ ERROR: CORS middleware should be before error handling!")
    
    # Check expose headers
    print("\n6. Exposed Headers:")
    expose_headers = getattr(settings, 'CORS_EXPOSE_HEADERS', [])
    for header in expose_headers:
        print(f"   - {header}")
    
    # Check CSRF trusted origins
    print("\n7. CSRF Trusted Origins:")
    csrf_origins = getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])
    for origin in csrf_origins[:5]:
        print(f"   - {origin}")
    
    # Check if vlanet.net is in allowed origins
    print("\n8. vlanet.net Configuration:")
    vlanet_found = False
    for origin in allowed_origins:
        if 'vlanet.net' in origin:
            vlanet_found = True
            print(f"   ✓ Found: {origin}")
    
    if not vlanet_found:
        print("   ✗ ERROR: vlanet.net not in allowed origins!")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    issues = []
    
    if not vlanet_found:
        issues.append("vlanet.net not in CORS_ALLOWED_ORIGINS")
    
    if cors_index >= error_index and error_index != -1:
        issues.append("CORS middleware order incorrect")
    
    if not getattr(settings, 'CORS_ALLOW_CREDENTIALS', False):
        issues.append("CORS_ALLOW_CREDENTIALS not enabled")
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  ✗ {issue}")
        return False
    else:
        print("  ✓ CORS configuration appears correct")
        return True


def test_cors_headers():
    """Test CORS headers with a mock request"""
    from django.test import RequestFactory
    from django.http import HttpResponse
    
    print("\n" + "=" * 60)
    print("Testing CORS Headers")
    print("=" * 60)
    
    factory = RequestFactory()
    
    # Test origins
    test_origins = [
        'https://vlanet.net',
        'https://www.vlanet.net',
        'https://vlanet-v2-0.vercel.app',
        'http://localhost:3000',
    ]
    
    for origin in test_origins:
        print(f"\nTesting origin: {origin}")
        
        # Create request
        request = factory.options('/api/users/login/', HTTP_ORIGIN=origin)
        
        # Process through middleware
        from corsheaders.middleware import CorsMiddleware
        from django.http import HttpResponse
        
        middleware = CorsMiddleware(lambda r: HttpResponse())
        response = middleware(request)
        
        # Check headers
        has_origin = 'Access-Control-Allow-Origin' in response
        has_credentials = response.get('Access-Control-Allow-Credentials') == 'true'
        
        print(f"  - Allow-Origin header: {'✓' if has_origin else '✗'}")
        print(f"  - Allow-Credentials: {'✓' if has_credentials else '✗'}")
        
        if has_origin:
            print(f"  - Origin value: {response['Access-Control-Allow-Origin']}")


if __name__ == '__main__':
    print("Starting Railway CORS Configuration Check...\n")
    
    # Run checks
    config_ok = check_cors_configuration()
    
    # Test headers
    try:
        test_cors_headers()
    except Exception as e:
        print(f"\nError testing headers: {e}")
    
    # Exit code
    sys.exit(0 if config_ok else 1)