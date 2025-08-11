from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import AllowAnyTemporary
# from .debug_permissions import DebugAllowAny  #  
from rest_framework.response import Response
from django.http import HttpResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import VideoPlanning, VideoPlanningImage, VideoPlanningAIPrompt
from .serializers import VideoPlanningSerializer, VideoPlanningListSerializer
from .gemini_service import GeminiService
from .ai_prompt_engine import PromptOptimizationService, PromptGenerationContext, PromptGenerationResult
from .ai_prompt_generator import VideoPlanningPromptGenerator, VEO3PromptGenerator
import logging

#    import
try:
    from .dalle_service import DalleService
    IMAGE_SERVICE_AVAILABLE = True
except ImportError:
    DalleService = None
    IMAGE_SERVICE_AVAILABLE = False
import requests
from urllib.parse import urlparse
import os
import json
from django.http import FileResponse, HttpResponse
from .pdf_export_service import PDFExportService
from .compressed_pdf_export_service import CompressedPDFExportService
from .pdf_export_service_enhanced import EnhancedPDFExportService
from .google_slides_service import GoogleSlidesService
from .services.advanced_pdf_export_service import AdvancedPDFExportService
from .async_image_generator import AsyncImageGenerator
import uuid
from django.core.cache import cache
import threading
from datetime import datetime
import base64
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_plannings(request):
    """
         .
    """
    #   
    logger.info(f"[get_recent_plannings] User: {request.user}, Authenticated: {request.user.is_authenticated}")
    logger.info(f"[get_recent_plannings] Auth Header: {request.META.get('HTTP_AUTHORIZATION', 'No auth header')}")
    
    try:
        #    5   
        #        
        recent_plannings = VideoPlanning.objects.filter(
            user=request.user
        ).values(
            'id', 'title', 'planning_text', 'stories', 'selected_story',
            'scenes', 'selected_scene', 'shots', 'selected_shot',
            'storyboards', 'planning_options', 'is_completed', 
            'current_step', 'created_at', 'updated_at'
        ).order_by('-created_at')[:5]
        
        #   
        planning_logs = []
        for planning in recent_plannings:
            try:
                # planning_options  ( planning )
                planning_options = {}
                if planning.get('selected_story') and isinstance(planning['selected_story'], dict):
                    planning_options = planning['selected_story'].get('planning_options', {})
                
                planning_logs.append({
                    'id': planning['id'],
                    'title': planning.get('title') or ' ',
                    'created_at': planning['created_at'].strftime('%Y-%m-%d %H:%M') if planning.get('created_at') else '',
                    'planning_options': planning.get('planning_options') or planning_options,
                    'current_step': planning.get('current_step') or 1,
                    'is_completed': planning.get('is_completed') or False,
                    'planning_data': {
                        'planning': planning.get('planning_text', ''),
                        'stories': planning.get('stories', []),
                        'scenes': planning.get('scenes', []),
                        'shots': planning.get('shots', []),
                        'storyboards': planning.get('storyboards', [])
                    }
                })
            except Exception as item_error:
                logger.warning(f"Error processing planning item {planning.get('id', 'unknown')}: {str(item_error)}")
                continue
        
        return Response({
            'status': 'success',
            'data': {
                'planning_logs': planning_logs,
                'total_count': VideoPlanning.objects.filter(user=request.user).count()
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in get_recent_plannings: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f'      : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_structure(request):
    try:
        # planning_text  planning_input      
        planning_input = request.data.get('planning_text', '') or request.data.get('planning_input', '')
        
        if not planning_input:
            return Response({
                'status': 'error',
                'message': ' .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        gemini_service = GeminiService()
        structure_data = gemini_service.generate_structure(planning_input)
        
        if 'error' in structure_data:
            logger.error(f"Gemini API error: {structure_data['error']}")
            structure_data = structure_data.get('fallback', {})
        
        return Response({
            'status': 'success',
            'data': structure_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in generate_structure: {str(e)}")
        return Response({
            'status': 'error',
            'message': '    .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_story(request):
    #   
    logger.info(f"[generate_story] User: {request.user}, Authenticated: {request.user.is_authenticated}")
    logger.info(f"[generate_story] Auth Header: {request.META.get('HTTP_AUTHORIZATION', 'No auth header')}")
    
    try:
        planning_text = request.data.get('planning_text', '')
        tone = request.data.get('tone', '')
        genre = request.data.get('genre', '')
        concept = request.data.get('concept', '')
        target = request.data.get('target', '')
        purpose = request.data.get('purpose', '')
        duration = request.data.get('duration', '')
        story_framework = request.data.get('story_framework', 'classic')
        development_level = request.data.get('development_level', 'balanced')
        character_name = request.data.get('character_name', '')
        character_description = request.data.get('character_description', '')
        character_image = request.data.get('character_image', '')
        
        if not planning_text:
            return Response({
                'status': 'error',
                'message': '  .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #     
        context = {
            'tone': tone,
            'genre': genre,
            'concept': concept,
            'target': target,
            'purpose': purpose,
            'duration': duration,
            'story_framework': story_framework,
            'development_level': development_level,
            'character_name': character_name,
            'character_description': character_description,
            'character_image': character_image
        }
        
        gemini_service = GeminiService()
        stories_data = gemini_service.generate_stories_from_planning(planning_text, context)
        
        logger.info(f"[generate_story] Stories data response: {stories_data}")
        
        if 'error' in stories_data:
            logger.error(f"Gemini API error: {stories_data['error']}")
            # fallback  ,  stories  
            if 'stories' in stories_data:
                #   stories   (fallback stories)
                stories_data = {'stories': stories_data['stories']}
            else:
                stories_data = stories_data.get('fallback', {'stories': []})
        
        #    VideoPanning  
        if request.user.is_authenticated:
            try:
                #   (     )
                title = stories_data.get('stories', [{}])[0].get('title', '')
                if not title:
                    title = planning_text[:50] + "..." if len(planning_text) > 50 else planning_text[:50]
                
                # VideoPanning 
                video_planning = VideoPlanning.objects.create(
                    user=request.user,
                    title=title,
                    planning_text=planning_text,
                    stories=stories_data.get('stories', []),
                    current_step=1
                )
                
                # planning_data   
                planning_data = {
                    'tone': tone,
                    'genre': genre,
                    'concept': concept,
                    'target': target,
                    'purpose': purpose,
                    'duration': duration,
                    'story_framework': story_framework,
                    'development_level': development_level,
                    'character_name': character_name,
                    'character_description': character_description,
                    'character_image': character_image
                }
                # JSON     (  )
                video_planning.selected_story = {'planning_options': planning_data}
                video_planning.save()
                
                logger.info(f"VideoPanning log created for user {request.user.email}")
            except Exception as e:
                logger.error(f"Failed to create VideoPanning log: {e}")
        
        # stories   
        if not stories_data.get('stories'):
            logger.warning("No stories in response, returning empty array")
            stories_data = {'stories': []}
        
        logger.info(f"[generate_story] Final response stories count: {len(stories_data.get('stories', []))}")
        
        #    
        token_usage = gemini_service.get_token_usage()
        
        return Response({
            'status': 'success',
            'data': stories_data,
            'token_usage': token_usage
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in generate_story: {str(e)}")
        return Response({
            'status': 'error',
            'message': '    .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_scenes(request):
    try:
        story_data = request.data.get('story_data', {})
        planning_options = request.data.get('planning_options', {})
        
        if not story_data:
            return Response({
                'status': 'error',
                'message': '  .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        gemini_service = GeminiService()
        #   planning_options 
        if planning_options:
            story_data['planning_options'] = planning_options
        scenes_data = gemini_service.generate_scenes_from_story(story_data)
        
        if 'error' in scenes_data:
            logger.error(f"Gemini API error: {scenes_data['error']}")
            scenes_data = scenes_data.get('fallback', {})
        
        #    
        token_usage = gemini_service.get_token_usage()
        
        return Response({
            'status': 'success',
            'data': scenes_data,
            'token_usage': token_usage
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in generate_scenes: {str(e)}")
        return Response({
            'status': 'error',
            'message': '    .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_shots(request):
    try:
        scene_data = request.data.get('scene_data', {})
        
        if not scene_data:
            return Response({
                'status': 'error',
                'message': '  .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        gemini_service = GeminiService()
        shots_data = gemini_service.generate_shots_from_scene(scene_data)
        
        if 'error' in shots_data:
            logger.error(f"Gemini API error: {shots_data['error']}")
            shots_data = shots_data.get('fallback', {})
        
        #    
        token_usage = gemini_service.get_token_usage()
        
        return Response({
            'status': 'success',
            'data': shots_data,
            'token_usage': token_usage
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in generate_shots: {str(e)}")
        return Response({
            'status': 'error',
            'message': '    .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_storyboards(request):
    try:
        # shot_data  scene  
        shot_data = request.data.get('shot_data', {})
        scene_data = request.data.get('scene', {})
        
        # scene   shot_data 
        if not shot_data and scene_data:
            shot_data = {
                'shot_number': 1,
                'shot_type': "",
                'description': scene_data.get('action') or scene_data.get('description', ''),
                'camera_angle': "",
                'camera_movement': "",
                'duration': "5",
                'scene_info': scene_data,
                'planning_options': scene_data.get('planning_options', {})
            }
        
        style = request.data.get('style', 'minimal')
        draft_mode = request.data.get('draft_mode', True)  #  True   
        speed_optimized = request.data.get('speed_optimized', False)
        no_image = request.data.get('no_image', False)  #    
        
        #    
        if speed_optimized or style == 'quick_draft':
            draft_mode = True
            style = 'minimal'  #   minimal  
        
        if not shot_data:
            return Response({
                'status': 'error',
                'message': '  .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # API    
        logger.info("=" * 50)
        logger.info("   ")
        logger.info(f"  - : {style}")
        logger.info(f"  -  : {shot_data}")
        logger.info(f"  - IMAGE_SERVICE_AVAILABLE: {IMAGE_SERVICE_AVAILABLE}")
        logger.info(f"  - DalleService : {'' if DalleService else ''}")
        
        #    GeminiService  
        gemini_service = GeminiService()
        gemini_service.style = style  #  
        gemini_service.draft_mode = draft_mode  # draft  
        gemini_service.no_image = no_image  #    
        storyboard_data = gemini_service.generate_storyboards_from_shot(shot_data)
        
        if 'error' in storyboard_data:
            logger.error(f"Gemini API error: {storyboard_data['error']}")
            storyboard_data = storyboard_data.get('fallback', {})
            
            #     
            if IMAGE_SERVICE_AVAILABLE and DalleService:
                try:
                    dalle_service = DalleService()
                    if dalle_service.available:
                        storyboards = storyboard_data.get('storyboards', [])
                        for i, frame in enumerate(storyboards):
                            logger.info(f"Generating image for fallback frame {i+1} (draft_mode={draft_mode})")
                            image_result = dalle_service.generate_storyboard_image(frame, draft_mode=draft_mode)
                            if image_result['success']:
                                storyboard_data['storyboards'][i]['image_url'] = image_result['image_url']
                                storyboard_data['storyboards'][i]['model_used'] = image_result.get('model_used')
                                storyboard_data['storyboards'][i]['draft_mode'] = draft_mode
                            else:
                                #  
                                try:
                                    from .placeholder_image_service import PlaceholderImageService
                                    ph_service = PlaceholderImageService()
                                    ph_result = ph_service.generate_storyboard_image(frame)
                                    if ph_result['success']:
                                        storyboard_data['storyboards'][i]['image_url'] = ph_result['image_url']
                                        storyboard_data['storyboards'][i]['is_placeholder'] = True
                                except Exception as e:
                                    logger.error(f"Placeholder generation failed: {e}")
                except Exception as e:
                    logger.error(f"Image generation for fallback failed: {e}")
        
        #    
        token_usage = gemini_service.get_token_usage()
        
        return Response({
            'status': 'success',
            'data': storyboard_data,
            'token_usage': token_usage
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in generate_storyboards: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f'    : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_all_storyboards(request):
    """
         .
    """
    try:
        scenes = request.data.get('scenes', [])
        style = request.data.get('style', 'minimal')
        
        if not scenes:
            return Response({
                'status': 'error',
                'message': '  .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info("=" * 50)
        logger.info(f"     ({len(scenes)} )")
        logger.info(f"  - : {style}")
        
        #    
        if not IMAGE_SERVICE_AVAILABLE:
            return Response({
                'status': 'error',
                'message': '    .'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        try:
            dalle_service = DalleService()
            if not dalle_service.available:
                return Response({
                    'status': 'error',
                    'message': 'DALL-E    . OPENAI_API_KEY .'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': '    '
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        #   
        storyboards = []
        success_count = 0
        error_count = 0
        
        #     
        for i, scene in enumerate(scenes):
            try:
                #      (  )
                shot_data = {
                    'shot_number': 1,
                    'shot_type': "",
                    'description': scene.get('action') or scene.get('description', ''),
                    'camera_angle': "",
                    'camera_movement': "",
                    'duration': "5",
                    'scene_info': scene
                }
                
                #    GeminiService  
                gemini_service = GeminiService()
                gemini_service.style = style  #  
                storyboard_data = gemini_service.generate_storyboards_from_shot(shot_data)
                
                if 'error' in storyboard_data:
                    logger.error(f" {i+1}   : {storyboard_data['error']}")
                    storyboards.append({
                        'scene_index': i,
                        'error': storyboard_data['error'],
                        'storyboard': None
                    })
                    error_count += 1
                else:
                    #    
                    storyboard_result = storyboard_data.get('storyboards', [{}])[0] if storyboard_data.get('storyboards') else {}
                    storyboards.append({
                        'scene_index': i,
                        'error': None,
                        'storyboard': storyboard_result
                    })
                    success_count += 1
                    logger.info(f" {i+1}   ")
                
            except Exception as e:
                logger.error(f" {i+1}   : {str(e)}")
                storyboards.append({
                    'scene_index': i,
                    'error': str(e),
                    'storyboard': None
                })
                error_count += 1
        
        return Response({
            'status': 'success',
            'data': {
                'storyboards': storyboards,
                'total': len(scenes),
                'success_count': success_count,
                'error_count': error_count
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in generate_all_storyboards: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f'     : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_storyboard_image(request):
    """
      .
        
    """
    try:
        frame_data = request.data.get('frame_data', {})
        use_async = request.data.get('use_async', True)  # :  
        style = request.data.get('style', 'minimal')
        draft_mode = request.data.get('draft_mode', True)  #  True   
        
        logger.info("=" * 50)
        logger.info("    ")
        logger.info(f"  - : {style}")
        logger.info(f"  -  : {frame_data}")
        
        if not frame_data:
            return Response({
                'status': 'error',
                'message': '  .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #    
        if not IMAGE_SERVICE_AVAILABLE:
            return Response({
                'status': 'error',
                'message': '    .'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        try:
            image_service = DalleService()
            if not image_service.available:
                return Response({
                    'status': 'error',
                    'message': 'DALL-E    . OPENAI_API_KEY .'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': '    '
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        #  
        if use_async:
            #  ID 
            task_id = str(uuid.uuid4())
            
            #    
            async_generator = AsyncImageGenerator()
            
            #      
            storyboard_data = {
                'storyboards': [frame_data]
            }
            
            #     
            def generate_single_image():
                async_generator.generate_storyboard_images_async(storyboard_data, task_id)
            
            thread = threading.Thread(target=generate_single_image)
            thread.daemon = True
            thread.start()
            
            return Response({
                'status': 'success',
                'task_id': task_id,
                'message': '  . task_id   .',
                'check_status_url': f'/api/video-planning/check-image-generation-status/{task_id}/'
            }, status=status.HTTP_202_ACCEPTED)
        else:
            #   ( )
            image_result = image_service.generate_storyboard_image(frame_data, style=style, draft_mode=draft_mode)
            
            if image_result['success']:
                return Response({
                    'status': 'success',
                    'data': {
                        'image_url': image_result['image_url'],
                        'frame_number': frame_data.get('frame_number', 0)
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'error',
                    'message': image_result.get('error', '  .')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Error in regenerate_storyboard_image: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f'    : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def download_storyboard_image(request):
    try:
        image_url = request.data.get('image_url', '')
        frame_title = request.data.get('frame_title', 'storyboard')
        
        if not image_url:
            return Response({
                'status': 'error',
                'message': ' URL .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # base64  
        if image_url.startswith('data:image'):
            try:
                # data:image/png;base64,iVBORw0...  
                header, base64_data = image_url.split(',', 1)
                mime_type = header.split(':')[1].split(';')[0]
                file_extension = '.' + mime_type.split('/')[1]
                
                # base64 
                image_data = base64.b64decode(base64_data)
                
                safe_title = "".join(c for c in frame_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_title}{file_extension}"
                
                # HTTP  
                http_response = HttpResponse(
                    image_data,
                    content_type=mime_type
                )
                http_response['Content-Disposition'] = f'attachment; filename="{filename}"'
                
                return http_response
                
            except Exception as e:
                logger.error(f"Base64 image processing error: {e}")
                return Response({
                    'status': 'error',
                    'message': 'base64     .'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # URL  
        try:
            response = requests.get(image_url, timeout=30)
            
            if response.status_code != 200:
                return Response({
                    'status': 'error',
                    'message': '   .'
                }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Image download error: {e}")
            return Response({
                'status': 'error',
                'message': '    .'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        #   
        file_extension = '.png'
        parsed_url = urlparse(image_url)
        if parsed_url.path:
            _, ext = os.path.splitext(parsed_url.path)
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                file_extension = ext
        
        safe_title = "".join(c for c in frame_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title}{file_extension}"
        
        # HTTP  
        http_response = HttpResponse(
            response.content,
            content_type=f'image/{file_extension[1:]}'
        )
        http_response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return http_response
        
    except Exception as e:
        logger.error(f"Error in download_storyboard_image: {str(e)}")
        return Response({
            'status': 'error',
            'message': '    .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_planning(request):
    """ ."""
    try:
        #   
        if not request.data.get('title'):
            return Response({
                'status': 'error',
                'message': '   .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # DRF Request     api_view   
        serializer = VideoPlanningSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            planning = serializer.save()
            
            #   URL   
            storyboards = planning.storyboards
            for storyboard in storyboards:
                if 'image_url' in storyboard and storyboard['image_url']:
                    VideoPlanningImage.objects.update_or_create(
                        planning=planning,
                        frame_number=storyboard.get('frame_number', 0),
                        defaults={
                            'image_url': storyboard['image_url'],
                            'prompt_used': storyboard.get('prompt_used', '')
                        }
                    )
            
            return Response({
                'status': 'success',
                'data': {
                    'planning_id': planning.id,
                    'planning': VideoPlanningSerializer(planning).data
                },
                'message': ' .'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'status': 'error',
                'message': '  .',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error in save_planning: {str(e)}")
        return Response({
            'status': 'error',
            'message': '    .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_planning_list(request):
    """   . ( 5)"""
    try:
        #    
        if request.user.is_authenticated:
            plannings = VideoPlanning.objects.filter(
                user=request.user
            ).order_by('-created_at')[:5]
        else:
            #      
            plannings = []
        
        serializer = VideoPlanningListSerializer(plannings, many=True)
        
        return Response({
            'status': 'success',
            'data': {
                'plannings': serializer.data
            },
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in get_planning_list: {str(e)}")
        return Response({
            'status': 'error',
            'message': '     .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_planning_detail(request, planning_id):
    """    ."""
    try:
        planning = VideoPlanning.objects.filter(
            id=planning_id,
            user=request.user
        ).first()
        
        if not planning:
            return Response({
                'status': 'error',
                'message': '   .'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = VideoPlanningSerializer(planning)
        
        return Response({
            'status': 'success',
            'data': {
                'planning': serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in get_planning_detail: {str(e)}")
        return Response({
            'status': 'error',
            'message': '    .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_planning(request, planning_id):
    """  ."""
    try:
        planning = VideoPlanning.objects.filter(
            id=planning_id,
            user=request.user
        ).first()
        
        if not planning:
            return Response({
                'status': 'error',
                'message': '   .'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = VideoPlanningSerializer(
            planning,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            planning = serializer.save()
            
            #   
            if 'storyboards' in request.data:
                storyboards = request.data['storyboards']
                for storyboard in storyboards:
                    if 'image_url' in storyboard and storyboard['image_url']:
                        VideoPlanningImage.objects.update_or_create(
                            planning=planning,
                            frame_number=storyboard.get('frame_number', 0),
                            defaults={
                                'image_url': storyboard['image_url'],
                                'prompt_used': storyboard.get('prompt_used', '')
                            }
                        )
            
            return Response({
                'status': 'success',
                'data': VideoPlanningSerializer(planning).data,
                'message': ' .'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': '  .',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error in update_planning: {str(e)}")
        return Response({
            'status': 'error',
            'message': '    .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_planning(request, planning_id):
    """ ."""
    try:
        planning = VideoPlanning.objects.filter(
            id=planning_id,
            user=request.user
        ).first()
        
        if not planning:
            return Response({
                'status': 'error',
                'message': '   .'
            }, status=status.HTTP_404_NOT_FOUND)
        
        planning.delete()
        
        return Response({
            'status': 'success',
            'message': ' .'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in delete_planning: {str(e)}")
        return Response({
            'status': 'error',
            'message': '    .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def planning_library_view(request):
    """  - GET POST  """
    if request.method == 'GET':
        #     
        try:
            plannings = VideoPlanning.objects.filter(
                user=request.user
            ).order_by('-created_at')
            
            planning_list = []
            for planning in plannings:
                planning_list.append({
                    'id': planning.id,
                    'title': planning.title or ' ',
                    'created_at': planning.created_at.strftime('%Y-%m-%d %H:%M') if planning.created_at else '',
                    'updated_at': planning.updated_at.strftime('%Y-%m-%d %H:%M') if planning.updated_at else '',
                    'is_completed': planning.is_completed,
                    'current_step': planning.current_step,
                    'thumbnail': planning.thumbnail_url if hasattr(planning, 'thumbnail_url') else None,
                    'planning_options': planning.planning_options if hasattr(planning, 'planning_options') else {},
                    'scene_count': len(planning.scenes) if planning.scenes else 0,
                    'has_storyboards': bool(planning.storyboards) if planning.storyboards else False
                })
            
            return Response({
                'status': 'success',
                'data': {
                    'plannings': planning_list,
                    'total_count': len(planning_list)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in planning_library_view GET: {str(e)}", exc_info=True)
            return Response({
                'status': 'error',
                'message': f'     : {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    elif request.method == 'POST':
        return save_planning(request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_to_pdf(request):
    """  PDF """
    try:
        planning_data = request.data.get('planning_data', {})
        export_type = request.data.get('export_type', 'full')  # 'full' or 'storyboard_only'
        use_enhanced_layout = request.data.get('use_enhanced_layout', True)  #    
        
        if not planning_data:
            return Response({
                'status': 'error',
                'message': '  .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #     JSON  
        logger.info("PDF    (JSON):")
        logger.info(json.dumps(planning_data, ensure_ascii=False, indent=2))
        
        # planning_options    
        if 'planning_options' not in planning_data:
            planning_data['planning_options'] = {}
        
        # PDF   
        use_compressed = request.data.get('use_compressed', True)  #   
        
        if use_compressed:
            #    (LLM  )
            pdf_service = CompressedPDFExportService()
            pdf_buffer = pdf_service.generate_pdf(planning_data)
        elif use_enhanced_layout:
            #    
            pdf_service = EnhancedPDFExportService()
            pdf_buffer = pdf_service.generate_pdf(planning_data)
        else:
            #    
            pdf_service = PDFExportService()
            if export_type == 'storyboard_only':
                pdf_buffer = pdf_service.generate_storyboard_only_pdf(planning_data)
            else:
                pdf_buffer = pdf_service.generate_pdf(planning_data)
        
        #  
        title = planning_data.get('title', '')
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        #   
        if use_compressed:
            layout_suffix = '_'
        elif use_enhanced_layout:
            layout_suffix = '_'
        else:
            layout_suffix = ''
        
        filename = f"{safe_title}_{'' if export_type == 'storyboard_only' else ''}{layout_suffix}.pdf"
        
        #   
        response = FileResponse(
            pdf_buffer,
            content_type='application/pdf',
            as_attachment=True,
            filename=filename
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in export_to_pdf: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f'PDF    : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_to_google_slides(request):
    """  Google Slides """
    try:
        planning_data = request.data.get('planning_data', {})
        
        if not planning_data:
            return Response({
                'status': 'error',
                'message': '  .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Google Slides 
        slides_service = GoogleSlidesService()
        
        #  
        title = planning_data.get('title', ' ')
        result = slides_service.create_presentation(title, planning_data)
        
        if 'error' in result:
            logger.error(f"Google Slides  : {result['error']}")
            return Response({
                'status': 'error',
                'message': result['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'status': 'success',
            'data': {
                'presentation_id': result['presentation_id'],
                'url': result['url']
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in export_to_google_slides: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f'Google Slides    : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_to_advanced_pdf(request):
    """AI    PDF """
    try:
        planning_data = request.data.get('planning_data', {})
        
        if not planning_data:
            return Response({
                'status': 'error',
                'message': '  .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #  PDF 
        advanced_pdf_service = AdvancedPDFExportService()
        
        # PDF 
        pdf_bytes = advanced_pdf_service.export_to_pdf(planning_data)
        
        if not pdf_bytes:
            return Response({
                'status': 'error',
                'message': 'PDF  .'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        #  
        title = planning_data.get('title', '')
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title}_AI_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # PDF 
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error in export_to_advanced_pdf: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f' PDF    : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_to_enhanced_pdf(request):
    """   PDF  ( A4)"""
    try:
        planning_data = request.data.get('planning_data', {})
        
        if not planning_data:
            return Response({
                'status': 'error',
                'message': '  .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #  PDF 
        enhanced_pdf_service = EnhancedPDFExportService()
        
        # PDF 
        pdf_buffer = enhanced_pdf_service.generate_pdf(planning_data)
        
        if not pdf_buffer:
            return Response({
                'status': 'error',
                'message': 'PDF  .'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        #  
        title = planning_data.get('title', '')
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title}__{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # PDF 
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error in export_to_enhanced_pdf: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f' PDF    : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_export_formats(request):
    """    """
    try:
        formats = [
            {
                'id': 'pdf_full',
                'name': 'PDF -  ',
                'description': '    ',
                'icon': 'file-pdf',
                'available': True
            },
            {
                'id': 'pdf_storyboard',
                'name': 'PDF - ',
                'description': '    ',
                'icon': 'file-image',
                'available': True
            },
            {
                'id': 'google_slides',
                'name': 'Google Slides',
                'description': '   ',
                'icon': 'file-presentation',
                'available': bool(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
            },
            {
                'id': 'pdf_advanced',
                'name': 'PDF - AI ',
                'description': 'Gemini AI    ',
                'icon': 'file-pdf-box',
                'available': bool(os.environ.get('GOOGLE_API_KEY'))
            },
            {
                'id': 'ai_proposal',
                'name': 'AI  (Google Slides)',
                'description': 'AI    ',
                'icon': 'robot',
                'available': bool(os.environ.get('GOOGLE_API_KEY') and os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
            },
            {
                'id': 'pdf_enhanced',
                'name': 'PDF -   ()',
                'description': '    A4  ',
                'icon': 'file-table',
                'available': True
            }
        ]
        
        return Response({
            'status': 'success',
            'data': {
                'formats': formats
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in get_export_formats: {str(e)}")
        return Response({
            'status': 'error',
            'message': '     .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================================
# AI   API 
# ================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_ai_prompt(request):
    """
    AI   - 1000%     
    """
    try:
        data = request.data
        planning_id = data.get('planning_id')
        prompt_type = data.get('prompt_type')  # story, scene, shot, image
        user_input = data.get('user_input', '')
        optimization_level = data.get('optimization_level', 'high')  # low, medium, high, extreme
        
        #  
        if not planning_id:
            return Response({
                'status': 'error',
                'message': ' ID .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not prompt_type:
            return Response({
                'status': 'error',
                'message': '  .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if prompt_type not in ['story', 'scene', 'shot', 'image', 'storyboard']:
            return Response({
                'status': 'error',
                'message': '   .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #     
        try:
            planning = VideoPlanning.objects.get(id=planning_id, user=request.user)
        except VideoPlanning.DoesNotExist:
            return Response({
                'status': 'error',
                'message': '      .'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # AI    
        prompt_service = PromptOptimizationService()
        
        if prompt_type == 'story':
            result = prompt_service.generate_story_prompt(planning, user_input, optimization_level)
        elif prompt_type == 'scene':
            result = prompt_service.generate_scene_prompt(planning, user_input, optimization_level)
        elif prompt_type == 'shot':
            result = prompt_service.generate_shot_prompt(planning, user_input, optimization_level)
        elif prompt_type in ['image', 'storyboard']:
            result = prompt_service.generate_image_prompt(planning, user_input, optimization_level)
        
        if result.is_successful:
            response_data = {
                'status': 'success',
                'data': {
                    'original_prompt': result.original_prompt,
                    'enhanced_prompt': result.enhanced_prompt,
                    'generation_time': result.generation_time,
                    'tokens_estimate': result.tokens_estimate,
                    'cost_estimate': result.cost_estimate,
                    'confidence_score': result.confidence_score,
                    'optimization_suggestions': result.optimization_suggestions
                },
                'message': 'AI   .'
            }
            
            #   
            try:
                analytics, created = planning.analytics.get_or_create(planning=planning)
                analytics.update_metrics()
            except Exception as e:
                logger.warning(f"   : {str(e)}")
            
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': f'  : {result.error_message}',
                'data': {
                    'generation_time': result.generation_time
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"AI   : {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f'    : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_prompt_analytics(request, planning_id):
    """
    AI    
    """
    try:
        #     
        try:
            planning = VideoPlanning.objects.get(id=planning_id, user=request.user)
        except VideoPlanning.DoesNotExist:
            return Response({
                'status': 'error',
                'message': '      .'
            }, status=status.HTTP_404_NOT_FOUND)
        
        #   
        prompt_service = PromptOptimizationService()
        analytics_data = prompt_service.get_optimization_analytics(planning)
        
        return Response({
            'status': 'success',
            'data': analytics_data,
            'message': '   .'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"   : {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f'     : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_prompt_history(request, planning_id):
    """
    AI    
    """
    try:
        #     
        try:
            planning = VideoPlanning.objects.get(id=planning_id, user=request.user)
        except VideoPlanning.DoesNotExist:
            return Response({
                'status': 'error',
                'message': '      .'
            }, status=status.HTTP_404_NOT_FOUND)
        
        #   
        prompts = VideoPlanningAIPrompt.objects.filter(planning=planning).order_by('-created_at')
        
        # 
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        total_count = prompts.count()
        prompts_page = prompts[start_idx:end_idx]
        
        #  
        prompt_data = []
        for prompt in prompts_page:
            prompt_data.append({
                'id': prompt.id,
                'prompt_type': prompt.prompt_type,
                'prompt_type_display': prompt.get_prompt_type_display(),
                'original_prompt': prompt.original_prompt[:200] + "..." if len(prompt.original_prompt) > 200 else prompt.original_prompt,
                'enhanced_prompt': prompt.enhanced_prompt[:200] + "..." if len(prompt.enhanced_prompt) > 200 else prompt.enhanced_prompt,
                'is_successful': prompt.is_successful,
                'generation_time': prompt.generation_time,
                'tokens_used': prompt.tokens_used,
                'cost_estimate': float(prompt.cost_estimate) if prompt.cost_estimate else 0,
                'created_at': prompt.created_at.isoformat(),
                'error_message': prompt.error_message
            })
        
        return Response({
            'status': 'success',
            'data': {
                'prompts': prompt_data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': (total_count + page_size - 1) // page_size,
                    'has_next': end_idx < total_count,
                    'has_prev': page > 1
                }
            },
            'message': '   .'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"   : {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f'    : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_pro_settings(request, planning_id):
    """
        
    """
    try:
        #     
        try:
            planning = VideoPlanning.objects.get(id=planning_id, user=request.user)
        except VideoPlanning.DoesNotExist:
            return Response({
                'status': 'error',
                'message': '      .'
            }, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        updated_fields = []
        
        #    (color_tone  )
        # if 'color_tone' in data:
        #     planning.color_tone = data['color_tone']
        #     updated_fields.append('color_tone')
        
        #    ( )
        # if 'camera_settings' in data:
        #     planning.camera_settings = data['camera_settings']
        #     updated_fields.append('camera_settings')
        
        #    ( )
        # if 'lighting_setup' in data:
        #     planning.lighting_setup = data['lighting_setup']
        #     updated_fields.append('lighting_setup')
        
        #    ( )
        # if 'audio_config' in data:
        #     planning.audio_config = data['audio_config']
        #     updated_fields.append('audio_config')
        
        # AI    ( )
        # if 'ai_generation_config' in data:
        #     planning.ai_generation_config = data['ai_generation_config']
        #     updated_fields.append('ai_generation_config')
        
        #    ( )
        # if 'collaboration_settings' in data:
        #     planning.collaboration_settings = data['collaboration_settings']
        #     updated_fields.append('collaboration_settings')
        
        #    ( )
        # if 'workflow_config' in data:
        #     planning.workflow_config = data['workflow_config']
        #     updated_fields.append('workflow_config')
        
        if updated_fields:
            planning.save(update_fields=updated_fields + ['updated_at'])
            
            return Response({
                'status': 'success',
                'data': {
                    'updated_fields': updated_fields,
                    'pro_mode_enabled': planning.is_pro_mode_enabled()
                },
                'message': '   .'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': '  .'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"   : {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f'    : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pro_templates(request):
    """
         
    """
    try:
        from .models import VideoPlanningProTemplate
        
        #   
        templates = VideoPlanningProTemplate.objects.filter(is_active=True).order_by('-usage_count', 'name')
        
        #  
        category = request.GET.get('category')
        if category:
            templates = templates.filter(category=category)
        
        template_data = []
        for template in templates:
            template_data.append({
                'id': template.id,
                'name': template.name,
                'category': template.category,
                'description': template.description,
                'default_color_tone': template.default_color_tone,
                'default_camera_settings': template.default_camera_settings,
                'default_lighting_setup': template.default_lighting_setup,
                'default_audio_config': template.default_audio_config,
                'usage_count': template.usage_count,
                'created_at': template.created_at.isoformat()
            })
        
        #    
        categories = VideoPlanningProTemplate.objects.filter(is_active=True).values_list('category', flat=True).distinct()
        
        return Response({
            'status': 'success',
            'data': {
                'templates': template_data,
                'categories': list(categories)
            },
            'message': '   .'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"   : {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f'    : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_pro_template(request, planning_id, template_id):
    """
       
    """
    try:
        from .models import VideoPlanningProTemplate
        
        #     
        try:
            planning = VideoPlanning.objects.get(id=planning_id, user=request.user)
        except VideoPlanning.DoesNotExist:
            return Response({
                'status': 'error',
                'message': '      .'
            }, status=status.HTTP_404_NOT_FOUND)
        
        #  
        try:
            template = VideoPlanningProTemplate.objects.get(id=template_id, is_active=True)
        except VideoPlanningProTemplate.DoesNotExist:
            return Response({
                'status': 'error',
                'message': '   .'
            }, status=status.HTTP_404_NOT_FOUND)
        
        #   ( )
        # planning.color_tone = template.default_color_tone
        # planning.camera_settings = template.default_camera_settings
        # planning.lighting_setup = template.default_lighting_setup
        # planning.audio_config = template.default_audio_config
        
        planning.save(update_fields=['updated_at'])
        
        #    
        template.increment_usage()
        
        return Response({
            'status': 'success',
            'data': {
                'template_name': template.name,
                'applied_settings': {
                    #  
                    # 'color_tone': planning.color_tone,
                    # 'camera_settings': planning.camera_settings,
                    # 'lighting_setup': planning.lighting_setup,
                    # 'audio_config': planning.audio_config
                }
            },
            'message': f'"{template.name}"   .'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"   : {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f'    : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================================
# AI     (30 )
# ================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_quick_suggestions(request):
    """AI    -    """
    try:
        from .ai_prompt_generator import VideoPlanningPromptGenerator
        
        generator = VideoPlanningPromptGenerator()
        suggestions = generator.generate_quick_suggestions(request.data)
        
        return Response({
            'status': 'success',
            'suggestions': suggestions,
            'message': 'AI  .'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"AI   : {str(e)}")
        return Response({
            'status': 'error',
            'message': f'AI     : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_generate_full_planning(request):
    """ AI   - 30  """
    try:
        from .ai_prompt_generator import VideoPlanningPromptGenerator
        
        generator = VideoPlanningPromptGenerator()
        planning = generator.generate_full_planning(request.data)
        
        #    
        if request.data.get('save_to_library', False):
            video_planning = VideoPlanning.objects.create(
                user=request.user,
                title=planning['title'],
                planning=planning['planning'],
                # color_tone=planning.get('pro_options', {}).get('colorTone'),  #  
                camera_settings={
                    'type': planning.get('pro_options', {}).get('cameraType'),
                    'lens': planning.get('pro_options', {}).get('lensType'),
                    'movement': planning.get('pro_options', {}).get('cameraMovement')
                } if planning.get('pro_options') else None
            )
            
            #  
            for story_data in planning.get('stories', []):
                VideoPlanningStory.objects.create(
                    planning=video_planning,
                    stage=story_data['stage'],
                    stage_name=story_data['stage_name'],
                    content=story_data['content'],
                    order=story_data['order']
                )
            
            #  
            for scene_data in planning.get('scenes', []):
                VideoPlanningScene.objects.create(
                    planning=video_planning,
                    story_index=scene_data['story_index'],
                    scene_number=scene_data['scene_number'],
                    title=scene_data['title'],
                    description=scene_data['description'],
                    duration=scene_data['duration']
                )
            
            planning['id'] = video_planning.id
        
        return Response({
            'status': 'success',
            'planning': planning,
            'message': 'AI   !'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"AI   : {str(e)}")
        return Response({
            'status': 'error',
            'message': f'AI     : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_veo3_prompt(request):
    """VEO3    """
    try:
        from .ai_prompt_generator import VEO3PromptGenerator
        
        generator = VEO3PromptGenerator()
        scene_data = request.data.get('scene_data', {})
        pro_options = request.data.get('pro_options', {})
        
        video_prompt = generator.generate_video_prompt(scene_data, pro_options)
        image_prompt = generator.generate_image_prompt(scene_data, pro_options)
        
        return Response({
            'status': 'success',
            'data': {
                'video_prompt': video_prompt,
                'image_prompt': image_prompt,
                'scene_title': scene_data.get('title', ''),
                'technical_specs': pro_options
            },
            'message': 'VEO3  .'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"VEO3   : {str(e)}")
        return Response({
            'status': 'error',
            'message': f'VEO3     : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_project(request):
    """   -      """
    try:
        planning_id = request.data.get('planning_id')
        final_video_url = request.data.get('final_video_url')
        completion_notes = request.data.get('completion_notes', '')
        
        #   
        video_file = request.FILES.get('video_file')
        
        if not planning_id:
            return Response({
                'status': 'error',
                'message': ' ID .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #  
        planning = VideoPlanning.objects.filter(
            id=planning_id,
            user=request.user
        ).first()
        
        if not planning:
            return Response({
                'status': 'error',
                'message': '   .'
            }, status=status.HTTP_404_NOT_FOUND)
        
        #     
        if video_file:
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            import os
            
            #  
            file_name = f"completed_videos/{planning_id}_{video_file.name}"
            path = default_storage.save(file_name, ContentFile(video_file.read()))
            final_video_url = request.build_absolute_uri(default_storage.url(path))
        
        #   
        planning_data = planning.planning_data or {}
        planning_data['completed'] = True
        planning_data['completed_at'] = timezone.now().isoformat()
        planning_data['final_video_url'] = final_video_url
        planning_data['completion_notes'] = completion_notes
        
        planning.planning_data = planning_data
        planning.save()
        
        return Response({
            'status': 'success',
            'message': '  !',
            'data': {
                'planning_id': planning.id,
                'completed_at': planning_data['completed_at'],
                'final_video_url': final_video_url
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"   : {str(e)}")
        return Response({
            'status': 'error',
            'message': f'     : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_storyboard_images_async(request):
    """
       .
      ID ,   .
    """
    try:
        storyboard_data = request.data.get('storyboard_data', {})
        
        if not storyboard_data or not storyboard_data.get('storyboards'):
            return Response({
                'status': 'error',
                'message': '  .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #  ID 
        task_id = str(uuid.uuid4())
        
        #    
        async_generator = AsyncImageGenerator()
        
        #     
        def generate_images():
            async_generator.generate_storyboard_images_async(storyboard_data, task_id)
        
        thread = threading.Thread(target=generate_images)
        thread.daemon = True
        thread.start()
        
        return Response({
            'status': 'success',
            'task_id': task_id,
            'message': '  . task_id   .'
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        logger.error(f"Error in generate_storyboard_images_async: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f'      : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_image_generation_status(request, task_id):
    """
         .
    """
    try:
        async_generator = AsyncImageGenerator()
        status_data = async_generator.get_generation_status(task_id)
        
        if status_data.get('status') == 'completed':
            #     
            result = async_generator.get_generation_result(task_id)
            return Response({
                'status': 'success',
                'task_status': status_data,
                'result': result
            }, status=status.HTTP_200_OK)
        else:
            #      
            return Response({
                'status': 'success',
                'task_status': status_data
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Error in check_image_generation_status: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f'    : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)