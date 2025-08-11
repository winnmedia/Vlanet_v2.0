from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import UserProfile
from .utils import user_validator
import os
import uuid
import json


@method_decorator(csrf_exempt, name='dispatch')
class ProfileImageUpload(View):
    """  /"""

    @user_validator
    def post(self, request):
        """  """
        try:
            profile_image = request.FILES.get('profile_image')
            
            if not profile_image:
                return JsonResponse({
                    'status': 'error',
                    'message': '  .'
                }, status=400)
            
            #    (5MB)
            if profile_image.size > 5 * 1024 * 1024:
                return JsonResponse({
                    'status': 'error',
                    'message': '  5MB   .'
                }, status=400)
            
            #   
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if profile_image.content_type not in allowed_types:
                return JsonResponse({
                    'status': 'error',
                    'message': '   . (JPG, PNG, GIF, WEBP )'
                }, status=400)
            
            # UserProfile  
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            #    
            if profile.profile_image:
                try:
                    profile.profile_image.delete(save=False)
                except:
                    pass
            
            #   
            ext = profile_image.name.split('.')[-1]
            filename = f"profile_{request.user.id}_{uuid.uuid4().hex[:8]}.{ext}"
            
            #  
            profile.profile_image.save(filename, profile_image, save=True)
            
            #  URL 
            image_url = profile.profile_image.url if profile.profile_image else None
            
            return JsonResponse({
                'status': 'success',
                'message': '  .',
                'profile_image_url': image_url
            }, status=200)
            
        except Exception as e:
            print(f"Profile image upload error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'    : {str(e)}'
            }, status=500)
    
    @user_validator
    def delete(self, request):
        """  """
        try:
            profile = UserProfile.objects.filter(user=request.user).first()
            
            if profile and profile.profile_image:
                #   
                profile.profile_image.delete(save=True)
                
                return JsonResponse({
                    'status': 'success',
                    'message': '  .'
                }, status=200)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': '   .'
                }, status=404)
                
        except Exception as e:
            print(f"Profile image delete error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'    : {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ProfileUpdate(View):
    """  """
    
    @user_validator
    def post(self, request):
        """  """
        return self.update_profile(request)
    
    @user_validator
    def patch(self, request):
        """   (PATCH  )"""
        return self.update_profile(request)
    
    def update_profile(self, request):
        """   """
        try:
            # JSON  
            try:
                data = json.loads(request.body)
            except:
                data = request.POST.dict()
            
            # UserProfile  
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            #  
            fields_to_update = ['bio', 'phone', 'company', 'position']
            
            for field in fields_to_update:
                if field in data:
                    setattr(profile, field, data[field])
            
            #  User  
            if 'nickname' in data:
                request.user.nickname = data['nickname']
                request.user.save()
            
            profile.save()
            
            #   
            response_data = {
                'status': 'success',
                'message': ' .',
                'profile': {
                    'nickname': request.user.nickname,
                    'bio': profile.bio,
                    'phone': profile.phone,
                    'company': profile.company,
                    'position': profile.position,
                    'profile_image': profile.profile_image.url if profile.profile_image else None
                }
            }
            
            return JsonResponse(response_data, status=200)
            
        except Exception as e:
            print(f"Profile update error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'    : {str(e)}'
            }, status=500)