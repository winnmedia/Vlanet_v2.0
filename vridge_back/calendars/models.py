from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project

User = get_user_model()


class CalendarEvent(models.Model):
    """캘린더 이벤트 모델"""
    title = models.CharField(max_length=200, verbose_name="제목")
    description = models.TextField(blank=True, verbose_name="설명")
    date = models.DateField(verbose_name="날짜")
    time = models.TimeField(verbose_name="시간")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='calendar_events',
        verbose_name="사용자"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='calendar_events',
        null=True,
        blank=True,
        verbose_name="프로젝트"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "캘린더 이벤트"
        verbose_name_plural = "캘린더 이벤트"
        ordering = ['-date', '-time']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['project', 'date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.date} {self.time}"
