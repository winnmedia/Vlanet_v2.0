from django.db import models
from core import models as core_model


class FeedBack(core_model.TimeStampedModel):
    # Project relationship
    project = models.ForeignKey(
        "projects.Project",
        related_name="feedbacks",
        on_delete=models.CASCADE,
        verbose_name="",
        null=True,  #  null  (  )
        blank=True
    )
    
    # User who created the feedback
    user = models.ForeignKey(
        "users.User",
        related_name="feedbacks",
        on_delete=models.CASCADE,
        verbose_name="",
        null=True,  #  null  (  )
        blank=True
    )
    
    # Feedback metadata
    title = models.CharField(
        verbose_name="",
        max_length=200,
        null=True,
        blank=True
    )
    description = models.TextField(
        verbose_name="",
        null=True,
        blank=True
    )
    
    # Status
    STATUS_CHOICES = [
        ('open', ''),
        ('resolved', ''),
        ('closed', ''),
    ]
    status = models.CharField(
        verbose_name="",
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    # Original file
    files = models.FileField(
        verbose_name=" ", upload_to="feedback_file", null=True, blank=True
    )
    
    # Encoded versions
    video_file_web = models.FileField(
        verbose_name="  ", upload_to="feedback_file/web", null=True, blank=True
    )
    video_file_high = models.CharField(
        verbose_name="  ", max_length=500, null=True, blank=True
    )
    video_file_medium = models.CharField(
        verbose_name="  ", max_length=500, null=True, blank=True
    )
    video_file_low = models.CharField(
        verbose_name="  ", max_length=500, null=True, blank=True
    )
    
    # Thumbnail - Temporarily changed to FileField due to missing Pillow
    thumbnail = models.FileField(
        verbose_name="", upload_to="feedback_file/thumbnails", null=True, blank=True
    )
    
    # HLS streaming
    hls_playlist_url = models.CharField(
        verbose_name="HLS  URL", max_length=500, null=True, blank=True
    )
    
    # Encoding status
    ENCODING_STATUS_CHOICES = [
        ('pending', ''),
        ('processing', ''),
        ('completed', ''),
        ('failed', ''),
        ('partial', ''),
    ]
    encoding_status = models.CharField(
        verbose_name=" ",
        max_length=20,
        choices=ENCODING_STATUS_CHOICES,
        default='pending',
        null=True,
        blank=True
    )
    
    # Video metadata
    duration = models.FloatField(verbose_name=" ()", null=True, blank=True)
    width = models.IntegerField(verbose_name=" ", null=True, blank=True)
    height = models.IntegerField(verbose_name=" ", null=True, blank=True)
    file_size = models.BigIntegerField(verbose_name=" (bytes)", null=True, blank=True)

    class Meta:
        verbose_name = " "
        verbose_name_plural = " "

    def __str__(self):
        if self.files:
            return f"{self.files.name}"
        else:
            return f"{self.id}"
    
    @property
    def video_file(self):
        """Backward compatibility property"""
        return self.files
    
    @property
    def is_video(self):
        """Check if uploaded file is a video"""
        try:
            if self.files and hasattr(self.files, 'name'):
                video_extensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv']
                return any(self.files.name.lower().endswith(ext) for ext in video_extensions)
        except Exception:
            pass
        return False


class FeedBackMessage(core_model.TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', ''),
        ('completed', ''),
    ]
    
    feedback = models.ForeignKey(
        "FeedBack",
        related_name="messages",
        on_delete=models.CASCADE,
        blank=False,
        verbose_name=" ",
    )
    user = models.ForeignKey(
        "users.User",
        related_name="messages",
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="",
    )
    text = models.TextField(verbose_name="", blank=False)
    status = models.CharField(
        verbose_name="",
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="   "
    )

    class Meta:
        verbose_name = " "
        verbose_name_plural = " "
        ordering = ("-created",)
        indexes = [
            models.Index(fields=['feedback', '-created']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
        ]


class FeedBackComment(core_model.TimeStampedModel):
    # Timestamp for video position
    timestamp = models.FloatField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="   ( )"
    )
    
    # Comment type
    TYPE_CHOICES = [
        ('general', ''),
        ('technical', ''),
        ('creative', ''),
        ('urgent', ''),
    ]
    type = models.CharField(
        verbose_name="",
        max_length=20,
        choices=TYPE_CHOICES,
        default='general'
    )
    
    # Comment content
    content = models.TextField(
        verbose_name="",
        null=True,
        blank=True
    )
    DISPLAY_MODE_CHOICES = [
        ('anonymous', ''),
        ('nickname', ''),
        ('realname', ''),
    ]
    
    feedback = models.ForeignKey(
        "FeedBack",
        related_name="comments",
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="",
    )
    user = models.ForeignKey(
        "users.User",
        related_name="comments",
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="",
    )
    security = models.BooleanField(verbose_name="", default=False)
    display_mode = models.CharField(
        verbose_name=" ",
        max_length=20,
        choices=DISPLAY_MODE_CHOICES,
        default='anonymous',
        help_text="   "
    )
    nickname = models.CharField(
        verbose_name="",
        max_length=20,
        null=True,
        blank=True,
        help_text="    "
    )
    title = models.TextField(verbose_name="", null=True, blank=False)
    section = models.TextField(verbose_name="", null=True, blank=False)
    text = models.TextField(verbose_name="", null=True, blank=False)
    
    # Add content field as an alias for compatibility
    @property
    def content(self):
        return self.text
    
    @content.setter
    def content(self, value):
        self.text = value

    class Meta:
        verbose_name = " "
        verbose_name_plural = " "
        ordering = ("-created",)
        indexes = [
            models.Index(fields=['feedback', '-created']),  #    
            models.Index(fields=['user']),  #   
        ]

    def __str__(self):
        if self.feedback and hasattr(self.feedback, 'projects') and self.feedback.projects:
            return f"  : {self.feedback.projects.name}"
        return f"  #{self.id}"


class FeedbackReaction(core_model.TimeStampedModel):
    """   """
    REACTION_CHOICES = [
        ('like', ''),
        ('dislike', ''),
        ('needExplanation', ''),
    ]
    
    message = models.ForeignKey(
        FeedBackMessage,
        related_name='reactions',
        on_delete=models.CASCADE,
        verbose_name=" "
    )
    user = models.ForeignKey(
        "users.User",
        related_name='feedback_reactions',
        on_delete=models.CASCADE,
        verbose_name=""
    )
    reaction_type = models.CharField(
        verbose_name=" ",
        max_length=20,
        choices=REACTION_CHOICES
    )
    
    class Meta:
        verbose_name = " "
        verbose_name_plural = " "
        unique_together = ['message', 'user']  #      
        indexes = [
            models.Index(fields=['message', 'user']),
            models.Index(fields=['reaction_type']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.message} - {self.reaction_type}"


class FeedbackFile(core_model.TimeStampedModel):
    """  """
    feedback = models.ForeignKey(
        FeedBack,
        related_name='attached_files',
        on_delete=models.CASCADE,
        verbose_name=""
    )
    file = models.FileField(
        verbose_name="",
        upload_to="feedback_files/%Y/%m/%d/"
    )
    filename = models.CharField(
        verbose_name="",
        max_length=255
    )
    file_type = models.CharField(
        verbose_name=" ",
        max_length=50,
        null=True,
        blank=True
    )
    file_size = models.BigIntegerField(
        verbose_name=" (bytes)",
        null=True,
        blank=True
    )
    uploaded_by = models.ForeignKey(
        "users.User",
        related_name='uploaded_feedback_files',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=" "
    )
    
    class Meta:
        verbose_name = " "
        verbose_name_plural = " "
        ordering = ("-created",)
        indexes = [
            models.Index(fields=['feedback', '-created']),
            models.Index(fields=['uploaded_by']),
        ]
    
    def __str__(self):
        return f"{self.feedback} - {self.filename}"
