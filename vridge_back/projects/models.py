import hashlib
from django.db import models
from core import models as core_model


class DevelopmentFramework(core_model.TimeStampedModel):
    """   """
    name = models.CharField(verbose_name=" ", max_length=100)
    intro_hook = models.TextField(
        verbose_name=" ", 
        help_text=" 5       "
    )
    immersion = models.TextField(
        verbose_name="", 
        help_text="       "
    )
    twist = models.TextField(
        verbose_name="", 
        help_text="       "
    )
    hook_next = models.TextField(
        verbose_name="", 
        help_text="      "
    )
    is_default = models.BooleanField(
        verbose_name=" ", 
        default=False,
        help_text="   "
    )
    user = models.ForeignKey(
        "users.User",
        related_name="frameworks",
        on_delete=models.CASCADE,
        verbose_name="",
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "  "
        verbose_name_plural = "  "
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_default']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_default'],
                condition=models.Q(is_default=True),
                name='unique_default_framework_per_user',
                violation_error_message='      .'
            )
        ]
    
    def __str__(self):
        return f"{self.name} ({'' if self.is_default else ''})"
    
    def save(self, *args, **kwargs):
        if self.is_default:
            #    
            DevelopmentFramework.objects.filter(
                user=self.user, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class AbstractItem(core_model.TimeStampedModel):
    start_date = models.DateTimeField(verbose_name=" ", null=True, blank=True)
    end_date = models.DateTimeField(verbose_name=" ", null=True, blank=True)

    class Meta:
        abstract = True


class BasicPlan(AbstractItem):
    class Meta:
        verbose_name = "  "
        verbose_name_plural = "  "


class Storyboard(AbstractItem):
    class Meta:
        verbose_name = " "
        verbose_name_plural = " "


class Filming(AbstractItem):
    class Meta:
        verbose_name = "(/)"
        verbose_name_plural = "(/)"


class VideoEdit(AbstractItem):
    class Meta:
        verbose_name = " "
        verbose_name_plural = " "


class PostWork(AbstractItem):
    class Meta:
        verbose_name = " "
        verbose_name_plural = " "


class VideoPreview(AbstractItem):
    class Meta:
        verbose_name = " "
        verbose_name_plural = " "


class Confirmation(AbstractItem):
    class Meta:
        verbose_name = ""
        verbose_name_plural = ""


class VideoDelivery(AbstractItem):
    class Meta:
        verbose_name = " "
        verbose_name_plural = " "


class File(core_model.TimeStampedModel):
    project = models.ForeignKey(
        "Project",
        related_name="files",
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="",
    )
    files = models.FileField(
        verbose_name=" ", upload_to="project_file", blank=False
    )
    
    class Meta:
        verbose_name = " "
        verbose_name_plural = " "
        indexes = [
            models.Index(fields=['project', '-created']),  #    
        ]


class Members(core_model.TimeStampedModel):
    RATING_CHOICES = (
        ("manager", ""),
        ("normal", ""),
    )

    project = models.ForeignKey(
        "Project",
        related_name="members",
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="",
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="members",
        blank=False,
        verbose_name="",
    )
    rating = models.CharField(
        verbose_name="",
        choices=RATING_CHOICES,
        max_length=10,
        default="normal",
        blank=False,
    )

    class Meta:
        verbose_name = ""
        verbose_name_plural = ""
        indexes = [
            models.Index(fields=['project', 'user']),
            models.Index(fields=['user']),
        ]


class ProjectInvitation(core_model.TimeStampedModel):
    """  """
    project = models.ForeignKey(
        "Project",
        related_name="invitations",
        on_delete=models.CASCADE,
        verbose_name="",
    )
    inviter = models.ForeignKey(
        "users.User",
        related_name="sent_invitations",
        on_delete=models.CASCADE,
        verbose_name="",
    )
    invitee_email = models.EmailField(verbose_name="  ")
    message = models.TextField(verbose_name=" ", blank=True, null=True)
    
    STATUS_CHOICES = [
        ('pending', ''),
        ('accepted', ''),
        ('declined', ''),
        ('expired', ''),
        ('cancelled', ''),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=""
    )
    
    #     
    invitee = models.ForeignKey(
        "users.User",
        related_name="received_invitations",
        on_delete=models.CASCADE,
        verbose_name=" ",
        null=True,
        blank=True,
    )
    
    token = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=" "
    )
    
    expires_at = models.DateTimeField(verbose_name="")
    accepted_at = models.DateTimeField(verbose_name="", null=True, blank=True)
    declined_at = models.DateTimeField(verbose_name="", null=True, blank=True)

    class Meta:
        verbose_name = " "
        verbose_name_plural = " "
        unique_together = ['project', 'invitee_email']
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['invitee_email']),
            models.Index(fields=['invitee']),
            models.Index(fields=['status']),
            models.Index(fields=['token']),
        ]

    def __str__(self):
        return f"{self.project.name}  to {self.invitee_email}"


class Memo(core_model.TimeStampedModel):
    project = models.ForeignKey(
        "Project",
        related_name="memos",
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="",
    )
    # user = models.ForeignKey(
    #     "users.User",
    #     on_delete=models.CASCADE,
    #     related_name="members",
    #     blank=False,
    #     verbose_name="",
    # )
    date = models.DateField(verbose_name="", null=True)
    memo = models.TextField(verbose_name="", null=True, blank=False)

    class Meta:
        verbose_name = " "
        verbose_name_plural = " "
        indexes = [
            models.Index(fields=['project', '-date']),  #    
        ]

    def __str__(self):
        return self.project.name


class Project(core_model.TimeStampedModel):
    user = models.ForeignKey(
        "users.User",
        related_name="projects",
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="",
    )

    name = models.CharField(verbose_name=" ", max_length=100, blank=False)
    manager = models.CharField(verbose_name="", max_length=50, blank=False)
    consumer = models.CharField(verbose_name="", max_length=50, blank=False)
    description = models.TextField(verbose_name=" ", blank=True)
    color = models.CharField(verbose_name="", max_length=100, null=True, blank=True)
    
    tone_manner = models.CharField(verbose_name="", max_length=50, null=True, blank=True)
    genre = models.CharField(verbose_name="", max_length=50, null=True, blank=True)
    concept = models.CharField(verbose_name="", max_length=50, null=True, blank=True)
    
    #    - Railway     
    # is_public = models.BooleanField(default=False, null=True, blank=True, verbose_name=" ")
    # allow_comments = models.BooleanField(default=True, null=True, blank=True, verbose_name=" ")
    # allow_anonymous_feedback = models.BooleanField(default=False, null=True, blank=True, verbose_name="  ")
    # tags = models.JSONField(blank=True, null=True, default=list, verbose_name="")
    # last_activity = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name=" ")

    basic_plan = models.ForeignKey(
        "BasicPlan",
        related_name="projects",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="  ",
    )
    story_board = models.ForeignKey(
        "Storyboard",
        related_name="projects",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=" ",
    )
    filming = models.ForeignKey(
        "Filming",
        related_name="projects",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="",
    )
    video_edit = models.ForeignKey(
        "VideoEdit",
        related_name="projects",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=" ",
    )
    post_work = models.ForeignKey(
        "PostWork",
        related_name="projects",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=" ",
    )
    video_preview = models.ForeignKey(
        "VideoPreview",
        related_name="projects",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=" ",
    )
    confirmation = models.ForeignKey(
        "Confirmation",
        related_name="projects",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="",
    )
    video_delivery = models.ForeignKey(
        "VideoDelivery",
        related_name="projects",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=" ",
    )
    
    # development_framework       
    # development_framework = models.ForeignKey(
    #     "DevelopmentFramework",
    #     related_name="projects",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     verbose_name="  ",
    #     help_text="    "
    # )

    # OneToOneField  - FeedBack  ForeignKey  
    
    # Calendar and Project Management Fields (added in migration 0035)
    status = models.CharField(
        choices=[
            ('planning', '기획 중'),
            ('in_progress', '진행 중'), 
            ('review', '검토 중'),
            ('completed', '완료'),
            ('on_hold', '보류'),
            ('cancelled', '취소')
        ],
        default='planning',
        max_length=20,
        verbose_name='프로젝트 상태'
    )
    progress = models.IntegerField(
        default=0,
        help_text='0-100 진행률',
        verbose_name='진행률'
    )
    actual_end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='실제 종료일'
    )

    class Meta:
        verbose_name = "1."
        verbose_name_plural = "1."
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created']),
            models.Index(fields=['name']),
        ]
        constraints = [
            #     (5 )
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='unique_user_project_name',
                violation_error_message='    .'
            )
        ]

    def __str__(self):
        return self.name


class ProjectInvite(core_model.TimeStampedModel):
    project = models.ForeignKey(
        "projects.Project",
        related_name="invites",
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="",
    )
    email = models.CharField(
        verbose_name=" ", max_length=100, null=True, blank=False
    )

    def __str__(self):
        if self.project.name:
            return self.project.name
        else:
            return self.project.id

    class Meta:
        verbose_name = " "
        verbose_name_plural = " "


class SampleFiles(core_model.TimeStampedModel):
    files = models.FileField(verbose_name="", upload_to="sample_file", blank=False)

    class Meta:
        verbose_name = ""
        verbose_name_plural = ""

    def __str__(self):
        return str(self.files.name)


class IdempotencyRecord(models.Model):
    """    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    idempotency_key = models.CharField(max_length=255, db_index=True)
    project_id = models.IntegerField(null=True, blank=True)
    request_data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='processing')
    
    class Meta:
        unique_together = [['user', 'idempotency_key']]
        indexes = [
            models.Index(fields=['created_at']),
        ]
        verbose_name = "멱등성 기록"
        verbose_name_plural = "멱등성 기록"


class ProjectCalendarEvent(core_model.TimeStampedModel):
    """프로젝트 캘린더 이벤트 모델 (마이그레이션 0035에서 추가)"""
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_calendar_events',
        verbose_name='프로젝트'
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name='project_calendar_events',
        verbose_name='작성자'
    )
    title = models.CharField(max_length=200, verbose_name='제목')
    description = models.TextField(blank=True, verbose_name='설명')
    event_type = models.CharField(
        choices=[
            ('meeting', '회의'),
            ('deadline', '마감'),
            ('review', '검토'),
            ('milestone', '마일스톤'),
            ('other', '기타')
        ],
        default='other',
        max_length=20,
        verbose_name='이벤트 유형'
    )
    start_date = models.DateTimeField(verbose_name='시작 날짜')
    end_date = models.DateTimeField(verbose_name='종료 날짜')
    all_day = models.BooleanField(default=False, verbose_name='종일 이벤트')
    location = models.CharField(blank=True, max_length=200, verbose_name='장소')
    reminder_minutes = models.IntegerField(
        default=60,
        help_text='알림을 받을 시간 (분)',
        verbose_name='알림 시간 (분)'
    )
    is_notified = models.BooleanField(default=False, verbose_name='알림 발송됨')
    color = models.CharField(default='#1631F8', max_length=7, verbose_name='색상')
    attendees = models.ManyToManyField(
        "users.User",
        blank=True,
        related_name='attending_events',
        verbose_name='참석자'
    )

    class Meta:
        verbose_name = "프로젝트 캘린더 이벤트"
        verbose_name_plural = "프로젝트 캘린더 이벤트"
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['project', 'start_date']),
            models.Index(fields=['user', 'start_date']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['is_notified']),
        ]

    def __str__(self):
        return f"{self.title} ({self.start_date.strftime('%Y-%m-%d')})"


class RecentInvitee(core_model.TimeStampedModel):
    """최근 초대한 사용자 모델 (마이그레이션 0035에서 추가)"""
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name='recent_invitees',
        verbose_name='초대자'
    )
    invitee_email = models.EmailField(verbose_name='초대받은 이메일')
    invitee_name = models.CharField(max_length=100, verbose_name='초대받은 이름')
    invitee = models.ForeignKey(
        "users.User",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='invited_by',
        verbose_name='초대받은 사용자'
    )
    is_favorite = models.BooleanField(default=False, verbose_name='즐겨찾기')
    last_invited_at = models.DateTimeField(auto_now=True, verbose_name='마지막 초대일')
    invite_count = models.IntegerField(default=1, verbose_name='초대 횟수')

    class Meta:
        verbose_name = "최근 초대자"
        verbose_name_plural = "최근 초대자"
        ordering = ['-is_favorite', '-last_invited_at']
        unique_together = [('user', 'invitee_email')]
        indexes = [
            models.Index(fields=['user', '-last_invited_at']),
            models.Index(fields=['user', 'is_favorite']),
        ]

    def __str__(self):
        return f"{self.invitee_name} ({self.invitee_email})"
