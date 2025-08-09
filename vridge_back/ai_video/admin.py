"""
Django Admin configuration for AI Video Generation models
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Story, Scene, ScenePrompt, Job,
    StoryStateTransition, AIProviderConfig
)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    """Admin interface for Story model"""
    list_display = [
        'title', 'user', 'project', 'status_badge', 
        'duration_seconds', 'ai_provider', 'estimated_cost',
        'actual_cost', 'created'
    ]
    list_filter = [
        'status', 'ai_provider', 'created', 'updated'
    ]
    search_fields = ['title', 'description', 'user__email', 'project__name']
    readonly_fields = [
        'id', 'preview_url_link', 'final_video_url_link',
        'thumbnail_url_link', 'created', 'updated',
        'planning_started_at', 'planning_completed_at',
        'preview_started_at', 'preview_completed_at',
        'rendering_started_at', 'rendering_completed_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'project', 'user', 'title', 'description', 'status')
        }),
        ('Video Configuration', {
            'fields': ('duration_seconds', 'fps', 'resolution', 'style_preset', 'ai_provider')
        }),
        ('Generated Content', {
            'fields': (
                'preview_url_link', 'final_video_url_link', 
                'thumbnail_url_link'
            )
        }),
        ('Cost Tracking', {
            'fields': ('estimated_cost', 'actual_cost')
        }),
        ('Timeline', {
            'fields': (
                'planning_started_at', 'planning_completed_at',
                'preview_started_at', 'preview_completed_at',
                'rendering_started_at', 'rendering_completed_at',
                'created', 'updated'
            ),
            'classes': ('collapse',)
        }),
        ('Advanced', {
            'fields': ('metadata', 'generation_config'),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'draft': 'gray',
            'planning': 'blue',
            'planned': 'cyan',
            'previewing': 'yellow',
            'rendering': 'orange',
            'completed': 'green',
            'failed': 'red',
            'archived': 'purple'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def preview_url_link(self, obj):
        """Make preview URL clickable"""
        if obj.preview_url:
            return format_html('<a href="{}" target="_blank">View Preview</a>', obj.preview_url)
        return '-'
    preview_url_link.short_description = 'Preview'
    
    def final_video_url_link(self, obj):
        """Make final video URL clickable"""
        if obj.final_video_url:
            return format_html('<a href="{}" target="_blank">View Video</a>', obj.final_video_url)
        return '-'
    final_video_url_link.short_description = 'Final Video'
    
    def thumbnail_url_link(self, obj):
        """Display thumbnail image"""
        if obj.thumbnail_url:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 150px;" />',
                obj.thumbnail_url
            )
        return '-'
    thumbnail_url_link.short_description = 'Thumbnail'


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    """Admin interface for Scene model"""
    list_display = [
        'title', 'story', 'order', 'scene_type',
        'duration', 'has_preview', 'has_video',
        'generation_attempts', 'created'
    ]
    list_filter = ['scene_type', 'created']
    search_fields = ['title', 'description', 'story__title']
    ordering = ['story', 'order']
    readonly_fields = [
        'id', 'preview_image_link', 'video_segment_link',
        'generation_attempts', 'last_generation_at',
        'created', 'updated'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'story', 'order', 'title', 'description', 'scene_type')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'duration')
        }),
        ('Generated Content', {
            'fields': ('preview_image_link', 'video_segment_link')
        }),
        ('Generation Stats', {
            'fields': (
                'generation_attempts', 'last_generation_at',
                'generation_metadata'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        })
    )
    
    def has_preview(self, obj):
        """Check if scene has preview"""
        return bool(obj.preview_image_url)
    has_preview.boolean = True
    has_preview.short_description = 'Has Preview'
    
    def has_video(self, obj):
        """Check if scene has video"""
        return bool(obj.video_segment_url)
    has_video.boolean = True
    has_video.short_description = 'Has Video'
    
    def preview_image_link(self, obj):
        """Display preview image"""
        if obj.preview_image_url:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px;" />',
                obj.preview_image_url
            )
        return '-'
    preview_image_link.short_description = 'Preview Image'
    
    def video_segment_link(self, obj):
        """Make video segment URL clickable"""
        if obj.video_segment_url:
            return format_html('<a href="{}" target="_blank">View Video</a>', obj.video_segment_url)
        return '-'
    video_segment_link.short_description = 'Video Segment'


@admin.register(ScenePrompt)
class ScenePromptAdmin(admin.ModelAdmin):
    """Admin interface for ScenePrompt model"""
    list_display = [
        'scene', 'prompt_type', 'version', 'is_active',
        'is_selected', 'generation_count', 'success_rate',
        'average_quality_score', 'created'
    ]
    list_filter = ['prompt_type', 'is_active', 'is_selected', 'created']
    search_fields = ['scene__title', 'user_prompt', 'system_prompt']
    readonly_fields = [
        'id', 'generation_count', 'success_rate',
        'average_quality_score', 'created', 'updated'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'scene', 'prompt_type', 'version')
        }),
        ('Prompt Content', {
            'fields': ('system_prompt', 'user_prompt', 'negative_prompt')
        }),
        ('Configuration', {
            'fields': ('parameters', 'is_active', 'is_selected')
        }),
        ('Performance Metrics', {
            'fields': (
                'generation_count', 'success_rate',
                'average_quality_score'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        })
    )


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Admin interface for Job model"""
    list_display = [
        'job_id', 'job_type', 'status_badge', 'story',
        'priority', 'attempts', 'worker_id',
        'duration_display', 'created'
    ]
    list_filter = ['status', 'job_type', 'queue_name', 'created']
    search_fields = ['job_id', 'story__title', 'error_message']
    readonly_fields = [
        'id', 'job_id', 'attempts', 'started_at',
        'completed_at', 'failed_at', 'created', 'updated'
    ]
    
    fieldsets = (
        ('Job Information', {
            'fields': (
                'id', 'job_id', 'queue_name', 'job_type',
                'status', 'priority'
            )
        }),
        ('Related Objects', {
            'fields': ('story', 'scene')
        }),
        ('Execution', {
            'fields': (
                'attempts', 'max_attempts', 'worker_id',
                'scheduled_at', 'started_at', 'completed_at', 'failed_at'
            )
        }),
        ('Data', {
            'fields': ('payload', 'result'),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('error_message', 'error_stack'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'pending': 'gray',
            'queued': 'blue',
            'processing': 'yellow',
            'completed': 'green',
            'failed': 'red',
            'cancelled': 'orange',
            'retrying': 'purple'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def duration_display(self, obj):
        """Display job duration"""
        if obj.started_at and (obj.completed_at or obj.failed_at):
            end_time = obj.completed_at or obj.failed_at
            duration = (end_time - obj.started_at).total_seconds()
            return f"{duration:.2f}s"
        return '-'
    duration_display.short_description = 'Duration'
    
    actions = ['retry_failed_jobs', 'cancel_pending_jobs']
    
    def retry_failed_jobs(self, request, queryset):
        """Admin action to retry failed jobs"""
        from .services import QueueService
        
        failed_jobs = queryset.filter(status='failed')
        retried_count = 0
        
        for job in failed_jobs:
            if job.can_retry():
                QueueService.retry_job(job)
                retried_count += 1
        
        self.message_user(
            request,
            f'Successfully retried {retried_count} failed jobs.'
        )
    retry_failed_jobs.short_description = 'Retry selected failed jobs'
    
    def cancel_pending_jobs(self, request, queryset):
        """Admin action to cancel pending jobs"""
        from .services import QueueService
        
        pending_jobs = queryset.filter(status__in=['pending', 'queued'])
        cancelled_count = 0
        
        for job in pending_jobs:
            QueueService.cancel_job(job)
            job.status = 'cancelled'
            job.save()
            cancelled_count += 1
        
        self.message_user(
            request,
            f'Successfully cancelled {cancelled_count} pending jobs.'
        )
    cancel_pending_jobs.short_description = 'Cancel selected pending jobs'


@admin.register(StoryStateTransition)
class StoryStateTransitionAdmin(admin.ModelAdmin):
    """Admin interface for StoryStateTransition model"""
    list_display = [
        'story', 'from_status', 'to_status', 'user',
        'created'
    ]
    list_filter = ['from_status', 'to_status', 'created']
    search_fields = ['story__title', 'user__email', 'reason']
    readonly_fields = ['story', 'from_status', 'to_status', 'user', 'created']
    
    fieldsets = (
        ('Transition Information', {
            'fields': ('story', 'from_status', 'to_status', 'user')
        }),
        ('Details', {
            'fields': ('reason', 'metadata')
        }),
        ('Timestamp', {
            'fields': ('created',)
        })
    )


@admin.register(AIProviderConfig)
class AIProviderConfigAdmin(admin.ModelAdmin):
    """Admin interface for AIProviderConfig model"""
    list_display = [
        'provider', 'is_active', 'rate_limit_per_minute',
        'rate_limit_per_hour', 'cost_per_image',
        'cost_per_second_video', 'total_requests',
        'total_cost', 'last_used_at'
    ]
    list_filter = ['provider', 'is_active']
    readonly_fields = ['total_requests', 'total_cost', 'last_used_at']
    
    fieldsets = (
        ('Provider Information', {
            'fields': ('provider', 'is_active')
        }),
        ('API Configuration', {
            'fields': ('api_key', 'api_endpoint'),
            'description': 'API key will be encrypted in production'
        }),
        ('Rate Limiting', {
            'fields': ('rate_limit_per_minute', 'rate_limit_per_hour')
        }),
        ('Cost Configuration', {
            'fields': ('cost_per_image', 'cost_per_second_video')
        }),
        ('Settings', {
            'fields': ('settings',),
            'classes': ('collapse',)
        }),
        ('Usage Statistics', {
            'fields': ('total_requests', 'total_cost', 'last_used_at'),
            'classes': ('collapse',)
        })
    )