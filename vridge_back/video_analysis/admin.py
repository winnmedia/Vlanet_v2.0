"""
AI    
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

from .models import VideoAnalysisResult, AIFeedbackItem, AIAnalysisSettings


@admin.register(AIAnalysisSettings)
class AIAnalysisSettingsAdmin(admin.ModelAdmin):
    """AI   """
    
    fieldsets = (
        (' ', {
            'fields': ('is_enabled', 'ai_server_url', 'api_key')
        }),
        (' ', {
            'fields': (
                'analyze_composition', 
                'analyze_lighting', 
                'analyze_audio', 
                'analyze_stability',
                'analyze_color', 
                'analyze_motion'
            )
        }),
        (' ', {
            'fields': ('max_video_duration', 'analysis_timeout')
        }),
        (' ', {
            'fields': ('updated_at', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('updated_at', 'updated_by')
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        #    
        return not AIAnalysisSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


class AIFeedbackItemInline(admin.TabularInline):
    """AI   """
    model = AIFeedbackItem
    extra = 0
    readonly_fields = ('created_at',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  #  
            return self.readonly_fields + ('feedback_type', 'score', 'message', 'timestamp', 'confidence')
        return self.readonly_fields


@admin.register(VideoAnalysisResult)
class VideoAnalysisResultAdmin(admin.ModelAdmin):
    """   """
    
    list_display = [
        'id', 
        'feedback_link', 
        'status_badge', 
        'overall_score_display',
        'ai_model_version',
        'processing_time_display',
        'created_at'
    ]
    
    list_filter = [
        'status', 
        'ai_model_version', 
        'created_at'
    ]
    
    search_fields = [
        'feedback__title',
        'feedback__user__username',
        'ai_model_version'
    ]
    
    readonly_fields = [
        'feedback',
        'created_at',
        'updated_at',
        'analysis_data_display',
        'error_display'
    ]
    
    fieldsets = (
        (' ', {
            'fields': ('feedback', 'status', 'overall_score')
        }),
        ('AI ', {
            'fields': ('ai_server_url', 'ai_model_version', 'processing_time')
        }),
        (' ', {
            'fields': ('analysis_data_display',),
            'classes': ('collapse',)
        }),
        (' ', {
            'fields': ('error_display',),
            'classes': ('collapse',)
        }),
        (' ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [AIFeedbackItemInline]
    
    def feedback_link(self, obj):
        """ """
        if obj.feedback:
            url = reverse('admin:feedbacks_feedback_change', args=[obj.feedback.id])
            return format_html('<a href="{}">{}</a>', url, obj.feedback.title)
        return '-'
    feedback_link.short_description = ''
    
    def status_badge(self, obj):
        """ """
        colors = {
            'pending': '#ffc107',      # 
            'processing': '#007bff',   #   
            'completed': '#28a745',    # 
            'failed': '#dc3545'        # 
        }
        
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = ''
    
    def overall_score_display(self, obj):
        """  """
        if obj.overall_score is not None:
            if obj.overall_score >= 8:
                color = '#28a745'  # 
            elif obj.overall_score >= 6:
                color = '#ffc107'  # 
            else:
                color = '#dc3545'  # 
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1f}/10</span>',
                color,
                obj.overall_score
            )
        return '-'
    overall_score_display.short_description = ' '
    
    def processing_time_display(self, obj):
        """  """
        if obj.processing_time:
            return f"{obj.processing_time:.1f}"
        return '-'
    processing_time_display.short_description = ' '
    
    def analysis_data_display(self, obj):
        """  """
        if obj.analysis_data:
            formatted_json = json.dumps(obj.analysis_data, indent=2, ensure_ascii=False)
            return format_html('<pre style="font-size: 12px;">{}</pre>', formatted_json)
        return '-'
    analysis_data_display.short_description = ' '
    
    def error_display(self, obj):
        """  """
        if obj.error_message:
            return format_html(
                '<div style="background-color: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24;">{}</div>',
                obj.error_message
            )
        return '-'
    error_display.short_description = ' '
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('feedback', 'feedback__user')
    
    actions = ['retry_failed_analyses', 'export_analysis_data']
    
    def retry_failed_analyses(self, request, queryset):
        """  """
        from .tasks import analyze_video_task
        
        failed_analyses = queryset.filter(status='failed')
        count = 0
        
        for analysis in failed_analyses:
            if analysis.feedback.file:
                analysis.status = 'processing'
                analysis.error_message = ''
                analysis.save()
                
                #   
                analyze_video_task.delay(analysis.id, analysis.feedback.file.path)
                count += 1
        
        self.message_user(request, f'{count}   .')
    retry_failed_analyses.short_description = '  '
    
    def export_analysis_data(self, request, queryset):
        """  """
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="analysis_results.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', ' ', '', '', ' ', 
            'AI ', ' ', ' '
        ])
        
        for analysis in queryset:
            writer.writerow([
                analysis.id,
                analysis.feedback.title,
                analysis.feedback.user.username,
                analysis.get_status_display(),
                analysis.overall_score or '',
                analysis.ai_model_version,
                analysis.processing_time or '',
                analysis.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    export_analysis_data.short_description = '  CSV '


@admin.register(AIFeedbackItem)
class AIFeedbackItemAdmin(admin.ModelAdmin):
    """AI   """
    
    list_display = [
        'id',
        'analysis_result_link',
        'feedback_type_badge',
        'score_display',
        'message_preview',
        'timestamp_display',
        'confidence_display'
    ]
    
    list_filter = [
        'feedback_type',
        'analysis_result__status',
        'created_at'
    ]
    
    search_fields = [
        'message',
        'analysis_result__feedback__title'
    ]
    
    readonly_fields = ['created_at']
    
    def analysis_result_link(self, obj):
        """  """
        url = reverse('admin:video_analysis_videoanalysisresult_change', args=[obj.analysis_result.id])
        return format_html('<a href="{}"> #{}</a>', url, obj.analysis_result.id)
    analysis_result_link.short_description = ' '
    
    def feedback_type_badge(self, obj):
        """  """
        colors = {
            'composition': '#007bff',
            'lighting': '#ffc107', 
            'audio': '#28a745',
            'stability': '#17a2b8',
            'color': '#e83e8c',
            'motion': '#6f42c1',
            'editing': '#fd7e14',
            'storytelling': '#20c997'
        }
        
        color = colors.get(obj.feedback_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_feedback_type_display()
        )
    feedback_type_badge.short_description = ''
    
    def score_display(self, obj):
        """ """
        if obj.score >= 8:
            color = '#28a745'
        elif obj.score >= 6:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}</span>',
            color,
            obj.score
        )
    score_display.short_description = ''
    
    def message_preview(self, obj):
        """ """
        if len(obj.message) > 50:
            return obj.message[:50] + '...'
        return obj.message
    message_preview.short_description = ''
    
    def timestamp_display(self, obj):
        """ """
        minutes = int(obj.timestamp // 60)
        seconds = int(obj.timestamp % 60)
        return f"{minutes:02d}:{seconds:02d}"
    timestamp_display.short_description = ''
    
    def confidence_display(self, obj):
        """ """
        percentage = obj.confidence * 100
        if percentage >= 90:
            color = '#28a745'
        elif percentage >= 70:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        return format_html(
            '<span style="color: {};">{:.0f}%</span>',
            color,
            percentage
        )
    confidence_display.short_description = ''