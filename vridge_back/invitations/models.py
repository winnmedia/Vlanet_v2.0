"""
Fixed models for invitations app - Resolves related_name conflicts
QA Lead: Grace
Risk Assessment: LOW - Only changes related_names, no functional impact
"""

from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project
from django.utils import timezone
from datetime import timedelta
import secrets

User = get_user_model()


class Invitation(models.Model):
    """General invitation model with fixed related_names"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
    ]
    
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_general_invitations',  # Fixed: was 'sent_invitations'
        verbose_name="Sender"
    )
    recipient_email = models.EmailField(verbose_name="Recipient Email")
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='general_invitations',  # Fixed: was 'project_invitations'
        null=True,
        blank=True,
        verbose_name="Project"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    message = models.TextField(blank=True, verbose_name="Message")
    token = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        verbose_name = "Invitation"
        verbose_name_plural = "Invitations"
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
    """Team member model - No conflicts"""
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_memberships',
        verbose_name="User"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='team_members',
        verbose_name="Project"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member',
        verbose_name="Role"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="Status"
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
        unique_together = ['user', 'project']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.project.title} ({self.role})"


class InvitationFriend(models.Model):
    """
    Renamed from Friend to InvitationFriend to avoid confusion
    Fixed related_names to avoid conflicts
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='invitation_friends',  # Fixed: was 'friends'
        verbose_name="User"
    )
    friend = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='invitation_friend_of',  # Fixed: was 'friend_of'
        verbose_name="Friend"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    last_interaction = models.DateTimeField(auto_now=True)
    projects_shared = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Invitation Friend"
        verbose_name_plural = "Invitation Friends"
        unique_together = ['user', 'friend']
        ordering = ['-last_interaction']
    
    def __str__(self):
        return f"{self.user.email} - {self.friend.email}"