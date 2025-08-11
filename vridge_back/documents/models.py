from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project
import os

User = get_user_model()

class Document(models.Model):
    """  """
    
    CATEGORY_CHOICES = [
        ('contract', ''),
        ('planning', ''),
        ('script', ''),
        ('storyboard', ''),
        ('report', ''),
        ('reference', ''),
        ('other', ''),
    ]
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='documents',
        verbose_name=''
    )
    
    uploader = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name=''
    )
    
    filename = models.CharField(
        max_length=255,
        verbose_name=''
    )
    
    file = models.FileField(
        upload_to='documents/%Y/%m/%d/',
        verbose_name=''
    )
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name=''
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=''
    )
    
    size = models.BigIntegerField(
        default=0,
        verbose_name=' '
    )
    
    mime_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='MIME '
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=' '
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=' '
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=' '
    )
    
    download_count = models.IntegerField(
        default=0,
        verbose_name=' '
    )
    
    class Meta:
        verbose_name = ''
        verbose_name_plural = ''
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['project', 'category']),
            models.Index(fields=['uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.project.name} - {self.filename}"
    
    def save(self, *args, **kwargs):
        #    
        if self.file and not self.size:
            self.size = self.file.size
        
        # MIME   
        if self.file and not self.mime_type:
            import mimetypes
            self.mime_type = mimetypes.guess_type(self.file.name)[0] or 'application/octet-stream'
        
        super().save(*args, **kwargs)
    
    def get_file_extension(self):
        """  """
        return os.path.splitext(self.filename)[1].lower()
    
    def is_image(self):
        """  """
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']
        return self.get_file_extension() in image_extensions
    
    def is_pdf(self):
        """PDF  """
        return self.get_file_extension() == '.pdf'
    
    def increment_download_count(self):
        """  """
        self.download_count += 1
        self.save(update_fields=['download_count'])