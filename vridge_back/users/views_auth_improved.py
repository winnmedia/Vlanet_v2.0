"""
   - 401  
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer
import logging

logger = logging.getLogger(__name__)

class ImprovedSignUp(APIView):
    """
      
           
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = request.data
            
            #   
            required_fields = ['username', 'email', 'password', 'nickname']
            for field in required_fields:
                if field not in data:
                    return Response({
                        'success': False,
                        'error': f'{field} is required',
                        'field': field
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # /  
            if User.objects.filter(username=data['username']).exists():
                return Response({
                    'success': False,
                    'error': 'Username already exists',
                    'field': 'username'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(email=data['email']).exists():
                return Response({
                    'success': False,
                    'error': 'Email already exists',
                    'field': 'email'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            #   
            if User.objects.filter(nickname=data['nickname']).exists():
                return Response({
                    'success': False,
                    'error': 'Nickname already exists',
                    'field': 'nickname'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            #  
            user = User.objects.create(
                username=data['username'],
                email=data['email'],
                nickname=data['nickname'],
                password=make_password(data['password']),
                is_active=True,
                email_verified=True  #     
            )
            
            #  
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'User created successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'nickname': user.nickname
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ImprovedSignIn(APIView):
    """
      
        401  
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = request.data
            
            #   
            if 'username' not in data or 'password' not in data:
                return Response({
                    'success': False,
                    'error': 'Username and password are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            username = data['username']
            password = data['password']
            
            #   (  )
            user = None
            if '@' in username:
                #  
                try:
                    user = User.objects.get(email=username)
                    username = user.username
                except User.DoesNotExist:
                    pass
            
            #  
            user = authenticate(username=username, password=password)
            
            if user is None:
                #   
                if '@' in data['username']:
                    exists = User.objects.filter(email=data['username']).exists()
                else:
                    exists = User.objects.filter(username=data['username']).exists()
                
                if exists:
                    return Response({
                        'success': False,
                        'error': 'Invalid password',
                        'code': 'INVALID_PASSWORD'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response({
                        'success': False,
                        'error': 'User not found',
                        'code': 'USER_NOT_FOUND'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            if not user.is_active:
                return Response({
                    'success': False,
                    'error': 'Account is inactive',
                    'code': 'INACTIVE_ACCOUNT'
                }, status=status.HTTP_403_FORBIDDEN)
            
            #  
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'nickname': user.nickname
                },
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TestUserCreate(APIView):
    """
       
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
              
        """
        test_users = [
            {
                'username': 'test@test.com',
                'email': 'test@test.com',
                'password': 'Test1234!',
                'nickname': 'TestUser'
            },
            {
                'username': 'demo@test.com',
                'email': 'demo@test.com',
                'password': 'Demo1234!',
                'nickname': 'DemoUser'
            }
        ]
        
        created_users = []
        
        for user_data in test_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'nickname': user_data['nickname'],
                    'password': make_password(user_data['password']),
                    'is_active': True,
                    'email_verified': True
                }
            )
            
            if not created:
                #    
                user.set_password(user_data['password'])
                user.is_active = True
                user.email_verified = True
                user.save()
            
            #  
            refresh = RefreshToken.for_user(user)
            
            created_users.append({
                'username': user.username,
                'email': user.email,
                'password': user_data['password'],  #   
                'nickname': user.nickname,
                'created': created,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            })
        
        return Response({
            'success': True,
            'message': 'Test users ready',
            'users': created_users
        }, status=status.HTTP_200_OK)