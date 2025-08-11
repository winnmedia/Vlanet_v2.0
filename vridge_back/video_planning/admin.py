from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
from .models import VideoPlanning, VideoPlanningImage


class VideoPlanningImageInline(admin.TabularInline):
    model = VideoPlanningImage
    extra = 0
    fields = ['frame_number', 'image_preview', 'prompt_used', 'created_at']
    readonly_fields = ['frame_number', 'image_preview', 'prompt_used', 'created_at']
    
    def image_preview(self, obj):
        if obj.image_url:
            if obj.image_url.startswith('data:image'):
                return format_html('<img src="{}" style="max-width: 200px; max-height: 150px;" />', obj.image_url)
            else:
                return format_html('<a href="{}" target="_blank"><img src="{}" style="max-width: 200px; max-height: 150px;" /></a>', 
                                 obj.image_url, obj.image_url)
        return '-'
    image_preview.short_description = ' '


@admin.register(VideoPlanning)
class VideoPlanningAdmin(admin.ModelAdmin):
    list_display = ['id', 'title_display', 'user_display', 'planning_options_display', 
                   'progress_display', 'image_count', 'created_at_display']
    list_filter = ['is_completed', 'current_step', 'created_at', 'user']
    search_fields = ['title', 'planning_text', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'formatted_planning_text', 
                      'story_preview', 'scene_preview', 'storyboard_preview']
    inlines = [VideoPlanningImageInline]
    date_hierarchy = 'created_at'
    list_per_page = 20
    actions = ['mark_as_completed', 'export_as_json']
    
    fieldsets = (
        (' ', {
            'fields': ('user', 'title', 'formatted_planning_text', 'is_completed', 'current_step')
        }),
        (' ', {
            'fields': ('planning_options_display_detail',),
            'classes': ('collapse',)
        }),
        (' ', {
            'fields': ('story_preview',),
            'classes': ('collapse',)
        }),
        (' ', {
            'fields': ('scene_preview',),
            'classes': ('collapse',)
        }),
        (' ', {
            'fields': ('storyboard_preview',),
            'classes': ('collapse',)
        }),
        ('  (JSON)', {
            'fields': ('stories', 'selected_story', 'scenes', 'selected_scene', 
                      'shots', 'selected_shot', 'storyboards'),
            'classes': ('collapse',),
            'description': '  JSON '
        }),
        ('', {
            'fields': ('created_at', 'updated_at')
        })
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(image_count=Count('images'))
        return queryset
    
    def title_display(self, obj):
        return format_html('<strong>{}</strong>', obj.title[:50] + '...' if len(obj.title) > 50 else obj.title)
    title_display.short_description = ''
    title_display.admin_order_field = 'title'
    
    def user_display(self, obj):
        if obj.user:
            return format_html('{}<br><small>{}</small>', obj.user.username, obj.user.email)
        return '-'
    user_display.short_description = ''
    user_display.admin_order_field = 'user__username'
    
    def planning_options_display(self, obj):
        """   """
        if obj.selected_story and isinstance(obj.selected_story, dict):
            options = obj.selected_story.get('planning_options', {})
            if options:
                tone = options.get('tone', '-')
                genre = options.get('genre', '-')
                return format_html('<small>: {}<br>: {}</small>', tone, genre)
        return '-'
    planning_options_display.short_description = ' '
    
    def planning_options_display_detail(self, obj):
        """    """
        if obj.selected_story and isinstance(obj.selected_story, dict):
            options = obj.selected_story.get('planning_options', {})
            if options:
                html = '<table style="width: 100%; border-collapse: collapse;">'
                html += '<tr><th style="text-align: left; padding: 5px;"></th><th style="text-align: left; padding: 5px;"></th></tr>'
                
                option_names = {
                    'tone': '',
                    'genre': '',
                    'concept': '',
                    'target': '',
                    'purpose': '',
                    'duration': '',
                    'story_framework': ' ',
                    'development_level': ' '
                }
                
                for key, name in option_names.items():
                    value = options.get(key, '-')
                    if value and value != '-':
                        html += f'<tr><td style="padding: 5px;"><strong>{name}:</strong></td><td style="padding: 5px;">{value}</td></tr>'
                
                html += '</table>'
                return mark_safe(html)
        return '   .'
    planning_options_display_detail.short_description = '  '
    
    def progress_display(self, obj):
        steps = ['', '', '', '', '']
        current = min(obj.current_step - 1, 4)
        
        html = '<div style="display: flex; gap: 5px;">'
        for i, step in enumerate(steps):
            if i <= current:
                color = '#4CAF50' if obj.is_completed and i == 4 else '#2196F3'
                html += f'<span style="background: {color}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{step}</span>'
            else:
                html += f'<span style="background: #ddd; color: #666; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{step}</span>'
        html += '</div>'
        
        return format_html(html)
    progress_display.short_description = ' '
    
    def image_count(self, obj):
        count = obj.image_count
        if count > 0:
            return format_html('<span style="background: #4CAF50; color: white; padding: 2px 8px; border-radius: 12px;">{}</span>', count)
        return '-'
    image_count.short_description = ''
    image_count.admin_order_field = 'image_count'
    
    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_display.short_description = ''
    created_at_display.admin_order_field = 'created_at'
    
    def formatted_planning_text(self, obj):
        return format_html('<div style="white-space: pre-wrap; background: #f5f5f5; padding: 10px; border-radius: 5px;">{}</div>', 
                         obj.planning_text)
    formatted_planning_text.short_description = ' '
    
    def story_preview(self, obj):
        if obj.stories:
            html = '<div style="max-height: 400px; overflow-y: auto;">'
            for i, story in enumerate(obj.stories[:3]):  #  3 
                html += f'<div style="margin-bottom: 15px; padding: 10px; background: #f9f9f9; border-radius: 5px;">'
                html += f'<h4> {i+1}: {story.get("title", " ")}</h4>'
                html += f'<p>{story.get("summary", " ")}</p>'
                html += '</div>'
            if len(obj.stories) > 3:
                html += f'<p>...  {len(obj.stories) - 3} </p>'
            html += '</div>'
            return mark_safe(html)
        return '  .'
    story_preview.short_description = ' '
    
    def scene_preview(self, obj):
        if obj.scenes:
            html = '<div style="max-height: 400px; overflow-y: auto;">'
            for i, scene in enumerate(obj.scenes[:5]):  #  5 
                html += f'<div style="margin-bottom: 10px; padding: 8px; background: #f9f9f9; border-radius: 5px;">'
                html += f'<strong> {scene.get("scene_number", i+1)}:</strong> '
                html += f'{scene.get("location", " ")} - {scene.get("action", " ")}'
                html += '</div>'
            if len(obj.scenes) > 5:
                html += f'<p>...  {len(obj.scenes) - 5} </p>'
            html += '</div>'
            return mark_safe(html)
        return '  .'
    scene_preview.short_description = ' '
    
    def storyboard_preview(self, obj):
        if obj.storyboards:
            html = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px;">'
            for frame in obj.storyboards[:6]:  #  6 
                html += '<div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px;">'
                html += f'<strong> {frame.get("frame_number", "?")}</strong><br>'
                html += f'<small>{frame.get("title", " ")}</small><br>'
                html += f'<small style="color: #666;">{frame.get("composition", "  ")}</small>'
                html += '</div>'
            html += '</div>'
            if len(obj.storyboards) > 6:
                html += f'<p style="margin-top: 10px;">...  {len(obj.storyboards) - 6} </p>'
            return mark_safe(html)
        return '  .'
    storyboard_preview.short_description = ' '
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(is_completed=True, current_step=5)
        self.message_user(request, f'{updated}    .')
    mark_as_completed.short_description = '    '
    
    def export_as_json(self, request, queryset):
        import json
        from django.http import HttpResponse
        
        data = []
        for planning in queryset:
            data.append({
                'id': planning.id,
                'title': planning.title,
                'user': planning.user.username if planning.user else None,
                'planning_text': planning.planning_text,
                'planning_options': planning.selected_story.get('planning_options', {}) if planning.selected_story else {},
                'stories': planning.stories,
                'scenes': planning.scenes,
                'shots': planning.shots,
                'storyboards': planning.storyboards,
                'created_at': planning.created_at.isoformat(),
                'is_completed': planning.is_completed
            })
        
        response = HttpResponse(json.dumps(data, ensure_ascii=False, indent=2), 
                              content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="video_plannings.json"'
        return response
    export_as_json.short_description = '  JSON '
    
    def changelist_view(self, request, extra_context=None):
        #   
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        total_plannings = VideoPlanning.objects.count()
        completed_plannings = VideoPlanning.objects.filter(is_completed=True).count()
        today_plannings = VideoPlanning.objects.filter(created_at__date=today).count()
        week_plannings = VideoPlanning.objects.filter(created_at__date__gte=week_ago).count()
        month_plannings = VideoPlanning.objects.filter(created_at__date__gte=month_ago).count()
        
        #  
        step_stats = {}
        for i in range(1, 6):
            step_stats[f'step_{i}'] = VideoPlanning.objects.filter(current_step=i).count()
        
        #   
        popular_tones = {}
        popular_genres = {}
        
        plannings_with_options = VideoPlanning.objects.exclude(selected_story__isnull=True)
        for planning in plannings_with_options[:100]:  #  100 
            if planning.selected_story and isinstance(planning.selected_story, dict):
                options = planning.selected_story.get('planning_options', {})
                tone = options.get('tone', 'Unknown')
                genre = options.get('genre', 'Unknown')
                
                popular_tones[tone] = popular_tones.get(tone, 0) + 1
                popular_genres[genre] = popular_genres.get(genre, 0) + 1
        
        #  3 
        top_tones = sorted(popular_tones.items(), key=lambda x: x[1], reverse=True)[:3]
        top_genres = sorted(popular_genres.items(), key=lambda x: x[1], reverse=True)[:3]
        
        extra_context = extra_context or {}
        extra_context['planning_stats'] = {
            'total': total_plannings,
            'completed': completed_plannings,
            'completion_rate': f"{(completed_plannings / total_plannings * 100):.1f}" if total_plannings > 0 else "0",
            'today': today_plannings,
            'week': week_plannings,
            'month': month_plannings,
            'step_stats': step_stats,
            'top_tones': top_tones,
            'top_genres': top_genres,
        }
        
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(VideoPlanningImage)
class VideoPlanningImageAdmin(admin.ModelAdmin):
    list_display = ['planning_title', 'frame_number', 'image_thumbnail', 'prompt_preview', 'created_at']
    list_filter = ['created_at', 'planning']
    search_fields = ['planning__title', 'prompt_used']
    readonly_fields = ['planning', 'frame_number', 'image_preview_large', 'prompt_used', 'created_at']
    list_per_page = 30
    
    fieldsets = (
        (' ', {
            'fields': ('planning', 'frame_number')
        }),
        ('', {
            'fields': ('image_preview_large', 'image_url')
        }),
        ('', {
            'fields': ('prompt_used',)
        }),
        ('', {
            'fields': ('created_at',)
        })
    )
    
    def planning_title(self, obj):
        return obj.planning.title[:50] + '...' if len(obj.planning.title) > 50 else obj.planning.title
    planning_title.short_description = ' '
    planning_title.admin_order_field = 'planning__title'
    
    def image_thumbnail(self, obj):
        if obj.image_url:
            if obj.image_url.startswith('data:image'):
                return format_html('<img src="{}" style="max-width: 100px; max-height: 75px;" />', obj.image_url)
            else:
                return format_html('<a href="{}" target="_blank"><img src="{}" style="max-width: 100px; max-height: 75px;" /></a>', 
                                 obj.image_url, obj.image_url)
        return '-'
    image_thumbnail.short_description = ''
    
    def image_preview_large(self, obj):
        if obj.image_url:
            if obj.image_url.startswith('data:image'):
                return format_html('<img src="{}" style="max-width: 500px; max-height: 400px;" />', obj.image_url)
            else:
                return format_html('<a href="{}" target="_blank"><img src="{}" style="max-width: 500px; max-height: 400px;" /></a>', 
                                 obj.image_url, obj.image_url)
        return '-'
    image_preview_large.short_description = ' '
    
    def prompt_preview(self, obj):
        if obj.prompt_used:
            return obj.prompt_used[:50] + '...' if len(obj.prompt_used) > 50 else obj.prompt_used
        return '-'
    prompt_preview.short_description = ''