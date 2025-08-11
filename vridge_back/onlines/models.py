from django.db import models
from core.models import TimeStampedModel


class OnlineVideo(TimeStampedModel):
    link = models.TextField(verbose_name="", null=True, blank=False)

    class Meta:
        verbose_name = " "
        verbose_name_plural = " "
        ordering = ("-created",)

    def __str__(self):
        return " ."
