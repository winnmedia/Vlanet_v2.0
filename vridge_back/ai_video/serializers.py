"""
Serializers for AI Video Generation API
Following REST best practices with nested serialization support
"""
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from .models import (
    Story, Scene, ScenePrompt, Job,
    StoryStatus, JobStatus, AIProvider,
    StoryStateTransition, AIProviderConfig
)


class ScenePromptSerializer(serializers.ModelSerializer):
    """Serializer for scene prompts"""
    
    class Meta:
        model = ScenePrompt
        fields = [
            'id', 'prompt_type', 'system_prompt', 'user_prompt',
            'negative_prompt', 'parameters', 'version', 'is_active',
            'is_selected', 'generation_count', 'success_rate',
            'average_quality_score', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'generation_count', 'success_rate', 'average_quality_score']
    
    def validate_parameters(self, value):
        """Validate prompt parameters based on prompt type"""
        prompt_type = self.initial_data.get('prompt_type', 'image')
        
        required_params = {
            'image': ['width', 'height', 'steps'],
            'video': ['width', 'height', 'fps', 'duration'],
            'audio': ['duration', 'sample_rate'],
            'text': ['max_tokens', 'temperature'],
            'motion': ['interpolation_frames', 'motion_strength']
        }
        
        if prompt_type in required_params:
            missing = [p for p in required_params[prompt_type] if p not in value]
            if missing:
                raise serializers.ValidationError(
                    f"Missing required parameters for {prompt_type}: {', '.join(missing)}"
                )
        
        return value


class SceneSerializer(serializers.ModelSerializer):
    """Serializer for scenes with nested prompts"""
    prompts = ScenePromptSerializer(many=True, read_only=True)
    selected_prompt = serializers.SerializerMethodField()
    
    class Meta:
        model = Scene
        fields = [
            'id', 'order', 'title', 'description', 'start_time',
            'end_time', 'duration', 'scene_type', 'preview_image_url',
            'video_segment_url', 'generation_attempts', 'last_generation_at',
            'generation_metadata', 'prompts', 'selected_prompt',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'preview_image_url', 'video_segment_url',
            'generation_attempts', 'last_generation_at'
        ]
    
    def get_selected_prompt(self, obj):
        """Get the currently selected prompt for the scene"""
        selected = obj.prompts.filter(is_selected=True, is_active=True).first()
        if selected:
            return ScenePromptSerializer(selected).data
        return None
    
    def validate(self, data):
        """Validate scene timing"""
        if 'end_time' in data and 'start_time' in data:
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError("End time must be after start time")
        return data


class StorySerializer(serializers.ModelSerializer):
    """Main serializer for stories with nested scenes"""
    scenes = SceneSerializer(many=True, read_only=True)
    scene_count = serializers.IntegerField(source='scenes.count', read_only=True)
    can_transition_to = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Story
        fields = [
            'id', 'project', 'user', 'title', 'description', 'status',
            'status_display', 'duration_seconds', 'fps', 'resolution',
            'style_preset', 'ai_provider', 'preview_url', 'final_video_url',
            'thumbnail_url', 'metadata', 'generation_config',
            'estimated_cost', 'actual_cost', 'scenes', 'scene_count',
            'can_transition_to', 'total_duration',
            'planning_started_at', 'planning_completed_at',
            'preview_started_at', 'preview_completed_at',
            'rendering_started_at', 'rendering_completed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'preview_url', 'final_video_url', 'thumbnail_url',
            'actual_cost', 'planning_started_at', 'planning_completed_at',
            'preview_started_at', 'preview_completed_at',
            'rendering_started_at', 'rendering_completed_at'
        ]
    
    def get_can_transition_to(self, obj):
        """Get available state transitions"""
        transitions = {
            StoryStatus.DRAFT: [StoryStatus.PLANNING, StoryStatus.ARCHIVED],
            StoryStatus.PLANNING: [StoryStatus.PLANNED, StoryStatus.DRAFT, StoryStatus.FAILED],
            StoryStatus.PLANNED: [StoryStatus.PREVIEWING, StoryStatus.PLANNING, StoryStatus.ARCHIVED],
            StoryStatus.PREVIEWING: [StoryStatus.PREVIEW_READY, StoryStatus.PLANNED, StoryStatus.FAILED],
            StoryStatus.PREVIEW_READY: [StoryStatus.FINALIZING, StoryStatus.PREVIEWING, StoryStatus.ARCHIVED],
            StoryStatus.FINALIZING: [StoryStatus.COMPLETED, StoryStatus.FAILED],
            StoryStatus.COMPLETED: [StoryStatus.ARCHIVED],
            StoryStatus.FAILED: [StoryStatus.DRAFT, StoryStatus.PLANNING],
            StoryStatus.ARCHIVED: [StoryStatus.DRAFT]
        }
        return transitions.get(obj.status, [])
    
    def get_total_duration(self, obj):
        """Calculate total duration from all scenes"""
        return sum(scene.duration for scene in obj.scenes.all())
    
    def create(self, validated_data):
        """Create story with initial setup"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class StoryTransitionSerializer(serializers.Serializer):
    """Serializer for story state transitions"""
    new_status = serializers.ChoiceField(choices=StoryStatus.choices)
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate_new_status(self, value):
        """Validate if transition is allowed"""
        story = self.context.get('story')
        if story and not story.can_transition_to(value):
            raise serializers.ValidationError(
                f"Cannot transition from {story.status} to {value}"
            )
        return value


class JobSerializer(serializers.ModelSerializer):
    """Serializer for background jobs"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    job_type_display = serializers.CharField(source='get_job_type_display', read_only=True)
    can_retry = serializers.BooleanField(read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'job_id', 'queue_name', 'story', 'scene', 'job_type',
            'job_type_display', 'status', 'status_display', 'payload',
            'result', 'priority', 'attempts', 'max_attempts', 'can_retry',
            'scheduled_at', 'started_at', 'completed_at', 'failed_at',
            'duration', 'error_message', 'error_stack', 'worker_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'job_id', 'result', 'attempts', 'started_at',
            'completed_at', 'failed_at', 'error_message', 'error_stack',
            'worker_id'
        ]
    
    def get_duration(self, obj):
        """Calculate job execution duration"""
        if obj.started_at and (obj.completed_at or obj.failed_at):
            end_time = obj.completed_at or obj.failed_at
            return (end_time - obj.started_at).total_seconds()
        return None


class CreateSceneSerializer(serializers.ModelSerializer):
    """Serializer for creating scenes with prompts"""
    prompts = ScenePromptSerializer(many=True, required=False)
    
    class Meta:
        model = Scene
        fields = [
            'order', 'title', 'description', 'start_time', 'end_time',
            'duration', 'scene_type', 'prompts'
        ]
    
    def create(self, validated_data):
        """Create scene with nested prompts"""
        prompts_data = validated_data.pop('prompts', [])
        
        with transaction.atomic():
            scene = Scene.objects.create(**validated_data)
            
            for prompt_data in prompts_data:
                ScenePrompt.objects.create(scene=scene, **prompt_data)
            
            return scene


class BulkSceneCreateSerializer(serializers.Serializer):
    """Serializer for bulk scene creation"""
    scenes = CreateSceneSerializer(many=True)
    
    def create(self, validated_data):
        """Create multiple scenes atomically"""
        story = self.context.get('story')
        scenes_data = validated_data.get('scenes', [])
        
        with transaction.atomic():
            created_scenes = []
            for scene_data in scenes_data:
                scene_data['story'] = story
                serializer = CreateSceneSerializer(data=scene_data)
                serializer.is_valid(raise_exception=True)
                created_scenes.append(serializer.save(story=story))
            
            return created_scenes


class StoryStateTransitionSerializer(serializers.ModelSerializer):
    """Serializer for state transition audit log"""
    from_status_display = serializers.CharField(source='get_from_status_display', read_only=True)
    to_status_display = serializers.CharField(source='get_to_status_display', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = StoryStateTransition
        fields = [
            'id', 'story', 'from_status', 'from_status_display',
            'to_status', 'to_status_display', 'user', 'user_email',
            'reason', 'metadata', 'created_at'
        ]
        read_only_fields = '__all__'


class AIProviderConfigSerializer(serializers.ModelSerializer):
    """Serializer for AI provider configuration"""
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    
    class Meta:
        model = AIProviderConfig
        fields = [
            'provider', 'provider_display', 'is_active', 'api_endpoint',
            'rate_limit_per_minute', 'rate_limit_per_hour',
            'cost_per_image', 'cost_per_second_video', 'settings',
            'total_requests', 'total_cost', 'last_used_at'
        ]
        read_only_fields = ['total_requests', 'total_cost', 'last_used_at']
    
    def to_representation(self, instance):
        """Remove sensitive API key from response"""
        data = super().to_representation(instance)
        # Never expose API key in responses
        data.pop('api_key', None)
        return data


class GeneratePreviewSerializer(serializers.Serializer):
    """Serializer for preview generation request"""
    quality = serializers.ChoiceField(
        choices=['low', 'medium', 'high'],
        default='medium'
    )
    include_audio = serializers.BooleanField(default=False)
    watermark = serializers.BooleanField(default=True)
    
    def validate(self, data):
        """Validate preview generation request"""
        story = self.context.get('story')
        if story.status not in [StoryStatus.PLANNED, StoryStatus.PREVIEWING]:
            raise serializers.ValidationError(
                "Story must be in PLANNED or PREVIEWING status to generate preview"
            )
        
        if not story.scenes.exists():
            raise serializers.ValidationError(
                "Story must have at least one scene to generate preview"
            )
        
        return data


class RenderFinalVideoSerializer(serializers.Serializer):
    """Serializer for final video rendering request"""
    quality = serializers.ChoiceField(
        choices=['standard', 'high', 'ultra'],
        default='high'
    )
    include_subtitles = serializers.BooleanField(default=False)
    output_format = serializers.ChoiceField(
        choices=['mp4', 'webm', 'mov'],
        default='mp4'
    )
    
    def validate(self, data):
        """Validate final render request"""
        story = self.context.get('story')
        if story.status != StoryStatus.PREVIEW_READY:
            raise serializers.ValidationError(
                "Story must be in PREVIEW_READY status to render final video"
            )
        
        if not story.preview_url:
            raise serializers.ValidationError(
                "Preview must be generated before final rendering"
            )
        
        return data


class JobRetrySerializer(serializers.Serializer):
    """Serializer for job retry request"""
    priority = serializers.IntegerField(required=False, min_value=0, max_value=10)
    delay_seconds = serializers.IntegerField(required=False, min_value=0, max_value=3600)
    
    def validate(self, data):
        """Validate retry request"""
        job = self.context.get('job')
        if not job.can_retry():
            raise serializers.ValidationError(
                f"Job cannot be retried. Status: {job.status}, "
                f"Attempts: {job.attempts}/{job.max_attempts}"
            )
        return data