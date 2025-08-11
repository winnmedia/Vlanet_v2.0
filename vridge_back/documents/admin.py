from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'project', 'category', 'uploader', 'size', 'uploaded_at', 'is_active']
    list_filter = ['category', 'is_active', 'uploaded_at']
    search_fields = ['filename', 'description', 'project__name', 'uploader__username']
    readonly_fields = ['size', 'mime_type', 'download_count', 'uploaded_at', 'updated_at']
    
    fieldsets = (
        (' ', {
            'fields': ('project', 'filename', 'file', 'category')
        }),
        (' ', {
            'fields': ('description', 'uploader', 'size', 'mime_type')
        }),
        ('', {
            'fields': ('download_count', 'is_active')
        }),
        ('', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )