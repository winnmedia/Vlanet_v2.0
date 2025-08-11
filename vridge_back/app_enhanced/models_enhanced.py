"""
HAR/OpenAPI    Enhanced Django 
        
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class VideoPlanningEnhanced(models.Model):
    """API    Enhanced VideoPlanning """
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True, help_text='status ')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'videoplanning_enhanced'
        verbose_name = 'VideoPlanning (Enhanced)'
        verbose_name_plural = 'VideoPlannings (Enhanced)'
        ordering = ['-id']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title or f'VideoPlanning({self.pk})'

    @property
    def age_in_days(self):
        """  """
        from django.utils import timezone
        return (timezone.now() - self.created_at).days


class ProjectEnhanced(models.Model):
    """API    Enhanced Project """
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    manager = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_enhanced'
        verbose_name = 'Project (Enhanced)'
        verbose_name_plural = 'Projects (Enhanced)'
        ordering = ['-id']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name or f'Project({self.pk})'

    @property
    def age_in_days(self):
        """  """
        from django.utils import timezone
        return (timezone.now() - self.created_at).days

