"""
AI Video Generation Domain Models
Following DDD principles with clear bounded contexts
"""
import uuid
import json
from enum import Enum
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import JSONField
from core import models as core_model


class StoryStatus(models.TextChoices):
    """Story lifecycle states following state machine pattern"""
    DRAFT = 'draft', 'Draft'
    PLANNING = 'planning', 'Planning'
    PLANNED = 'planned', 'Planned'
    PREVIEWING = 'previewing', 'Previewing'
    PREVIEW_READY = 'preview_ready', 'Preview Ready'
    FINALIZING = 'finalizing', 'Finalizing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    ARCHIVED = 'archived', 'Archived'


class JobStatus(models.TextChoices):
    """Job queue status for async processing"""
    PENDING = 'pending', 'Pending'
    QUEUED = 'queued', 'Queued'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'
    RETRYING = 'retrying', 'Retrying'


class AIProvider(models.TextChoices):
    """Supported AI providers for video generation"""
    STABILITY_AI = 'stability_ai', 'Stability AI'
    RUNWAY_ML = 'runway_ml', 'Runway ML'
    REPLICATE = 'replicate', 'Replicate'
    OPENAI = 'openai', 'OpenAI'
    ANTHROPIC = 'anthropic', 'Anthropic'


class Story(core_model.TimeStampedModel):
    """
    Main aggregate root for AI video generation
    Represents a complete video project with scenes
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Ownership and identity
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='ai_stories',
        verbose_name='Project'
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='ai_stories',
        verbose_name='Owner'
    )
    
    # Basic information
    title = models.CharField(max_length=255, verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')
    
    # State management
    status = models.CharField(
        max_length=20,
        choices=StoryStatus.choices,
        default=StoryStatus.DRAFT,
        verbose_name='Status',
        db_index=True
    )
    
    # Video configuration
    duration_seconds = models.IntegerField(
        default=30,
        validators=[MinValueValidator(5), MaxValueValidator(300)],
        verbose_name='Duration (seconds)'
    )
    fps = models.IntegerField(
        default=30,
        choices=[(24, '24 FPS'), (30, '30 FPS'), (60, '60 FPS')],
        verbose_name='Frame Rate'
    )
    resolution = models.CharField(
        max_length=20,
        default='1920x1080',
        choices=[
            ('1920x1080', 'Full HD (1920x1080)'),
            ('1280x720', 'HD (1280x720)'),
            ('3840x2160', '4K (3840x2160)'),
            ('1080x1920', 'Vertical (1080x1920)'),
            ('1080x1080', 'Square (1080x1080)')
        ],
        verbose_name='Resolution'
    )
    
    # AI Generation settings
    style_preset = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Style Preset',
        help_text='Visual style for AI generation'
    )
    ai_provider = models.CharField(
        max_length=20,
        choices=AIProvider.choices,
        default=AIProvider.STABILITY_AI,
        verbose_name='AI Provider'
    )
    
    # Storage and outputs
    preview_url = models.URLField(blank=True, verbose_name='Preview URL')
    final_video_url = models.URLField(blank=True, verbose_name='Final Video URL')
    thumbnail_url = models.URLField(blank=True, verbose_name='Thumbnail URL')
    
    # Metadata and tracking
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Metadata')
    generation_config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Generation Config',
        help_text='AI provider specific configuration'
    )
    
    # State transition timestamps
    planning_started_at = models.DateTimeField(null=True, blank=True)
    planning_completed_at = models.DateTimeField(null=True, blank=True)
    preview_started_at = models.DateTimeField(null=True, blank=True)
    preview_completed_at = models.DateTimeField(null=True, blank=True)
    rendering_started_at = models.DateTimeField(null=True, blank=True)
    rendering_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Cost tracking
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Estimated Cost ($)'
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Actual Cost ($)'
    )
    
    # Business rules tracking
    is_locked = models.BooleanField(
        default=False,
        verbose_name='Is Locked',
        help_text='Story is locked for editing once planned'
    )
    locked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Locked At'
    )
    locked_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='locked_stories',
        verbose_name='Locked By'
    )
    
    class Meta:
        verbose_name = 'AI Story'
        verbose_name_plural = 'AI Stories'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['status', 'user']),
            models.Index(fields=['project', 'status']),
            models.Index(fields=['created']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    # Domain Properties - Business Rules
    @property
    def total_scenes_count(self):
        """Get total number of scenes"""
        return self.scenes.count()
    
    @property
    def has_minimum_scenes(self):
        """Check if story has minimum required scenes (12)"""
        return self.total_scenes_count >= 12
    
    @property
    def can_be_planned(self):
        """Check if story can transition to planned state"""
        return (
            self.status == StoryStatus.PLANNING and
            self.has_minimum_scenes and
            all(scene.prompts.filter(is_active=True).exists() for scene in self.scenes.all())
        )
    
    @property
    def total_duration(self):
        """Calculate total story duration from scenes"""
        return self.scenes.aggregate(
            total=models.Sum('duration')
        )['total'] or 0
    
    @property
    def is_ready_for_preview(self):
        """Check if story is ready for preview generation"""
        return (
            self.status == StoryStatus.PLANNED and
            self.is_locked and
            all(scene.prompts.filter(is_selected=True).exists() for scene in self.scenes.all())
        )
    
    @property
    def preview_progress(self):
        """Get preview generation progress percentage"""
        if self.status not in [StoryStatus.PREVIEWING, StoryStatus.PREVIEW_READY]:
            return 0
        
        total_scenes = self.total_scenes_count
        if total_scenes == 0:
            return 0
            
        scenes_with_preview = self.scenes.exclude(preview_image_url='').count()
        return (scenes_with_preview / total_scenes) * 100
    
    @property
    def final_render_progress(self):
        """Get final render progress percentage"""
        if self.status != StoryStatus.FINALIZING:
            return 0
        
        total_scenes = self.total_scenes_count
        if total_scenes == 0:
            return 0
            
        scenes_with_video = self.scenes.exclude(video_segment_url='').count()
        return (scenes_with_video / total_scenes) * 100
    
    def can_transition_to(self, new_status):
        """Validate state transitions based on state machine rules and business logic"""
        # Basic transition rules
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
        
        # Check if transition is allowed by state machine
        if new_status not in transitions.get(self.status, []):
            return False
        
        # Apply business rule validations
        if new_status == StoryStatus.PLANNED:
            # Cannot transition to PLANNED without minimum scenes and prompts
            if not self.can_be_planned:
                return False
                
        elif new_status == StoryStatus.PREVIEWING:
            # Cannot start previewing if not ready
            if not self.is_ready_for_preview:
                return False
                
        elif new_status == StoryStatus.FINALIZING:
            # Cannot start finalizing without completed preview
            if self.status != StoryStatus.PREVIEW_READY or not self.preview_url:
                return False
        
        # Locked stories cannot be transitioned back to editable states
        if self.is_locked and new_status in [StoryStatus.DRAFT, StoryStatus.PLANNING]:
            return False
        
        return True
    
    def transition_to(self, new_status):
        """Execute state transition with validation"""
        if not self.can_transition_to(new_status):
            raise ValueError(f"Cannot transition from {self.status} to {new_status}")
        
        old_status = self.status
        self.status = new_status
        
        # Track transition timestamps
        from django.utils import timezone
        now = timezone.now()
        
        if new_status == StoryStatus.PLANNING:
            self.planning_started_at = now
        elif new_status == StoryStatus.PLANNED:
            self.planning_completed_at = now
        elif new_status == StoryStatus.PREVIEWING:
            self.preview_started_at = now
        elif new_status == StoryStatus.PREVIEW_READY:
            self.preview_completed_at = now
        elif new_status == StoryStatus.FINALIZING:
            self.rendering_started_at = now
        elif new_status == StoryStatus.COMPLETED:
            self.rendering_completed_at = now
        
        self.save()
        
        # Auto-lock story when planned
        if new_status == StoryStatus.PLANNED and not self.is_locked:
            self.lock_story(self.user)
        
        # Create state transition log
        StoryStateTransition.objects.create(
            story=self,
            from_status=old_status,
            to_status=new_status,
            user=self.user
        )
        
        return self
    
    def lock_story(self, user):
        """Lock story to prevent further editing"""
        if self.is_locked:
            raise ValueError("Story is already locked")
        
        from django.utils import timezone
        self.is_locked = True
        self.locked_at = timezone.now()
        self.locked_by = user
        self.save()
        return self
    
    def unlock_story(self, user):
        """Unlock story for editing (admin only)"""
        if not self.is_locked:
            raise ValueError("Story is not locked")
        
        # Only allow unlocking if story is not in processing states
        if self.status in [StoryStatus.PREVIEWING, StoryStatus.FINALIZING]:
            raise ValueError("Cannot unlock story during processing")
        
        self.is_locked = False
        self.locked_at = None
        self.locked_by = None
        self.save()
        return self
    
    def validate_business_invariants(self):
        """Validate all business rules and invariants"""
        violations = []
        
        # Rule 1: Planned stories must have minimum scenes
        if self.status == StoryStatus.PLANNED and not self.has_minimum_scenes:
            violations.append(f"Planned story must have at least 12 scenes, found {self.total_scenes_count}")
        
        # Rule 2: Planned stories must be locked
        if self.status == StoryStatus.PLANNED and not self.is_locked:
            violations.append("Planned story must be locked")
        
        # Rule 3: All scenes must have active prompts for planning
        if self.status in [StoryStatus.PLANNING, StoryStatus.PLANNED]:
            scenes_without_prompts = [
                scene for scene in self.scenes.all() 
                if not scene.prompts.filter(is_active=True).exists()
            ]
            if scenes_without_prompts:
                violations.append(f"Scenes missing active prompts: {[s.order for s in scenes_without_prompts]}")
        
        # Rule 4: Preview ready requires preview URL
        if self.status == StoryStatus.PREVIEW_READY and not self.preview_url:
            violations.append("Preview ready state requires preview URL")
        
        # Rule 5: Completed stories require final video URL
        if self.status == StoryStatus.COMPLETED and not self.final_video_url:
            violations.append("Completed story must have final video URL")
        
        # Rule 6: Duration consistency
        calculated_duration = self.total_duration
        if abs(calculated_duration - self.duration_seconds) > 5:  # 5 second tolerance
            violations.append(f"Duration mismatch: expected {self.duration_seconds}s, calculated {calculated_duration}s")
        
        return violations
    
    def estimate_generation_cost(self):
        """Calculate estimated cost for AI generation"""
        if not hasattr(self, '_provider_config'):
            try:
                self._provider_config = AIProviderConfig.objects.get(
                    provider=self.ai_provider, 
                    is_active=True
                )
            except AIProviderConfig.DoesNotExist:
                return 0
        
        config = self._provider_config
        total_cost = 0
        
        # Image generation cost (preview)
        scene_count = self.total_scenes_count
        total_cost += scene_count * float(config.cost_per_image)
        
        # Video generation cost (final render)
        video_duration = self.duration_seconds
        total_cost += video_duration * float(config.cost_per_second_video)
        
        self.estimated_cost = total_cost
        return total_cost
    
    def can_be_deleted(self):
        """Check if story can be safely deleted"""
        # Cannot delete stories in processing states
        if self.status in [StoryStatus.PREVIEWING, StoryStatus.FINALIZING]:
            return False
        
        # Check for dependent jobs
        active_jobs = self.jobs.filter(
            status__in=[JobStatus.QUEUED, JobStatus.PROCESSING, JobStatus.RETRYING]
        ).exists()
        
        return not active_jobs


class Scene(core_model.TimeStampedModel):
    """
    Individual scene within a story
    Represents a segment of the video with specific content
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='scenes',
        verbose_name='Story'
    )
    
    # Scene properties
    order = models.PositiveIntegerField(verbose_name='Order', db_index=True)
    title = models.CharField(max_length=255, verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')
    
    # Timing
    start_time = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name='Start Time (seconds)'
    )
    end_time = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name='End Time (seconds)'
    )
    duration = models.FloatField(
        validators=[MinValueValidator(0.1)],
        verbose_name='Duration (seconds)'
    )
    
    # Content configuration
    scene_type = models.CharField(
        max_length=50,
        choices=[
            ('intro', 'Intro'),
            ('main', 'Main Content'),
            ('transition', 'Transition'),
            ('outro', 'Outro'),
            ('text_overlay', 'Text Overlay'),
            ('b_roll', 'B-Roll')
        ],
        default='main',
        verbose_name='Scene Type'
    )
    
    # Generated assets
    preview_image_url = models.URLField(blank=True, verbose_name='Preview Image')
    video_segment_url = models.URLField(blank=True, verbose_name='Video Segment')
    
    # AI generation tracking
    generation_attempts = models.PositiveIntegerField(default=0)
    last_generation_at = models.DateTimeField(null=True, blank=True)
    generation_metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Scene'
        verbose_name_plural = 'Scenes'
        ordering = ['story', 'order']
        unique_together = [['story', 'order']]
        indexes = [
            models.Index(fields=['story', 'order']),
        ]
    
    def __str__(self):
        return f"{self.story.title} - Scene {self.order}: {self.title}"
    
    # Domain Properties
    @property
    def has_active_prompts(self):
        """Check if scene has at least one active prompt"""
        return self.prompts.filter(is_active=True).exists()
    
    @property
    def selected_prompt(self):
        """Get the currently selected prompt for generation"""
        return self.prompts.filter(is_selected=True, is_active=True).first()
    
    @property
    def is_generated(self):
        """Check if scene has generated content"""
        return bool(self.preview_image_url or self.video_segment_url)
    
    @property
    def generation_status(self):
        """Get generation status based on available assets"""
        if self.video_segment_url:
            return 'video_ready'
        elif self.preview_image_url:
            return 'preview_ready'
        elif self.last_generation_at:
            return 'generating'
        else:
            return 'not_generated'
    
    # Business Methods
    def can_be_generated(self):
        """Check if scene can be generated"""
        if not self.has_active_prompts:
            return False
        
        if not self.selected_prompt:
            return False
        
        # Cannot generate if story is not in appropriate state
        if self.story.status not in [StoryStatus.PREVIEWING, StoryStatus.FINALIZING]:
            return False
        
        return True
    
    def validate_timing_constraints(self):
        """Validate scene timing against story constraints"""
        violations = []
        
        # Start time must be non-negative
        if self.start_time < 0:
            violations.append("Start time cannot be negative")
        
        # End time must be after start time
        if self.end_time <= self.start_time:
            violations.append("End time must be after start time")
        
        # Duration must match calculated duration
        calculated_duration = self.end_time - self.start_time
        if abs(self.duration - calculated_duration) > 0.1:  # 0.1s tolerance
            violations.append(f"Duration mismatch: {self.duration}s vs calculated {calculated_duration}s")
        
        # Scene must fit within story duration
        if self.end_time > self.story.duration_seconds:
            violations.append(f"Scene extends beyond story duration ({self.story.duration_seconds}s)")
        
        # Check for overlaps with other scenes (within same story)
        overlapping_scenes = Scene.objects.filter(
            story=self.story
        ).exclude(
            id=self.id
        ).filter(
            models.Q(start_time__lt=self.end_time) & models.Q(end_time__gt=self.start_time)
        )
        
        if overlapping_scenes.exists():
            overlaps = [f"Scene {s.order}" for s in overlapping_scenes]
            violations.append(f"Scene overlaps with: {', '.join(overlaps)}")
        
        return violations
    
    def record_generation_attempt(self, success=True, metadata=None):
        """Record AI generation attempt for analytics"""
        from django.utils import timezone
        
        self.generation_attempts += 1
        self.last_generation_at = timezone.now()
        
        if metadata:
            self.generation_metadata.update(metadata)
        
        # Update prompt success rate if we have a selected prompt
        if self.selected_prompt and success:
            prompt = self.selected_prompt
            prompt.generation_count += 1
            total_successes = prompt.generation_count * (prompt.success_rate / 100)
            total_successes += 1 if success else 0
            prompt.success_rate = (total_successes / prompt.generation_count) * 100
            prompt.save()
        
        self.save()
        return self
    
    def save(self, *args, **kwargs):
        # Auto-calculate duration if not set
        if not self.duration and self.start_time is not None and self.end_time is not None:
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)


class ScenePrompt(core_model.TimeStampedModel):
    """
    AI prompts for scene generation
    Supports multiple prompt variations and A/B testing
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    scene = models.ForeignKey(
        Scene,
        on_delete=models.CASCADE,
        related_name='prompts',
        verbose_name='Scene'
    )
    
    # Prompt configuration
    prompt_type = models.CharField(
        max_length=50,
        choices=[
            ('image', 'Image Generation'),
            ('video', 'Video Generation'),
            ('audio', 'Audio Generation'),
            ('text', 'Text Generation'),
            ('motion', 'Motion/Animation')
        ],
        verbose_name='Prompt Type'
    )
    
    # Prompt content
    system_prompt = models.TextField(
        blank=True,
        verbose_name='System Prompt',
        help_text='System-level instructions for AI'
    )
    user_prompt = models.TextField(
        verbose_name='User Prompt',
        help_text='Main prompt for content generation'
    )
    negative_prompt = models.TextField(
        blank=True,
        verbose_name='Negative Prompt',
        help_text='What to avoid in generation'
    )
    
    # Generation parameters
    parameters = models.JSONField(
        default=dict,
        verbose_name='Parameters',
        help_text='Provider-specific generation parameters'
    )
    
    # Versioning and selection
    version = models.PositiveIntegerField(default=1, verbose_name='Version')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    is_selected = models.BooleanField(default=False, verbose_name='Is Selected')
    
    # Performance tracking
    generation_count = models.PositiveIntegerField(default=0)
    success_rate = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Success Rate (%)'
    )
    average_quality_score = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name='Average Quality Score'
    )
    
    class Meta:
        verbose_name = 'Scene Prompt'
        verbose_name_plural = 'Scene Prompts'
        ordering = ['scene', '-version']
        indexes = [
            models.Index(fields=['scene', 'prompt_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.scene.title} - {self.prompt_type} v{self.version}"
    
    # Domain Properties
    @property
    def effectiveness_score(self):
        """Calculate prompt effectiveness based on success rate and quality"""
        if self.generation_count == 0:
            return 0
        
        # Weight success rate (70%) and quality score (30%)
        return (self.success_rate * 0.7) + (self.average_quality_score * 10 * 0.3)
    
    @property
    def is_performing_well(self):
        """Check if prompt is performing above minimum threshold"""
        return self.effectiveness_score >= 70  # 70% effectiveness threshold
    
    # Business Methods
    def select_as_active(self):
        """Select this prompt as the active prompt for the scene"""
        if not self.is_active:
            raise ValueError("Cannot select inactive prompt")
        
        # Deselect other prompts for this scene and prompt type
        ScenePrompt.objects.filter(
            scene=self.scene,
            prompt_type=self.prompt_type,
            is_selected=True
        ).exclude(id=self.id).update(is_selected=False)
        
        self.is_selected = True
        self.save()
        return self
    
    def create_variation(self, user_prompt_variation, **kwargs):
        """Create a new variation of this prompt for A/B testing"""
        new_version = ScenePrompt.objects.filter(
            scene=self.scene,
            prompt_type=self.prompt_type
        ).aggregate(
            max_version=models.Max('version')
        )['max_version'] + 1
        
        variation = ScenePrompt.objects.create(
            scene=self.scene,
            prompt_type=self.prompt_type,
            system_prompt=kwargs.get('system_prompt', self.system_prompt),
            user_prompt=user_prompt_variation,
            negative_prompt=kwargs.get('negative_prompt', self.negative_prompt),
            parameters=kwargs.get('parameters', self.parameters.copy()),
            version=new_version,
            is_active=True,
            is_selected=False
        )
        
        return variation
    
    def validate_prompt_constraints(self):
        """Validate prompt content and parameters"""
        violations = []
        
        # User prompt is required
        if not self.user_prompt.strip():
            violations.append("User prompt cannot be empty")
        
        # Prompt length constraints
        if len(self.user_prompt) > 2000:
            violations.append("User prompt too long (max 2000 characters)")
        
        if len(self.system_prompt) > 1000:
            violations.append("System prompt too long (max 1000 characters)")
        
        if len(self.negative_prompt) > 1000:
            violations.append("Negative prompt too long (max 1000 characters)")
        
        # Only one selected prompt per scene/type combination
        if self.is_selected:
            other_selected = ScenePrompt.objects.filter(
                scene=self.scene,
                prompt_type=self.prompt_type,
                is_selected=True
            ).exclude(id=self.id)
            
            if other_selected.exists():
                violations.append(f"Another prompt is already selected for {self.prompt_type}")
        
        # Validate parameters based on prompt type
        if self.prompt_type == 'image':
            self._validate_image_parameters(violations)
        elif self.prompt_type == 'video':
            self._validate_video_parameters(violations)
        
        return violations
    
    def _validate_image_parameters(self, violations):
        """Validate image generation parameters"""
        params = self.parameters
        
        if 'width' in params and 'height' in params:
            width, height = params['width'], params['height']
            if width * height > 2048 * 2048:
                violations.append("Image resolution too high (max 2048x2048)")
        
        if 'steps' in params:
            steps = params['steps']
            if not (1 <= steps <= 100):
                violations.append("Steps must be between 1 and 100")
    
    def _validate_video_parameters(self, violations):
        """Validate video generation parameters"""
        params = self.parameters
        
        if 'duration' in params:
            duration = params['duration']
            if not (1 <= duration <= 30):
                violations.append("Video duration must be between 1 and 30 seconds")
        
        if 'fps' in params:
            fps = params['fps']
            if fps not in [24, 30, 60]:
                violations.append("FPS must be 24, 30, or 60")
    
    def update_quality_score(self, new_score):
        """Update average quality score with new rating"""
        if not (0 <= new_score <= 10):
            raise ValueError("Quality score must be between 0 and 10")
        
        # Calculate new average using rolling average
        total_ratings = self.generation_count
        if total_ratings == 0:
            self.average_quality_score = new_score
        else:
            current_total = self.average_quality_score * total_ratings
            new_total = current_total + new_score
            self.average_quality_score = new_total / (total_ratings + 1)
        
        self.save()
        return self


class Job(core_model.TimeStampedModel):
    """
    Background job for async processing
    Integrates with BullMQ/Redis queue system
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Job identification
    job_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Queue Job ID',
        help_text='BullMQ job identifier'
    )
    queue_name = models.CharField(
        max_length=100,
        default='ai-video-generation',
        verbose_name='Queue Name'
    )
    
    # Related entities
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='jobs',
        null=True,
        blank=True,
        verbose_name='Story'
    )
    scene = models.ForeignKey(
        Scene,
        on_delete=models.CASCADE,
        related_name='jobs',
        null=True,
        blank=True,
        verbose_name='Scene'
    )
    
    # Job details
    job_type = models.CharField(
        max_length=50,
        choices=[
            ('story_planning', 'Story Planning'),
            ('scene_generation', 'Scene Generation'),
            ('preview_generation', 'Preview Generation'),
            ('final_render', 'Final Render'),
            ('thumbnail_generation', 'Thumbnail Generation'),
            ('upload_to_storage', 'Upload to Storage'),
            ('cleanup', 'Cleanup')
        ],
        verbose_name='Job Type'
    )
    
    status = models.CharField(
        max_length=20,
        choices=JobStatus.choices,
        default=JobStatus.PENDING,
        verbose_name='Status',
        db_index=True
    )
    
    # Job configuration and data
    payload = models.JSONField(
        default=dict,
        verbose_name='Payload',
        help_text='Input data for job processing'
    )
    result = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Result',
        help_text='Output data from job processing'
    )
    
    # Execution tracking
    priority = models.IntegerField(
        default=0,
        verbose_name='Priority',
        help_text='Higher priority jobs are processed first'
    )
    attempts = models.PositiveIntegerField(default=0, verbose_name='Attempts')
    max_attempts = models.PositiveIntegerField(default=3, verbose_name='Max Attempts')
    
    # Timing
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name='Scheduled At')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Started At')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Completed At')
    failed_at = models.DateTimeField(null=True, blank=True, verbose_name='Failed At')
    
    # Error tracking
    error_message = models.TextField(blank=True, verbose_name='Error Message')
    error_stack = models.TextField(blank=True, verbose_name='Error Stack Trace')
    
    # Worker information
    worker_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Worker ID',
        help_text='ID of the worker processing this job'
    )
    
    class Meta:
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-priority', 'created']
        indexes = [
            models.Index(fields=['status', 'queue_name']),
            models.Index(fields=['story', 'status']),
            models.Index(fields=['job_type', 'status']),
            models.Index(fields=['-priority', 'created']),
        ]
    
    def __str__(self):
        return f"{self.job_type} - {self.job_id} ({self.get_status_display()})"
    
    # Domain Properties
    @property
    def is_active(self):
        """Check if job is currently active/processing"""
        return self.status in [JobStatus.QUEUED, JobStatus.PROCESSING, JobStatus.RETRYING]
    
    @property
    def is_completed_successfully(self):
        """Check if job completed without errors"""
        return self.status == JobStatus.COMPLETED and not self.error_message
    
    @property
    def execution_duration(self):
        """Calculate job execution duration in seconds"""
        if not self.started_at:
            return None
        
        end_time = self.completed_at or self.failed_at
        if not end_time:
            from django.utils import timezone
            end_time = timezone.now()
        
        return (end_time - self.started_at).total_seconds()
    
    @property
    def wait_duration(self):
        """Calculate time spent waiting in queue"""
        if not self.started_at:
            return None
        
        queue_time = self.scheduled_at or self.created
        return (self.started_at - queue_time).total_seconds()
    
    # Business Methods
    def mark_as_started(self, worker_id=None):
        """Mark job as started by a worker"""
        if self.status != JobStatus.QUEUED:
            raise ValueError(f"Cannot start job in {self.status} status")
        
        from django.utils import timezone
        self.status = JobStatus.PROCESSING
        self.started_at = timezone.now()
        if worker_id:
            self.worker_id = worker_id
        self.save()
        return self
    
    def mark_as_completed(self, result_data=None):
        """Mark job as completed successfully"""
        if self.status != JobStatus.PROCESSING:
            raise ValueError(f"Cannot complete job in {self.status} status")
        
        from django.utils import timezone
        self.status = JobStatus.COMPLETED
        self.completed_at = timezone.now()
        if result_data:
            self.result = result_data
        self.save()
        return self
    
    def mark_as_failed(self, error_message, error_stack=None):
        """Mark job as failed with error details"""
        from django.utils import timezone
        self.status = JobStatus.FAILED
        self.failed_at = timezone.now()
        self.error_message = error_message
        if error_stack:
            self.error_stack = error_stack
        self.save()
        return self
    
    def validate_job_constraints(self):
        """Validate job data and constraints"""
        violations = []
        
        # Job ID must be unique
        if Job.objects.filter(job_id=self.job_id).exclude(id=self.id).exists():
            violations.append(f"Duplicate job ID: {self.job_id}")
        
        # Story or Scene reference required for most job types
        if self.job_type in ['story_planning', 'preview_generation', 'final_render']:
            if not self.story:
                violations.append(f"{self.job_type} requires story reference")
        
        if self.job_type == 'scene_generation':
            if not self.scene:
                violations.append("Scene generation requires scene reference")
        
        # Priority validation
        if not (-10 <= self.priority <= 10):
            violations.append("Priority must be between -10 and 10")
        
        # Max attempts validation
        if self.attempts > self.max_attempts:
            violations.append(f"Attempts ({self.attempts}) exceed maximum ({self.max_attempts})")
        
        # Status consistency checks
        if self.status == JobStatus.COMPLETED and not self.completed_at:
            violations.append("Completed jobs must have completion timestamp")
        
        if self.status == JobStatus.FAILED and not self.error_message:
            violations.append("Failed jobs must have error message")
        
        if self.status == JobStatus.PROCESSING and not self.started_at:
            violations.append("Processing jobs must have start timestamp")
        
        return violations
    
    def estimate_processing_time(self):
        """Estimate processing time based on job type and payload"""
        # Base estimates in seconds
        estimates = {
            'story_planning': 30,
            'scene_generation': 60,
            'preview_generation': 120,
            'final_render': 300,
            'thumbnail_generation': 15,
            'upload_to_storage': 30,
            'cleanup': 10
        }
        
        base_time = estimates.get(self.job_type, 60)
        
        # Adjust based on complexity
        if self.job_type == 'preview_generation' and self.story:
            scene_count = self.story.total_scenes_count
            base_time = base_time * (scene_count / 12)  # Scale with scene count
        
        if self.job_type == 'final_render' and self.story:
            duration = self.story.duration_seconds
            base_time = base_time * (duration / 30)  # Scale with video duration
        
        return int(base_time)
    
    def can_retry(self):
        """Check if job can be retried"""
        return self.attempts < self.max_attempts and self.status == JobStatus.FAILED
    
    def retry(self):
        """Retry failed job"""
        if not self.can_retry():
            raise ValueError("Job cannot be retried")
        
        self.status = JobStatus.RETRYING
        self.attempts += 1
        self.save()
        
        # Trigger re-queue logic here
        return self


class StoryStateTransition(core_model.TimeStampedModel):
    """
    Audit log for story state transitions
    Tracks all state changes for compliance and debugging
    """
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='state_transitions',
        verbose_name='Story'
    )
    
    from_status = models.CharField(
        max_length=20,
        choices=StoryStatus.choices,
        verbose_name='From Status'
    )
    to_status = models.CharField(
        max_length=20,
        choices=StoryStatus.choices,
        verbose_name='To Status'
    )
    
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='story_transitions',
        verbose_name='Performed By'
    )
    
    reason = models.TextField(
        blank=True,
        verbose_name='Reason',
        help_text='Reason for state transition'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadata',
        help_text='Additional context for transition'
    )
    
    class Meta:
        verbose_name = 'Story State Transition'
        verbose_name_plural = 'Story State Transitions'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['story', '-created']),
        ]
    
    def __str__(self):
        return f"{self.story.title}: {self.from_status} → {self.to_status}"


class AIProviderConfig(core_model.TimeStampedModel):
    """
    Configuration for AI providers
    Stores API keys, endpoints, and provider-specific settings
    """
    provider = models.CharField(
        max_length=20,
        choices=AIProvider.choices,
        unique=True,
        verbose_name='Provider'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    # API Configuration (encrypted in production)
    api_key = models.CharField(
        max_length=500,
        verbose_name='API Key',
        help_text='Encrypted API key'
    )
    api_endpoint = models.URLField(
        blank=True,
        verbose_name='API Endpoint',
        help_text='Custom endpoint if different from default'
    )
    
    # Rate limiting
    rate_limit_per_minute = models.PositiveIntegerField(
        default=60,
        verbose_name='Rate Limit (per minute)'
    )
    rate_limit_per_hour = models.PositiveIntegerField(
        default=1000,
        verbose_name='Rate Limit (per hour)'
    )
    
    # Cost configuration
    cost_per_image = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        verbose_name='Cost per Image ($)'
    )
    cost_per_second_video = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        verbose_name='Cost per Second of Video ($)'
    )
    
    # Provider-specific settings
    settings = models.JSONField(
        default=dict,
        verbose_name='Provider Settings',
        help_text='Provider-specific configuration'
    )
    
    # Usage tracking
    total_requests = models.PositiveIntegerField(default=0)
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Total Cost ($)'
    )
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'AI Provider Config'
        verbose_name_plural = 'AI Provider Configs'
        ordering = ['provider']
    
    def __str__(self):
        return f"{self.get_provider_display()} ({'Active' if self.is_active else 'Inactive'})"
    
    # Domain Methods
    def record_usage(self, cost_amount):
        """Record API usage and update statistics"""
        from django.utils import timezone
        
        self.total_requests += 1
        self.total_cost += cost_amount
        self.last_used_at = timezone.now()
        self.save()
        return self
    
    def is_within_rate_limits(self):
        """Check if current usage is within rate limits"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        # Check hourly limit
        hour_ago = now - timedelta(hours=1)
        recent_jobs = Job.objects.filter(
            created__gte=hour_ago,
            story__ai_provider=self.provider,
            status__in=[JobStatus.COMPLETED, JobStatus.PROCESSING]
        ).count()
        
        if recent_jobs >= self.rate_limit_per_hour:
            return False
        
        # Check per-minute limit
        minute_ago = now - timedelta(minutes=1)
        recent_jobs_minute = Job.objects.filter(
            created__gte=minute_ago,
            story__ai_provider=self.provider,
            status__in=[JobStatus.COMPLETED, JobStatus.PROCESSING]
        ).count()
        
        return recent_jobs_minute < self.rate_limit_per_minute


# Domain Services and Factory Methods
class StoryFactory:
    """Factory for creating properly configured stories"""
    
    @staticmethod
    def create_story(project, user, title, **kwargs):
        """Create a new story with proper defaults and validation"""
        story = Story(
            project=project,
            user=user,
            title=title,
            description=kwargs.get('description', ''),
            duration_seconds=kwargs.get('duration_seconds', 30),
            fps=kwargs.get('fps', 30),
            resolution=kwargs.get('resolution', '1920x1080'),
            ai_provider=kwargs.get('ai_provider', AIProvider.STABILITY_AI),
            style_preset=kwargs.get('style_preset', ''),
        )
        
        # Validate before saving
        violations = story.validate_business_invariants()
        if violations:
            raise ValueError(f"Story validation failed: {violations}")
        
        story.save()
        
        # Estimate initial cost
        story.estimate_generation_cost()
        story.save()
        
        return story
    
    @staticmethod
    def create_story_with_scenes(project, user, title, scene_data, **kwargs):
        """Create story with initial scenes"""
        story = StoryFactory.create_story(project, user, title, **kwargs)
        
        total_duration = 0
        for i, scene_info in enumerate(scene_data):
            scene = Scene.objects.create(
                story=story,
                order=i + 1,
                title=scene_info.get('title', f'Scene {i + 1}'),
                description=scene_info.get('description', ''),
                start_time=total_duration,
                end_time=total_duration + scene_info.get('duration', 2.5),
                duration=scene_info.get('duration', 2.5),
                scene_type=scene_info.get('scene_type', 'main')
            )
            
            # Create default prompt
            if 'prompt' in scene_info:
                ScenePrompt.objects.create(
                    scene=scene,
                    prompt_type='image',
                    user_prompt=scene_info['prompt'],
                    is_active=True,
                    is_selected=True,
                    version=1
                )
            
            total_duration = scene.end_time
        
        # Update story duration
        story.duration_seconds = int(total_duration)
        story.save()
        
        return story


class AIVideoGenerationService:
    """Domain service for coordinating AI video generation workflows"""
    
    @staticmethod
    def validate_story_readiness(story):
        """Comprehensive validation before generation"""
        all_violations = []
        
        # Story-level validation
        story_violations = story.validate_business_invariants()
        all_violations.extend(story_violations)
        
        # Scene-level validation
        for scene in story.scenes.all():
            scene_violations = scene.validate_timing_constraints()
            if scene_violations:
                all_violations.extend([f"Scene {scene.order}: {v}" for v in scene_violations])
        
        # Prompt-level validation
        for scene in story.scenes.all():
            for prompt in scene.prompts.filter(is_active=True):
                prompt_violations = prompt.validate_prompt_constraints()
                if prompt_violations:
                    all_violations.extend([f"Scene {scene.order} prompt: {v}" for v in prompt_violations])
        
        return all_violations
    
    @staticmethod
    def estimate_total_generation_time(story):
        """Estimate total time needed for complete generation"""
        if not story.can_be_planned:
            return 0
        
        # Preview generation time
        preview_time = story.total_scenes_count * 30  # 30 seconds per scene
        
        # Final render time (based on duration and complexity)
        render_time = story.duration_seconds * 10  # 10 seconds processing per second of video
        
        # Upload and processing overhead
        overhead_time = 60
        
        return preview_time + render_time + overhead_time
    
    @staticmethod
    def calculate_generation_priority(story):
        """Calculate job priority based on business rules"""
        priority = 0
        
        # User premium status
        if hasattr(story.user, 'is_premium') and story.user.is_premium:
            priority += 5
        
        # Story age (older stories get higher priority)
        from django.utils import timezone
        age_days = (timezone.now() - story.created).days
        priority += min(age_days, 3)  # Max 3 points for age
        
        # Story duration (shorter stories get priority)
        if story.duration_seconds <= 30:
            priority += 2
        elif story.duration_seconds <= 60:
            priority += 1
        
        # Retry attempts (failed jobs get lower priority)
        failed_jobs = story.jobs.filter(status=JobStatus.FAILED).count()
        priority -= failed_jobs
        
        return max(-10, min(10, priority))  # Clamp to valid range
    
    @staticmethod
    def cleanup_failed_generations(story):
        """Clean up resources from failed generation attempts"""
        # Cancel pending jobs
        pending_jobs = story.jobs.filter(
            status__in=[JobStatus.QUEUED, JobStatus.PENDING, JobStatus.RETRYING]
        )
        pending_jobs.update(status=JobStatus.CANCELLED)
        
        # Clear partial assets
        story.scenes.update(
            preview_image_url='',
            video_segment_url='',
            generation_metadata={}
        )
        
        # Reset story state if needed
        if story.status in [StoryStatus.PREVIEWING, StoryStatus.FINALIZING]:
            story.transition_to(StoryStatus.PLANNED)
        
        return story