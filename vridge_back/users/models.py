import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from core import managers, models as core_model


class User(AbstractUser):
    LOGIN_CHOICES = (
        ("email", "Email"),
        ("google", "Google"),
        ("kakao", "Kakao"),
        ("naver", "Naver"),
    )

    nickname = models.CharField(verbose_name="", max_length=100, blank=True)
    login_method = models.CharField(
        max_length=50, verbose_name=" ", choices=LOGIN_CHOICES, default="email"
    )
    email_secret = models.CharField(verbose_name=" ()", max_length=10, null=True, blank=True)
    email_verified = models.BooleanField(default=False, verbose_name="  ")
    email_verified_at = models.DateTimeField(null=True, blank=True, verbose_name="   ")
    
    # Soft delete  
    is_deleted = models.BooleanField(default=False, verbose_name=" ")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=" ")
    deletion_reason = models.CharField(
        max_length=200, null=True, blank=True, default='', verbose_name=" "
    )
    
    #   
    can_recover = models.BooleanField(default=True, verbose_name="  ")
    recovery_deadline = models.DateTimeField(null=True, blank=True, verbose_name=" ")
    
    objects = managers.CustomUserManager()

    class Meta:
        verbose_name = ""
        verbose_name_plural = ""
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['login_method']),
            models.Index(fields=['is_deleted', 'deleted_at']),
        ]
    
    def soft_delete(self, reason=" "):
        """   """
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deletion_reason = reason
        #    (30)
        self.recovery_deadline = timezone.now() + timezone.timedelta(days=30)
        self.is_active = False
        self.save()
    
    def restore_account(self):
        """ """
        self.is_deleted = False
        self.deleted_at = None
        self.deletion_reason = None
        self.recovery_deadline = None
        self.is_active = True
        self.save()
    
    def can_be_recovered(self):
        """  """
        if not self.is_deleted or not self.can_recover:
            return False
        if self.recovery_deadline:
            from django.utils import timezone
            return timezone.now() <= self.recovery_deadline
        return True


class UserProfile(core_model.TimeStampedModel):
    """  """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name=""
    )
    profile_image = models.ImageField(
        verbose_name=" ", 
        upload_to="profile_images/", 
        null=True, 
        blank=True
    )
    bio = models.TextField(verbose_name="", max_length=500, blank=True)
    phone = models.CharField(verbose_name="", max_length=20, blank=True)
    company = models.CharField(verbose_name="/", max_length=100, blank=True)
    position = models.CharField(verbose_name="", max_length=100, blank=True)
    
    class Meta:
        verbose_name = " "
        verbose_name_plural = " "
    
    def __str__(self):
        return f"{self.user.username} "


class EmailVerify(core_model.TimeStampedModel):
    email = models.CharField(verbose_name=" ", max_length=200)
    auth_number = models.CharField(verbose_name="", max_length=10)

    def __str__(self):
        return f"{self.email} - {self.auth_number}"

    class Meta:
        verbose_name = " "
        verbose_name_plural = " "


class EmailVerificationToken(core_model.TimeStampedModel):
    """   """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="verification_tokens",
        verbose_name=""
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name=" "
    )
    email = models.EmailField(verbose_name=" ")
    is_verified = models.BooleanField(default=False, verbose_name="  ")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="  ")
    expires_at = models.DateTimeField(verbose_name=" ")
    
    class Meta:
        verbose_name = "  "
        verbose_name_plural = "  "
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['email', 'is_verified']),
        ]
    
    def __str__(self):
        return f"{self.email} - {'' if self.is_verified else ''}"
    
    def is_expired(self):
        """  """
        from django.utils import timezone
        return timezone.now() > self.expires_at


class UserMemo(core_model.TimeStampedModel):
    user = models.ForeignKey(
        "User", related_name="memos", on_delete=models.CASCADE, verbose_name="", null=True, blank=True
    )
    date = models.DateField(verbose_name="", null=True)
    memo = models.TextField(verbose_name="", null=True, blank=False)

    class Meta:
        verbose_name = " "
        verbose_name_plural = " "

    def __str__(self):
        return self.user.nickname


class Notification(core_model.TimeStampedModel):
    """  """
    NOTIFICATION_TYPES = [
        ('invitation_received', ' '),
        ('invitation_accepted', ' '),
        ('invitation_declined', ' '),
        ('project_member_added', '   '),
        ('feedback_added', '  '),
        ('project_updated', ' '),
        ('system', ' '),
    ]
    
    recipient = models.ForeignKey(
        "User",
        related_name="notifications",
        on_delete=models.CASCADE,
        verbose_name=""
    )
    
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        verbose_name=" "
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=" "
    )
    
    message = models.TextField(
        verbose_name=" "
    )
    
    #   ()
    project_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="  ID"
    )
    
    invitation_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="  ID"
    )
    
    #  
    is_read = models.BooleanField(
        default=False,
        verbose_name=" "
    )
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=" "
    )
    
    #   (JSON)
    extra_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=" "
    )

    class Meta:
        verbose_name = ""
        verbose_name_plural = ""
        ordering = ['-created']
        indexes = [
            models.Index(fields=['recipient', '-created']),
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"


class Friendship(core_model.TimeStampedModel):
    """  """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friendships",
        verbose_name=""
    )
    friend = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friend_of",
        verbose_name=""
    )
    
    STATUS_CHOICES = [
        ('pending', ''),
        ('accepted', ''),
        ('declined', ''),
        ('blocked', ''),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=""
    )
    
    #    
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_friend_requests",
        verbose_name=""
    )
    
    # / 
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name=" ")
    
    class Meta:
        unique_together = [['user', 'friend']]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['friend', 'status']),
        ]
        verbose_name = " "
        verbose_name_plural = " "
    
    def __str__(self):
        return f"{self.user.email} - {self.friend.email} ({self.get_status_display()})"


class RecentInvitation(core_model.TimeStampedModel):
    """   """
    inviter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recent_invitations",
        verbose_name=""
    )
    invitee_email = models.EmailField(verbose_name="  ")
    invitee_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="  ")
    project_name = models.CharField(max_length=200, verbose_name="")
    
    #   (     )
    invitation_count = models.PositiveIntegerField(default=1, verbose_name=" ")
    last_invited_at = models.DateTimeField(auto_now=True, verbose_name="  ")
    
    class Meta:
        unique_together = [['inviter', 'invitee_email']]
        ordering = ['-last_invited_at']
        verbose_name = " "
        verbose_name_plural = " "
    
    def __str__(self):
        return f"{self.inviter.email} -> {self.invitee_email} ({self.invitation_count})"
