from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
import logging
import json

from feedbacks.models import FeedBack
from .models import VideoAnalysisResult, AIFeedbackItem
from .serializers import VideoAnalysisResultSerializer, AIFeedbackItemSerializer

logger = logging.getLogger(__name__)

# Graceful import handling for development environment
try:
    from .twelve_labs_service import TwelveLabsService
    from .ai_teacher_service import AITeacherService
    SERVICES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"AI services not available in development: {e}")
    TwelveLabsService = None
    AITeacherService = None
    SERVICES_AVAILABLE = False


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_feedback_video(request, feedback_id):
    """
       
    """
    if not SERVICES_AVAILABLE:
        return Response({
            'status': 'error',
            'message': 'AI      .'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    try:
        #   
        feedback = get_object_or_404(FeedBack, id=feedback_id)
        
        #   ( )
        project = feedback.project_feedback.first()
        if project and not project.members.filter(user=request.user).exists():
            return Response({
                'status': 'error',
                'message': '      .'
            }, status=status.HTTP_403_FORBIDDEN)
        
        #     
        existing_analysis = VideoAnalysisResult.objects.filter(feedback=feedback).first()
        if existing_analysis:
            if existing_analysis.status == 'processing':
                return Response({
                    'status': 'info',
                    'message': '   .',
                    'data': VideoAnalysisResultSerializer(existing_analysis).data
                }, status=status.HTTP_200_OK)
            elif existing_analysis.status == 'completed':
                return Response({
                    'status': 'info',
                    'message': '  .',
                    'data': VideoAnalysisResultSerializer(existing_analysis).data
                }, status=status.HTTP_200_OK)
        
        #   URL 
        video_url = None
        if feedback.files:
            #   
            video_url = request.build_absolute_uri(feedback.files.url)
        elif feedback.video_file_web:
            #    
            video_url = request.build_absolute_uri(f"/media/{feedback.video_file_web}")
        else:
            return Response({
                'status': 'error',
                'message': '   .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #    
        with transaction.atomic():
            analysis_result = VideoAnalysisResult.objects.create(
                feedback=feedback,
                status='pending',
                created_by=request.user,
                analysis_type='twelve_labs'
            )
        
        # Twelve Labs  
        try:
            twelve_labs = TwelveLabsService()
        except ValueError as e:
            analysis_result.status = 'failed'
            analysis_result.error_message = str(e)
            analysis_result.save()
            
            return Response({
                'status': 'error',
                'message': 'Twelve Labs API   .'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        #   
        analysis_result.status = 'processing'
        analysis_result.processing_started_at = timezone.now()
        analysis_result.save()
        
        #  
        metadata = {
            "feedback_id": str(feedback_id),
            "project_id": str(project.id) if project else None,
            "uploaded_by": request.user.email,
            "original_filename": feedback.files.name if feedback.files else "unknown"
        }
        
        # Twelve Labs  
        upload_result = twelve_labs.upload_video(
            video_url=video_url,
            video_name=f"feedback_{feedback_id}",
            metadata=metadata
        )
        
        if not upload_result['success']:
            analysis_result.status = 'failed'
            analysis_result.error_message = upload_result.get('error', '  ')
            analysis_result.processing_completed_at = timezone.now()
            analysis_result.save()
            
            return Response({
                'status': 'error',
                'message': '  .',
                'error': upload_result.get('error')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        #  ID 
        analysis_result.external_video_id = upload_result.get('video_id')
        analysis_result.save()
        
        #   
        if upload_result.get('video_id'):
            analysis_data = twelve_labs.analyze_video(upload_result['video_id'])
            
            if analysis_data['success']:
                #   
                analysis_result.analysis_data = analysis_data['analysis']
                analysis_result.overall_score = 85  #   (    )
                analysis_result.status = 'completed'
                analysis_result.processing_completed_at = timezone.now()
                
                #    
                _create_feedback_items(analysis_result, analysis_data['analysis'])
                
            else:
                analysis_result.status = 'failed'
                analysis_result.error_message = analysis_data.get('error', ' ')
                analysis_result.processing_completed_at = timezone.now()
        else:
            analysis_result.status = 'failed'
            analysis_result.error_message = ' ID  .'
            analysis_result.processing_completed_at = timezone.now()
        
        analysis_result.save()
        
        return Response({
            'status': 'success',
            'message': '  .',
            'data': VideoAnalysisResultSerializer(analysis_result).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': '    .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _create_feedback_items(analysis_result, analysis_data):
    """     """
    try:
        #   
        if analysis_data.get('summary', {}).get('text'):
            AIFeedbackItem.objects.create(
                analysis_result=analysis_result,
                category='summary',
                severity='info',
                title=' ',
                description=analysis_data['summary']['text'],
                confidence_score=0.9
            )
        
        #   
        key_moments = analysis_data.get('key_moments', [])
        for i, moment in enumerate(key_moments[:5]):  #  5
            AIFeedbackItem.objects.create(
                analysis_result=analysis_result,
                category='key_moment',
                severity='info',
                title=f'  #{i+1}',
                description=f"{moment['start_time']:.1f} - {moment['end_time']:.1f}",
                timestamp=moment['start_time'],
                confidence_score=moment.get('confidence', 0.8),
                metadata={'thumbnail_url': moment.get('thumbnail_url')}
            )
        
        #    
        texts_in_video = analysis_data.get('text_in_video', [])
        if texts_in_video:
            text_summary = '\n'.join([f"[{t['start_time']:.1f}s] {t['text']}" for t in texts_in_video[:10]])
            AIFeedbackItem.objects.create(
                analysis_result=analysis_result,
                category='text_detection',
                severity='info',
                title='  ',
                description=text_summary,
                confidence_score=0.85
            )
        
        #   
        conversations = analysis_data.get('conversations', [])
        if conversations:
            conv_summary = '\n'.join([f"[{c['start_time']:.1f}s] {c['transcript']}" for c in conversations[:5]])
            AIFeedbackItem.objects.create(
                analysis_result=analysis_result,
                category='conversation',
                severity='info',
                title='  ',
                description=conv_summary,
                confidence_score=0.9
            )
            
    except Exception as e:
        logger.error(f"Error creating feedback items: {e}")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analysis_result(request, feedback_id):
    """
      
    """
    try:
        feedback = get_object_or_404(FeedBack, id=feedback_id)
        
        #  
        project = feedback.project_feedback.first()
        if project and not project.members.filter(user=request.user).exists():
            return Response({
                'status': 'error',
                'message': '       .'
            }, status=status.HTTP_403_FORBIDDEN)
        
        analysis_result = VideoAnalysisResult.objects.filter(feedback=feedback).first()
        
        if not analysis_result:
            return Response({
                'status': 'info',
                'message': '  .'
            }, status=status.HTTP_404_NOT_FOUND)
        
        #    
        feedback_items = AIFeedbackItem.objects.filter(
            analysis_result=analysis_result
        ).order_by('-severity', '-confidence_score')
        
        return Response({
            'status': 'success',
            'data': {
                'analysis': VideoAnalysisResultSerializer(analysis_result).data,
                'feedback_items': AIFeedbackItemSerializer(feedback_items, many=True).data
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error retrieving analysis result: {str(e)}")
        return Response({
            'status': 'error',
            'message': '     .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_in_videos(request):
    """
       
    """
    try:
        query = request.data.get('query', '')
        options = request.data.get('options', ['visual', 'conversation', 'text_in_video'])
        limit = request.data.get('limit', 10)
        
        if not query:
            return Response({
                'status': 'error',
                'message': ' .'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Twelve Labs  
        try:
            twelve_labs = TwelveLabsService()
        except ValueError:
            return Response({
                'status': 'error',
                'message': 'Twelve Labs API   .'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        #   
        search_results = twelve_labs.search_in_videos(
            query=query,
            options=options,
            limit=limit
        )
        
        #     
        enriched_results = []
        for result in search_results:
            # external_video_id   
            analysis = VideoAnalysisResult.objects.filter(
                external_video_id=result['video_id']
            ).first()
            
            if analysis and analysis.feedback:
                #  
                project = analysis.feedback.project_feedback.first()
                if project and project.members.filter(user=request.user).exists():
                    result['feedback_id'] = analysis.feedback.id
                    result['feedback_title'] = f"Feedback #{analysis.feedback.id}"
                    result['project_name'] = project.name if project else None
                    enriched_results.append(result)
        
        return Response({
            'status': 'success',
            'data': {
                'query': query,
                'results': enriched_results,
                'total': len(enriched_results)
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error searching videos: {str(e)}")
        return Response({
            'status': 'error',
            'message': '    .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_analysis(request, feedback_id):
    """
      
    """
    try:
        feedback = get_object_or_404(FeedBack, id=feedback_id)
        
        #   ( )
        project = feedback.project_feedback.first()
        if project:
            member = project.members.filter(user=request.user, member_type='manager').first()
            if not member:
                return Response({
                    'status': 'error',
                    'message': '      .'
                }, status=status.HTTP_403_FORBIDDEN)
        
        analysis_result = VideoAnalysisResult.objects.filter(feedback=feedback).first()
        
        if not analysis_result:
            return Response({
                'status': 'info',
                'message': '   .'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Twelve Labs  
        if analysis_result.external_video_id:
            try:
                twelve_labs = TwelveLabsService()
                twelve_labs.delete_video(analysis_result.external_video_id)
            except Exception as e:
                logger.error(f"Failed to delete video from Twelve Labs: {e}")
        
        #    (CASCADE AIFeedbackItem  )
        analysis_result.delete()
        
        return Response({
            'status': 'success',
            'message': '  .'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error deleting analysis: {str(e)}")
        return Response({
            'status': 'error',
            'message': '     .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_teacher_feedback(request, feedback_id):
    """
    AI   
    """
    try:
        #   
        analysis_result = get_object_or_404(
            VideoAnalysisResult,
            feedback_id=feedback_id,
            status='completed'
        )
        
        #  
        project = analysis_result.feedback.project_feedback.first()
        if project and not project.members.filter(user=request.user).exists():
            return Response({
                'status': 'error',
                'message': '      .'
            }, status=status.HTTP_403_FORBIDDEN)
        
        #  
        teacher_type = request.data.get('teacher_type', 'owl')
        
        # AI   
        teacher_service = AITeacherService()
        
        #  
        teacher_feedback = teacher_service.transform_feedback(
            analysis_result.analysis_data,
            teacher_type
        )
        
        #   AIFeedbackItem 
        feedback_data = teacher_feedback['feedback']
        teacher_info = teacher_feedback['teacher']
        
        #     ( )
        AIFeedbackItem.objects.filter(
            analysis_result=analysis_result,
            category='teacher_feedback',
            metadata__teacher_type=teacher_type
        ).delete()
        
        #   
        overall_item = AIFeedbackItem.objects.create(
            analysis_result=analysis_result,
            category='teacher_feedback',
            severity='info',
            title=f"{teacher_info['name']}  ",
            description=feedback_data['overall_feedback'],
            confidence_score=feedback_data.get('score', 75) / 100,
            metadata={
                'teacher_type': teacher_type,
                'teacher_name': teacher_info['name'],
                'emoji': teacher_info['emoji'],
                'score': feedback_data.get('score', 75),
                'emoji_reaction': feedback_data.get('emoji_reaction', '')
            }
        )
        
        #  
        for strength in feedback_data.get('strengths', []):
            AIFeedbackItem.objects.create(
                analysis_result=analysis_result,
                category='teacher_strength',
                severity='low',
                title='',
                description=strength,
                confidence_score=0.9,
                metadata={'teacher_type': teacher_type}
            )
        
        #  
        for improvement in feedback_data.get('improvements', []):
            AIFeedbackItem.objects.create(
                analysis_result=analysis_result,
                category='teacher_improvement',
                severity='medium',
                title='',
                description=improvement,
                confidence_score=0.9,
                metadata={'teacher_type': teacher_type}
            )
        
        #   
        for comment in feedback_data.get('specific_comments', []):
            AIFeedbackItem.objects.create(
                analysis_result=analysis_result,
                category='teacher_comment',
                severity='info',
                title=' ',
                description=comment['comment'],
                timestamp=comment['timestamp'],
                confidence_score=0.85,
                metadata={'teacher_type': teacher_type}
            )
        
        #  
        AIFeedbackItem.objects.create(
            analysis_result=analysis_result,
            category='teacher_final',
            severity='info',
            title=' ',
            description=feedback_data.get('final_message', ''),
            confidence_score=1.0,
            metadata={'teacher_type': teacher_type}
        )
        
        return Response({
            'status': 'success',
            'data': {
                'teacher': teacher_info,
                'feedback': feedback_data,
                'analysis_summary': teacher_feedback.get('analysis_summary', {})
            }
        }, status=status.HTTP_200_OK)
        
    except VideoAnalysisResult.DoesNotExist:
        return Response({
            'status': 'error',
            'message': '    .'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting teacher feedback: {str(e)}")
        return Response({
            'status': 'error',
            'message': '     .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_all_teachers(request):
    """
     AI   
    """
    try:
        # AI    (   )
        teachers = {
            'tiger': {
                'name': ' ',
                'emoji': '',
                'personality': ' ',
                'style': '  ',
                'tone': ' ',
                'greeting': '! ,      !',
                'color': '#FF6B35',
                'bg_color': '#FFF5F0'
            },
            'owl': {
                'name': ' ',
                'emoji': '',
                'personality': ' ',
                'style': '   ',
                'tone': ' ',
                'greeting': '~   .     .',
                'color': '#8B4513',
                'bg_color': '#FFF8DC'
            },
            'dolphin': {
                'name': ' ',
                'emoji': '',
                'personality': ' ',
                'style': '  ',
                'tone': ' ',
                'greeting': '~ !    ?',
                'color': '#4169E1',
                'bg_color': '#F0F8FF'
            },
            'eagle': {
                'name': ' ',
                'emoji': '',
                'personality': ' ',
                'style': '  ',
                'tone': ' ',
                'greeting': '~     .',
                'color': '#8B4513',
                'bg_color': '#FFFAF0'
            }
        }
        
        return Response({
            'status': 'success',
            'data': {
                'teachers': teachers
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting teachers: {str(e)}")
        return Response({
            'status': 'error',
            'message': '     .'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)