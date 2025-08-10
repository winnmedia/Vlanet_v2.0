"""
Debug views for Railway deployment troubleshooting
"""
import os
import sys
import json
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db import connection
from django.core.cache import cache


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def debug_status(request):
    """Debug endpoint to check server status"""
    try:
        status = {
            "status": "ok",
            "method": request.method,
            "path": request.path,
            "debug": settings.DEBUG,
            "environment": {
                "django_settings": os.environ.get('DJANGO_SETTINGS_MODULE', 'not set'),
                "debug": os.environ.get('DEBUG', 'not set'),
                "database_url": "configured" if os.environ.get('DATABASE_URL') else "not configured",
                "secret_key": "configured" if os.environ.get('SECRET_KEY') else "using default",
                "python_version": sys.version,
            },
            "headers": {
                "host": request.get_host(),
                "origin": request.META.get('HTTP_ORIGIN', 'not set'),
                "content_type": request.content_type,
                "user_agent": request.META.get('HTTP_USER_AGENT', 'not set'),
            },
            "cors": {
                "allowed_origins": getattr(settings, 'CORS_ALLOWED_ORIGINS', [])[:5],
                "allow_all": getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False),
                "allow_credentials": getattr(settings, 'CORS_ALLOW_CREDENTIALS', False),
            },
            "database": "unknown",
            "cache": "unknown",
        }
        
        # Test database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                status["database"] = "connected"
        except Exception as e:
            status["database"] = f"error: {str(e)}"
        
        # Test cache
        try:
            cache.set("test_key", "test_value", 10)
            if cache.get("test_key") == "test_value":
                status["cache"] = "working"
            else:
                status["cache"] = "not working"
        except Exception as e:
            status["cache"] = f"error: {str(e)}"
        
        # Handle POST request body
        if request.method == "POST":
            try:
                if request.body:
                    body = json.loads(request.body.decode('utf-8'))
                    status["received_data"] = body
                else:
                    status["received_data"] = "empty body"
            except Exception as e:
                status["body_error"] = str(e)
        
        return JsonResponse(status, status=200)
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def debug_echo(request):
    """Echo endpoint for testing POST requests"""
    try:
        data = {}
        
        # Parse request body
        if request.body:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                data = {"raw_body": request.body.decode('utf-8', errors='ignore')}
        
        response = {
            "status": "success",
            "method": request.method,
            "headers": {
                "content_type": request.content_type,
                "origin": request.META.get('HTTP_ORIGIN', 'not set'),
            },
            "data_received": data,
            "message": "Echo successful"
        }
        
        return JsonResponse(response, status=200)
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status=500)


@csrf_exempt
def test_signup_debug(request):
    """Debug endpoint to test signup flow"""
    if request.method == "OPTIONS":
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "content-type"
        return response
    
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    
    try:
        # Import here to avoid circular imports
        from users.models import User
        
        # Parse request
        if request.body:
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = {}
        
        # Test creating a user
        test_email = data.get("email", "test@example.com")
        test_nickname = data.get("nickname", "testuser")
        test_password = data.get("password", "Test1234!")
        
        # Check if user exists
        existing = User.objects.filter(username=test_email).first()
        if existing:
            return JsonResponse({
                "status": "user_exists",
                "user_id": existing.id,
                "email": existing.email,
                "nickname": existing.nickname,
                "message": "User already exists"
            })
        
        # Try to create user
        user = User(
            username=test_email,
            email=test_email,
            nickname=test_nickname,
            login_method='email'
        )
        user.set_password(test_password)
        user.save()
        
        return JsonResponse({
            "status": "success",
            "user_id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "message": "Test user created successfully"
        })
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status=500)