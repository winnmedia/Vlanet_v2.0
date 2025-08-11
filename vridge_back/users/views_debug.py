"""
JWT  
"""
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
import json
import traceback

@method_decorator(csrf_exempt, name='dispatch')
class JWTDebugView(View):
    """JWT  """
    
    def post(self, request):
        """JWT   """
        try:
            data = json.loads(request.body)
            token = data.get('token')
            
            if not token:
                return JsonResponse({"error": "No token provided"}, status=400)
            
            #   
            try:
                access_token = AccessToken(token)
                payload = dict(access_token.payload)
                
                #   
                user_info = None
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user_id = payload.get('user_id')
                    if user_id:
                        user = User.objects.get(id=user_id)
                        user_info = {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "is_active": user.is_active,
                        }
                except Exception as e:
                    user_info = {"error": str(e)}
                
                return JsonResponse({
                    "status": "success",
                    "payload": payload,
                    "user": user_info
                })
                
            except Exception as e:
                return JsonResponse({
                    "status": "error",
                    "error": str(e),
                    "type": type(e).__name__,
                    "traceback": traceback.format_exc()
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "error": str(e),
                "type": type(e).__name__
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AuthDebugView(View):
    """ """
    
    def get(self, request):
        """   """
        try:
            #  
            auth_header = request.META.get('HTTP_AUTHORIZATION', 'No auth header')
            
            # JWT  
            jwt_result = None
            try:
                jwt_auth = JWTAuthentication()
                auth_result = jwt_auth.authenticate(request)
                if auth_result:
                    user, token = auth_result
                    jwt_result = {
                        "authenticated": True,
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email
                        }
                    }
                else:
                    jwt_result = {"authenticated": False, "reason": "No auth result"}
            except Exception as e:
                jwt_result = {
                    "authenticated": False,
                    "error": str(e),
                    "type": type(e).__name__,
                    "traceback": traceback.format_exc()
                }
            
            #   
            db_status = None
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    db_status = "connected"
            except Exception as e:
                db_status = f"error: {str(e)}"
            
            # User   
            user_fields = None
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user_fields = [field.name for field in User._meta.fields]
            except Exception as e:
                user_fields = f"error: {str(e)}"
            
            return JsonResponse({
                "auth_header": auth_header,
                "jwt_authentication": jwt_result,
                "database": db_status,
                "user_model_fields": user_fields,
                "request_user": str(request.user),
                "is_authenticated": request.user.is_authenticated
            })
            
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }, status=500)