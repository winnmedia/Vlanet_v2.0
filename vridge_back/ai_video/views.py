"""
API Views for AI Video Generation
Implementing REST endpoints with proper error handling and permissions
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.db import transaction
import logging

# django_filters  
try:
    from django_filters.rest_framework import DjangoFilterBackend
    HAS_DJANGO_FILTERS = True
except ImportError:
    DjangoFilterBackend = None
    HAS_DJANGO_FILTERS = False

from .models import (
    Story, Scene, ScenePrompt, Job,
    StoryStatus, JobStatus, StoryStateTransition
)
from .serializers import (
    StorySerializer, SceneSerializer, ScenePromptSerializer,
    JobSerializer, StoryTransitionSerializer, CreateSceneSerializer,
    BulkSceneCreateSerializer, GeneratePreviewSerializer,
    RenderFinalVideoSerializer, JobRetrySerializer,
    StoryStateTransitionSerializer
)
from .services import AIVideoService, QueueService, StorageService
from .permissions import IsOwnerOrReadOnly

logger = logging.getLogger(__name__)


class StoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Story CRUD operations and workflow management
    """
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] + ([DjangoFilterBackend] if HAS_DJANGO_FILTERS else [])
    filterset_fields = ['status', 'project', 'ai_provider'] if HAS_DJANGO_FILTERS else []
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter stories by current user"""
        queryset = Story.objects.filter(user=self.request.user)
        
        # Prefetch related data for performance
        queryset = queryset.prefetch_related(
            'scenes',
            'scenes__prompts',
            'jobs'
        ).select_related('project', 'user')
        
        # Additional filters from query params
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set user when creating story"""
        serializer.save(user=self.request.user)
        
        # Create initial job for story planning
        story = serializer.instance
        QueueService.create_planning_job(story)
    
    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        """
        Transition story to a new status
        POST /api/ai-video/stories/{id}/transition/
        """
        story = self.get_object()
        serializer = StoryTransitionSerializer(
            data=request.data,
            context={'story': story}
        )
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['new_status']
        reason = serializer.validated_data.get('reason', '')
        
        try:
            with transaction.atomic():
                story.transition_to(new_status)
                
                # Trigger appropriate jobs based on transition
                if new_status == StoryStatus.PLANNING:
                    QueueService.create_planning_job(story)
                elif new_status == StoryStatus.PREVIEWING:
                    QueueService.create_preview_job(story)
                elif new_status == StoryStatus.FINALIZING:
                    QueueService.create_render_job(story)
                
                # Log transition
                logger.info(
                    f"Story {story.id} transitioned from {story.status} to {new_status} "
                    f"by user {request.user.id}"
                )
                
                return Response(
                    StorySerializer(story, context={'request': request}).data,
                    status=status.HTTP_200_OK
                )
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error transitioning story {story.id}: {str(e)}")
            return Response(
                {'error': 'An error occurred during transition'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def generate_preview(self, request, pk=None):
        """
        Generate preview for story
        POST /api/ai-video/stories/{id}/generate_preview/
        """
        story = self.get_object()
        serializer = GeneratePreviewSerializer(
            data=request.data,
            context={'story': story}
        )
        serializer.is_valid(raise_exception=True)
        
        try:
            # Create preview generation job
            job = QueueService.create_preview_job(
                story,
                quality=serializer.validated_data['quality'],
                include_audio=serializer.validated_data['include_audio'],
                watermark=serializer.validated_data['watermark']
            )
            
            # Update story status
            if story.status == StoryStatus.PLANNED:
                story.transition_to(StoryStatus.PREVIEWING)
            
            return Response(
                {
                    'message': 'Preview generation started',
                    'job_id': job.job_id,
                    'story': StorySerializer(story, context={'request': request}).data
                },
                status=status.HTTP_202_ACCEPTED
            )
        
        except Exception as e:
            logger.error(f"Error generating preview for story {story.id}: {str(e)}")
            return Response(
                {'error': 'Failed to start preview generation'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def render_final(self, request, pk=None):
        """
        Render final video for story
        POST /api/ai-video/stories/{id}/render_final/
        """
        story = self.get_object()
        serializer = RenderFinalVideoSerializer(
            data=request.data,
            context={'story': story}
        )
        serializer.is_valid(raise_exception=True)
        
        try:
            # Create final render job
            job = QueueService.create_render_job(
                story,
                quality=serializer.validated_data['quality'],
                include_subtitles=serializer.validated_data['include_subtitles'],
                output_format=serializer.validated_data['output_format']
            )
            
            # Update story status
            story.transition_to(StoryStatus.FINALIZING)
            
            return Response(
                {
                    'message': 'Final video rendering started',
                    'job_id': job.job_id,
                    'estimated_time': AIVideoService.estimate_render_time(story),
                    'story': StorySerializer(story, context={'request': request}).data
                },
                status=status.HTTP_202_ACCEPTED
            )
        
        except Exception as e:
            logger.error(f"Error rendering final video for story {story.id}: {str(e)}")
            return Response(
                {'error': 'Failed to start final rendering'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        """
        Lock story for planning ( )
        POST /api/ai-video/stories/{id}/lock/
        """
        story = self.get_object()
        
        if story.is_locked:
            return Response(
                {'error': 'Story is already locked'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            story.lock_story(request.user)
            
            # Transition to planned if all requirements are met
            if story.can_be_planned:
                story.transition_to(StoryStatus.PLANNED)
            
            return Response(
                {
                    'message': 'Story locked successfully',
                    'story': StorySerializer(story, context={'request': request}).data
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f"Error locking story {story.id}: {str(e)}")
            return Response(
                {'error': 'Failed to lock story'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """
        Unlock story for editing ( )
        POST /api/ai-video/stories/{id}/unlock/
        """
        story = self.get_object()
        
        if not story.is_locked:
            return Response(
                {'error': 'Story is not locked'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            story.unlock_story(request.user)
            
            return Response(
                {
                    'message': 'Story unlocked successfully',
                    'story': StorySerializer(story, context={'request': request}).data
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f"Error unlocking story {story.id}: {str(e)}")
            return Response(
                {'error': 'Failed to unlock story'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def generate_prompts(self, request, pk=None):
        """
        Generate AI prompts for all scenes
        POST /api/ai-video/stories/{id}/generate-prompts/
        """
        story = self.get_object()
        
        if not story.scenes.exists():
            return Response(
                {'error': 'Story must have scenes to generate prompts'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            generated_count = 0
            
            with transaction.atomic():
                for scene in story.scenes.all():
                    # Check if scene already has prompts
                    if not scene.prompts.exists():
                        AIVideoService._generate_scene_prompts(scene)
                        generated_count += 1
            
            return Response(
                {
                    'message': f'Generated prompts for {generated_count} scenes',
                    'generated_count': generated_count,
                    'total_scenes': story.scenes.count(),
                    'story': StorySerializer(story, context={'request': request}).data
                },
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            logger.error(f"Error generating prompts for story {story.id}: {str(e)}")
            return Response(
                {'error': 'Failed to generate prompts'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def bulk_create_scenes(self, request, pk=None):
        """
        Create 12 scenes in bulk for story
        POST /api/ai-video/stories/{id}/scenes/bulk/
        """
        story = self.get_object()
        
        if story.scenes.exists():
            return Response(
                {'error': 'Story already has scenes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Generate 12 default scenes
            scene_duration = story.duration_seconds / 12
            scenes = []
            
            with transaction.atomic():
                for i in range(12):
                    start_time = i * scene_duration
                    end_time = (i + 1) * scene_duration
                    
                    # Scene types for variety
                    if i == 0:
                        scene_type = 'intro'
                        title = f"Opening Scene"
                    elif i == 11:
                        scene_type = 'outro'
                        title = f"Closing Scene"
                    elif i in [3, 7]:
                        scene_type = 'transition'
                        title = f"Transition {i//4 + 1}"
                    else:
                        scene_type = 'main'
                        title = f"Main Scene {i}"
                    
                    scene = Scene.objects.create(
                        story=story,
                        order=i + 1,
                        title=title,
                        description=f"Auto-generated {scene_type} scene",
                        start_time=start_time,
                        end_time=end_time,
                        duration=scene_duration,
                        scene_type=scene_type
                    )
                    scenes.append(scene)
                
                # Generate prompts for all scenes
                for scene in scenes:
                    AIVideoService._generate_scene_prompts(scene)
            
            return Response(
                {
                    'message': 'Successfully created 12 scenes with prompts',
                    'scenes_created': len(scenes),
                    'story': StorySerializer(story, context={'request': request}).data
                },
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            logger.error(f"Error bulk creating scenes for story {story.id}: {str(e)}")
            return Response(
                {'error': 'Failed to create scenes'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def transitions(self, request, pk=None):
        """
        Get state transition history for story
        GET /api/ai-video/stories/{id}/transitions/
        """
        story = self.get_object()
        transitions = story.state_transitions.all()
        serializer = StoryStateTransitionSerializer(transitions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def jobs(self, request, pk=None):
        """
        Get all jobs for story
        GET /api/ai-video/stories/{id}/jobs/
        """
        story = self.get_object()
        jobs = story.jobs.all()
        
        # Filter by status if provided
        job_status = request.query_params.get('status')
        if job_status:
            jobs = jobs.filter(status=job_status)
        
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def cost_estimate(self, request, pk=None):
        """
        Get cost estimate for story
        GET /api/ai-video/stories/{id}/cost_estimate/
        """
        story = self.get_object()
        estimate = AIVideoService.calculate_cost_estimate(story)
        
        return Response({
            'estimated_cost': estimate['total'],
            'breakdown': {
                'scene_generation': estimate['scene_generation'],
                'preview': estimate['preview'],
                'final_render': estimate['final_render'],
                'storage': estimate['storage']
            },
            'currency': 'USD'
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get user's story statistics
        GET /api/ai-video/stories/statistics/
        """
        stories = self.get_queryset()
        
        stats = {
            'total_stories': stories.count(),
            'by_status': {},
            'total_duration': 0,
            'total_cost': 0,
            'average_scenes_per_story': 0,
            'completion_rate': 0
        }
        
        # Count by status
        for status_choice in StoryStatus.choices:
            status_value = status_choice[0]
            stats['by_status'][status_value] = stories.filter(
                status=status_value
            ).count()
        
        # Calculate aggregates
        aggregates = stories.aggregate(
            total_duration=Sum('duration_seconds'),
            total_cost=Sum('actual_cost'),
            avg_scenes=Avg('scenes__count')
        )
        
        stats['total_duration'] = aggregates['total_duration'] or 0
        stats['total_cost'] = float(aggregates['total_cost'] or 0)
        stats['average_scenes_per_story'] = float(aggregates['avg_scenes'] or 0)
        
        # Calculate completion rate
        total = stories.count()
        if total > 0:
            completed = stories.filter(status=StoryStatus.COMPLETED).count()
            stats['completion_rate'] = (completed / total) * 100
        
        return Response(stats)


class StoryDevelopmentViewSet(viewsets.ViewSet):
    """
       ViewSet
          
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def analyze_project(self, request):
        """
               
        POST /api/ai-video/story-development/analyze-project/
        """
        project_id = request.data.get('project_id')
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from projects.models import Project
            project = Project.objects.get(id=project_id, user=request.user)
            
            #   
            project_data = project.project_data or {}
            
            analysis = {
                'project_completeness': 0,
                'story_readiness': False,
                'missing_elements': [],
                'recommendations': []
            }
            
            #   
            required_fields = ['genre', 'tone', 'intensity', 'target_audience']
            present_fields = []
            
            for field in required_fields:
                if field in project_data and project_data[field]:
                    present_fields.append(field)
                else:
                    analysis['missing_elements'].append(field)
            
            analysis['project_completeness'] = (len(present_fields) / len(required_fields)) * 100
            analysis['story_readiness'] = analysis['project_completeness'] >= 75
            
            #   
            if not analysis['story_readiness']:
                analysis['recommendations'].append('   ')
            
            if 'key_message' not in project_data:
                analysis['recommendations'].append('        ')
            
            if 'brand_values' not in project_data:
                analysis['recommendations'].append('       ')
            
            return Response({
                'project_id': project_id,
                'analysis': analysis,
                'current_settings': project_data
            })
        
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error analyzing project: {str(e)}")
            return Response(
                {'error': 'Failed to analyze project'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_story_outline(self, request):
        """
             
        POST /api/ai-video/story-development/generate-story-outline/
        """
        project_id = request.data.get('project_id')
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from projects.models import Project
            project = Project.objects.get(id=project_id, user=request.user)
            
            #   
            development_result = StoryDevelopmentService.develop_story_from_project(project)
            
            if development_result['success']:
                return Response({
                    'message': 'Story outline generated successfully',
                    'outline': development_result
                })
            else:
                return Response(
                    {'error': development_result['error']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error generating story outline: {str(e)}")
            return Response(
                {'error': 'Failed to generate story outline'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def genre_templates(self, request):
        """
           
        GET /api/ai-video/story-development/genre-templates/
        """
        return Response({
            'genre_templates': StoryDevelopmentService.GENRE_TEMPLATES,
            'tone_styles': StoryDevelopmentService.TONE_STYLES,
            'intensity_levels': StoryDevelopmentService.INTENSITY_LEVELS
        })
    
    @action(detail=False, methods=['get'])
    def style_guide(self, request):
        """
           
        GET /api/ai-video/story-development/style-guide/
        """
        tone = request.query_params.get('tone', 'professional')
        intensity = int(request.query_params.get('intensity', 5))
        
        tone_style = StoryDevelopmentService.TONE_STYLES.get(
            tone, StoryDevelopmentService.TONE_STYLES['professional']
        )
        intensity_guide = StoryDevelopmentService.INTENSITY_LEVELS.get(
            intensity, StoryDevelopmentService.INTENSITY_LEVELS[5]
        )
        
        return Response({
            'tone': tone,
            'intensity': intensity,
            'tone_style': tone_style,
            'intensity_guide': intensity_guide,
            'combined_guide': {
                'visual_approach': f"{tone_style['visual_style']} with {intensity_guide['motion']} motion",
                'lighting_setup': f"{tone_style['lighting']} with {intensity_guide['effects']} effects",
                'editing_pace': f"{intensity_guide['pace']} pacing with {tone_style['composition']}",
                'color_scheme': tone_style['color_palette']
            }
        })


class SceneViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Scene CRUD operations
    """
    serializer_class = SceneSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter] + ([DjangoFilterBackend] if HAS_DJANGO_FILTERS else [])
    filterset_fields = ['story', 'scene_type'] if HAS_DJANGO_FILTERS else []
    ordering_fields = ['order', 'created_at']
    ordering = ['order']
    
    def get_queryset(self):
        """Filter scenes by story and user"""
        queryset = Scene.objects.filter(story__user=self.request.user)
        
        # Prefetch related data
        queryset = queryset.prefetch_related('prompts').select_related('story')
        
        # Filter by story if provided
        story_id = self.request.query_params.get('story_id')
        if story_id:
            queryset = queryset.filter(story_id=story_id)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Bulk create scenes for a story
        POST /api/ai-video/scenes/bulk_create/
        """
        story_id = request.data.get('story_id')
        if not story_id:
            return Response(
                {'error': 'story_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            story = Story.objects.get(id=story_id, user=request.user)
        except Story.DoesNotExist:
            return Response(
                {'error': 'Story not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = BulkSceneCreateSerializer(
            data=request.data,
            context={'story': story, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        scenes = serializer.save()
        return Response(
            SceneSerializer(scenes, many=True, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """
        Generate content for a specific scene
        POST /api/ai-video/scenes/{id}/generate/
        """
        scene = self.get_object()
        
        # Check if scene has active prompts
        active_prompt = scene.prompts.filter(is_selected=True, is_active=True).first()
        if not active_prompt:
            return Response(
                {'error': 'No active prompt selected for this scene'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create scene generation job
            job = QueueService.create_scene_generation_job(scene, active_prompt)
            
            return Response(
                {
                    'message': 'Scene generation started',
                    'job_id': job.job_id,
                    'scene': SceneSerializer(scene, context={'request': request}).data
                },
                status=status.HTTP_202_ACCEPTED
            )
        
        except Exception as e:
            logger.error(f"Error generating scene {scene.id}: {str(e)}")
            return Response(
                {'error': 'Failed to start scene generation'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """
        Reorder scenes within a story
        POST /api/ai-video/scenes/{id}/reorder/
        """
        scene = self.get_object()
        new_order = request.data.get('new_order')
        
        if new_order is None:
            return Response(
                {'error': 'new_order is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Get all scenes in the story
                scenes = list(scene.story.scenes.order_by('order'))
                current_index = scenes.index(scene)
                
                # Remove from current position and insert at new position
                scenes.pop(current_index)
                scenes.insert(new_order - 1, scene)
                
                # Update order for all scenes
                for idx, s in enumerate(scenes, 1):
                    s.order = idx
                    s.save(update_fields=['order'])
                
                return Response(
                    SceneSerializer(scene, context={'request': request}).data,
                    status=status.HTTP_200_OK
                )
        
        except Exception as e:
            logger.error(f"Error reordering scene {scene.id}: {str(e)}")
            return Response(
                {'error': 'Failed to reorder scene'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ScenePromptViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ScenePrompt CRUD operations
    """
    serializer_class = ScenePromptSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter] + ([DjangoFilterBackend] if HAS_DJANGO_FILTERS else [])
    filterset_fields = ['scene', 'prompt_type', 'is_active', 'is_selected'] if HAS_DJANGO_FILTERS else []
    ordering_fields = ['version', 'created_at']
    ordering = ['-version']
    
    def get_queryset(self):
        """Filter prompts by user's scenes"""
        queryset = ScenePrompt.objects.filter(scene__story__user=self.request.user)
        
        # Prefetch related data
        queryset = queryset.select_related('scene', 'scene__story')
        
        # Filter by scene if provided
        scene_id = self.request.query_params.get('scene_id')
        if scene_id:
            queryset = queryset.filter(scene_id=scene_id)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def select(self, request, pk=None):
        """
        Select this prompt as the active prompt for its scene
        POST /api/ai-video/prompts/{id}/select/
        """
        prompt = self.get_object()
        
        with transaction.atomic():
            # Deselect all other prompts for this scene
            ScenePrompt.objects.filter(
                scene=prompt.scene
            ).update(is_selected=False)
            
            # Select this prompt
            prompt.is_selected = True
            prompt.save()
        
        return Response(
            ScenePromptSerializer(prompt).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """
        Test prompt generation without saving results
        POST /api/ai-video/prompts/{id}/test/
        """
        prompt = self.get_object()
        
        try:
            # Run test generation
            result = AIVideoService.test_prompt(prompt)
            
            return Response({
                'success': result['success'],
                'preview_url': result.get('preview_url'),
                'generation_time': result.get('generation_time'),
                'metadata': result.get('metadata')
            })
        
        except Exception as e:
            logger.error(f"Error testing prompt {prompt.id}: {str(e)}")
            return Response(
                {'error': 'Failed to test prompt'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Job monitoring and management
    """
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter] + ([DjangoFilterBackend] if HAS_DJANGO_FILTERS else [])
    filterset_fields = ['status', 'job_type', 'queue_name'] if HAS_DJANGO_FILTERS else []
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter jobs by user's stories"""
        queryset = Job.objects.filter(
            Q(story__user=self.request.user) | 
            Q(scene__story__user=self.request.user)
        )
        
        # Prefetch related data
        queryset = queryset.select_related('story', 'scene')
        
        # Filter by story if provided
        story_id = self.request.query_params.get('story_id')
        if story_id:
            queryset = queryset.filter(story_id=story_id)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """
        Retry a failed job
        POST /api/ai-video/jobs/{id}/retry/
        """
        job = self.get_object()
        serializer = JobRetrySerializer(
            data=request.data,
            context={'job': job}
        )
        serializer.is_valid(raise_exception=True)
        
        try:
            # Update priority if provided
            if 'priority' in serializer.validated_data:
                job.priority = serializer.validated_data['priority']
            
            # Retry the job
            job.retry()
            
            # Re-queue the job
            QueueService.retry_job(
                job,
                delay=serializer.validated_data.get('delay_seconds', 0)
            )
            
            return Response(
                JobSerializer(job).data,
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f"Error retrying job {job.id}: {str(e)}")
            return Response(
                {'error': 'Failed to retry job'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a pending or running job
        POST /api/ai-video/jobs/{id}/cancel/
        """
        job = self.get_object()
        
        if job.status not in [JobStatus.PENDING, JobStatus.QUEUED, JobStatus.PROCESSING]:
            return Response(
                {'error': f'Cannot cancel job with status {job.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Cancel job in queue
            QueueService.cancel_job(job)
            
            # Update job status
            job.status = JobStatus.CANCELLED
            job.save()
            
            return Response(
                JobSerializer(job).data,
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f"Error cancelling job {job.id}: {str(e)}")
            return Response(
                {'error': 'Failed to cancel job'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get job statistics
        GET /api/ai-video/jobs/statistics/
        """
        jobs = self.get_queryset()
        
        stats = {
            'total_jobs': jobs.count(),
            'by_status': {},
            'by_type': {},
            'average_duration': 0,
            'success_rate': 0,
            'retry_rate': 0
        }
        
        # Count by status
        for status_choice in JobStatus.choices:
            status_value = status_choice[0]
            stats['by_status'][status_value] = jobs.filter(
                status=status_value
            ).count()
        
        # Count by type
        job_types = jobs.values_list('job_type', flat=True).distinct()
        for job_type in job_types:
            stats['by_type'][job_type] = jobs.filter(job_type=job_type).count()
        
        # Calculate success rate
        total = jobs.count()
        if total > 0:
            completed = jobs.filter(status=JobStatus.COMPLETED).count()
            stats['success_rate'] = (completed / total) * 100
            
            retried = jobs.filter(attempts__gt=1).count()
            stats['retry_rate'] = (retried / total) * 100
        
        # Calculate average duration for completed jobs
        completed_jobs = jobs.filter(
            status=JobStatus.COMPLETED,
            started_at__isnull=False,
            completed_at__isnull=False
        )
        
        if completed_jobs.exists():
            total_duration = sum(
                (job.completed_at - job.started_at).total_seconds()
                for job in completed_jobs
            )
            stats['average_duration'] = total_duration / completed_jobs.count()
        
        return Response(stats)