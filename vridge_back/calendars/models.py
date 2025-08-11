from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project

User = get_user_model()


class CalendarEvent(models.Model):
    """  """
    title = models.CharField(max_length=200, verbose_name="")
    description = models.TextField(blank=True, verbose_name="")
    date = models.DateField(verbose_name="")
    time = models.TimeField(verbose_name="")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='calendar_events',
        verbose_name=""
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='calendar_events',
        null=True,
        blank=True,
        verbose_name=""
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = " "
        verbose_name_plural = " "
        ordering = ['-date', '-time']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['project', 'date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.date} {self.time}"
