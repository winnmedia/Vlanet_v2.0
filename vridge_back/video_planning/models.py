from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
import json


class VideoPlanning(models.Model):
    """    """
    
    #  
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='video_plannings', null=True, blank=True)
    title = models.CharField(max_length=200)
    planning_text = models.TextField(help_text="  ")
    
    #   (JSON  )
    stories = models.JSONField(default=list, help_text="  ")
    selected_story = models.JSONField(null=True, blank=True, help_text=" ")
    
    scenes = models.JSONField(default=list, help_text="  ")
    selected_scene = models.JSONField(null=True, blank=True, help_text=" ")
    
    shots = models.JSONField(default=list, help_text="  ")
    selected_shot = models.JSONField(null=True, blank=True, help_text=" ")
    
    storyboards = models.JSONField(default=list, help_text=" () ")
    
    #   (,  ) -  
    planning_options = models.JSONField(default=dict, help_text="  (, ,  )")
    
    #   -     ( 0005 )
    # color_tone = models.JSONField(default=dict, help_text="  (primary, secondary, mood )")
    # camera_settings = models.JSONField(default=dict, help_text="  (, ,  )")
    # lighting_setup = models.JSONField(default=dict, help_text="  (, ,  )")
    # audio_config = models.JSONField(default=dict, help_text="  (BGM, ,  )")
    
    # AI   ( 0005 )
    # ai_generation_config = models.JSONField(default=dict, help_text="AI   (, ,  )")
    # prompt_templates = models.JSONField(default=list, help_text="   ")
    
    #   ( 0005 )
    # collaboration_settings = models.JSONField(default=dict, help_text="  (,   )")
    # workflow_config = models.JSONField(default=dict, help_text="  ( ,  )")
    
    #  
    is_completed = models.BooleanField(default=False, help_text="  ")
    current_step = models.IntegerField(default=1, help_text="   (1-5)")
    
    # 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'video_planning'
        verbose_name = ' '
        verbose_name_plural = '  '
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{self.title} - {username}"
    
    def save(self, *args, **kwargs):
        #       
        if not self.title and self.planning_text:
            self.title = self.planning_text[:50] + "..." if len(self.planning_text) > 50 else self.planning_text
        super().save(*args, **kwargs)


class VideoPlanningImage(models.Model):
    """   """
    
    planning = models.ForeignKey(VideoPlanning, on_delete=models.CASCADE, related_name='images')
    frame_number = models.IntegerField()
    image_url = models.URLField(max_length=500)
    prompt_used = models.TextField(blank=True, help_text="   ")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'video_planning_image'
        verbose_name = ' '
        verbose_name_plural = '  '
        ordering = ['planning', 'frame_number']
        unique_together = ['planning', 'frame_number']
    
    def __str__(self):
        return f"{self.planning.title} - Frame {self.frame_number}"
    
    def get_thumbnail_url(self):
        """ URL  (    )"""
        return self.image_url


class VideoPlanningProTemplate(models.Model):
    """    """
    
    name = models.CharField(max_length=100, help_text=" ")
    category = models.CharField(max_length=50, help_text=" (corporate, creative, educational )")
    description = models.TextField(help_text=" ")
    
    #  
    default_color_tone = models.JSONField(help_text="  ")
    default_camera_settings = models.JSONField(help_text="  ")
    default_lighting_setup = models.JSONField(help_text="  ")
    default_audio_config = models.JSONField(help_text="  ")
    
    # 
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0, help_text=" ")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'video_planning_pro_template'
        verbose_name = '   '
        verbose_name_plural = '    '
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    def increment_usage(self):
        """  """
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class VideoPlanningCollaboration(models.Model):
    """   """
    
    ROLE_CHOICES = [
        ('owner', ''),
        ('editor', ''),
        ('viewer', ''),
        ('reviewer', ''),
    ]
    
    STATUS_CHOICES = [
        ('invited', ''),
        ('accepted', ''),
        ('declined', ''),
        ('removed', ''),
    ]
    
    planning = models.ForeignKey(VideoPlanning, on_delete=models.CASCADE, related_name='collaborations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='invited')
    
    #  
    can_edit = models.BooleanField(default=False)
    can_comment = models.BooleanField(default=True)
    can_approve = models.BooleanField(default=False)
    can_invite = models.BooleanField(default=False)
    
    # 
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='video_planning_invitations_sent')
    invited_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'video_planning_collaboration'
        verbose_name = '  '
        verbose_name_plural = '   '
        unique_together = ['planning', 'user']
        indexes = [
            models.Index(fields=['planning', 'status']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.planning.title} - {self.user.username} ({self.get_role_display()})"
    
    def accept_invitation(self):
        """ """
        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.save()
    
    def decline_invitation(self):
        """ """
        self.status = 'declined'
        self.responded_at = timezone.now()
        self.save()
    
    def update_last_access(self):
        """   """
        self.last_accessed = timezone.now()
        self.save(update_fields=['last_accessed'])


class VideoPlanningAIPrompt(models.Model):
    """AI   """
    
    TYPE_CHOICES = [
        ('story', ' '),
        ('scene', ' '),
        ('shot', ' '),
        ('image', ' '),
        ('storyboard', ' '),
    ]
    
    planning = models.ForeignKey(VideoPlanning, on_delete=models.CASCADE, related_name='ai_prompts')
    prompt_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    original_prompt = models.TextField(help_text=" ")
    enhanced_prompt = models.TextField(help_text="AI  ")
    
    #  
    generation_result = models.JSONField(null=True, blank=True, help_text="AI  ")
    is_successful = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, help_text=" ")
    
    #  
    generation_time = models.FloatField(null=True, blank=True, help_text=" ()")
    tokens_used = models.IntegerField(null=True, blank=True, help_text="  ")
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, help_text=" ")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'video_planning_ai_prompt'
        verbose_name = 'AI '
        verbose_name_plural = 'AI  '
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['planning', 'prompt_type']),
            models.Index(fields=['is_successful', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_prompt_type_display()} - {self.planning.title}"
    
    def get_success_rate(self):
        """   """
        total = VideoPlanningAIPrompt.objects.filter(planning=self.planning).count()
        successful = VideoPlanningAIPrompt.objects.filter(planning=self.planning, is_successful=True).count()
        return (successful / total * 100) if total > 0 else 0


class VideoPlanningAnalytics(models.Model):
    """    """
    
    planning = models.OneToOneField(VideoPlanning, on_delete=models.CASCADE, related_name='analytics')
    
    #  
    view_count = models.IntegerField(default=0)
    edit_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    collaboration_count = models.IntegerField(default=0)
    
    # AI  
    ai_generation_count = models.IntegerField(default=0)
    ai_success_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    total_tokens_used = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    
    #  
    avg_generation_time = models.FloatField(default=0.0)
    completion_percentage = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    quality_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    
    #  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'video_planning_analytics'
        verbose_name = '  '
        verbose_name_plural = '   '
    
    def __str__(self):
        return f"{self.planning.title} - Analytics"
    
    def update_metrics(self):
        """ """
        # AI   
        ai_prompts = self.planning.ai_prompts.all()
        if ai_prompts.exists():
            successful = ai_prompts.filter(is_successful=True).count()
            self.ai_success_rate = (successful / ai_prompts.count()) * 100
            self.ai_generation_count = ai_prompts.count()
            self.total_tokens_used = sum(p.tokens_used or 0 for p in ai_prompts)
            self.total_cost = sum(p.cost_estimate or 0 for p in ai_prompts)
            
            #   
            times = [p.generation_time for p in ai_prompts if p.generation_time]
            if times:
                self.avg_generation_time = sum(times) / len(times)
        
        #  
        self.collaboration_count = self.planning.collaborations.filter(status='accepted').count()
        
        #  
        completion_factors = [
            bool(self.planning.selected_story),
            bool(self.planning.selected_scene),
            bool(self.planning.selected_shot),
            bool(self.planning.storyboards),
            self.planning.is_completed
        ]
        self.completion_percentage = (sum(completion_factors) / len(completion_factors)) * 100
        
        self.save()
    
    def get_efficiency_rating(self):
        """  """
        if self.ai_success_rate >= 90 and self.avg_generation_time <= 10:
            return 'excellent'
        elif self.ai_success_rate >= 75 and self.avg_generation_time <= 20:
            return 'good'
        elif self.ai_success_rate >= 60:
            return 'average'
        else:
            return 'needs_improvement'