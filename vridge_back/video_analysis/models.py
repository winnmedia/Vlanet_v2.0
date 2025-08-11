"""
AI    
"""
from django.db import models
from django.conf import settings
from feedbacks.models import FeedBack
import json


class VideoAnalysisResult(models.Model):
    """AI   """
    
    ANALYSIS_STATUS_CHOICES = [
        ('pending', ''),
        ('processing', ''),
        ('completed', ''),
        ('failed', ''),
    ]
    
    feedback = models.OneToOneField(
        FeedBack, 
        on_delete=models.CASCADE,
        related_name='ai_analysis'
    )
    
    status = models.CharField(
        max_length=20,
        choices=ANALYSIS_STATUS_CHOICES,
        default='pending'
    )
    
    #  
    overall_score = models.FloatField(null=True, blank=True)
    
    #   (JSON)
    analysis_data = models.JSONField(default=dict)
    
    #  
    processing_time = models.FloatField(null=True, blank=True)
    
    # AI  
    ai_server_url = models.URLField(blank=True)
    ai_model_version = models.CharField(max_length=50, blank=True)
    
    # / 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    #  
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'video_analysis_results'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analysis for {self.feedback.title} - {self.status}"
    
    @property
    def feedback_list(self):
        """   """
        return self.analysis_data.get('feedback', [])
    
    @property
    def technical_info(self):
        """   """
        return self.analysis_data.get('technical_analysis', {})
    
    @property
    def improvement_suggestions(self):
        """   """
        return self.analysis_data.get('improvement_suggestions', [])


class AIFeedbackItem(models.Model):
    """AI  """
    
    FEEDBACK_TYPES = [
        ('composition', ''),
        ('lighting', ''),
        ('audio', ''),
        ('stability', ''),
        ('color', ''),
        ('motion', ''),
        ('editing', ''),
        ('storytelling', ''),
    ]
    
    analysis_result = models.ForeignKey(
        VideoAnalysisResult,
        on_delete=models.CASCADE,
        related_name='feedback_items'
    )
    
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    score = models.FloatField()  # 0-10 
    message = models.TextField()  #  
    timestamp = models.FloatField()  #    ()
    confidence = models.FloatField(default=1.0)  # AI 
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_feedback_items'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.get_feedback_type_display()} - {self.score}/10"


class AIAnalysisSettings(models.Model):
    """AI  """
    
    #   
    is_enabled = models.BooleanField(default=False)
    
    # AI  
    ai_server_url = models.URLField(
        default='',
        help_text='GCP GPU  URL'
    )
    api_key = models.CharField(max_length=255, blank=True)
    
    #  
    analyze_composition = models.BooleanField(default=True)
    analyze_lighting = models.BooleanField(default=True)
    analyze_audio = models.BooleanField(default=True)
    analyze_stability = models.BooleanField(default=True)
    analyze_color = models.BooleanField(default=True)
    analyze_motion = models.BooleanField(default=True)
    
    #  
    max_video_duration = models.IntegerField(
        default=300,  # 5
        help_text='    ()'
    )
    analysis_timeout = models.IntegerField(
        default=600,  # 10
        help_text='  ()'
    )
    
    #  
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'ai_analysis_settings'
        verbose_name = 'AI  '
        verbose_name_plural = 'AI  '
    
    def save(self, *args, **kwargs):
        #   -   
        if not self.pk and AIAnalysisSettings.objects.exists():
            raise ValueError('AI      .')
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """ AI   """
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    def __str__(self):
        status = "" if self.is_enabled else ""
        return f"AI   - {status}"