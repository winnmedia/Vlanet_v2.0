from django.db import models
from . import managers


class TimeStampedModel(models.Model):

    """Time Stamped Model"""

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = managers.CustomModelManager()  # manager  model 

    class Meta:
        abstract = True

    # def __init__(self, *args, **kwargs):
    #     super(TimeStampedModel, self).__init__(*args, **kwargs)
    #     self._meta.get_field("created").editable = True
