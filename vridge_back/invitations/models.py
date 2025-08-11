from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project
from django.utils import timezone
from datetime import timedelta
import secrets

User = get_user_model()


class Invitation(models.Model):
    """초대 모델"""
    STATUS_CHOICES = [
        ('pending', '대기 중'),
        ('accepted', '수락됨'),
        ('declined', '거절됨'),
        ('cancelled', '취소됨'),
    ]
    
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_invitations',
        verbose_name="보낸 사람"
    )
    recipient_email = models.EmailField(verbose_name="받는 사람 이메일")
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_invitations',
        null=True,
        blank=True,
        verbose_name="프로젝트"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="상태"
    )
    message = models.TextField(blank=True, verbose_name="메시지")
    token = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        verbose_name = "초대"
        verbose_name_plural = "초대"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'status']),
            models.Index(fields=['recipient_email', 'status']),
            models.Index(fields=['token']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"{self.sender.email} -> {self.recipient_email} ({self.status})"


class TeamMember(models.Model):
    """팀 멤버 모델"""
    ROLE_CHOICES = [
        ('owner', '소유자'),
        ('admin', '관리자'),
        ('member', '멤버'),
        ('viewer', '뷰어'),
    ]
    
    STATUS_CHOICES = [
        ('active', '활성'),
        ('inactive', '비활성'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_memberships',
        verbose_name="사용자"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='team_members',
        verbose_name="프로젝트"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member',
        verbose_name="역할"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="상태"
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "팀 멤버"
        verbose_name_plural = "팀 멤버"
        unique_together = ['user', 'project']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.project.title} ({self.role})"


class Friend(models.Model):
    """친구 관계 모델"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friends',
        verbose_name="사용자"
    )
    friend = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friend_of',
        verbose_name="친구"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    last_interaction = models.DateTimeField(auto_now=True)
    projects_shared = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "친구"
        verbose_name_plural = "친구"
        unique_together = ['user', 'friend']
        ordering = ['-last_interaction']
    
    def __str__(self):
        return f"{self.user.email} - {self.friend.email}"
