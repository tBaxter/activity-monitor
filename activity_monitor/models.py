from django.contrib.auth import get_user_model
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .managers import ActivityItemManager


class Activity(models.Model):
    actor = models.ForeignKey(get_user_model(), related_name="timeline_items")
    verb = models.CharField(blank=True, max_length=255)
    timestamp = models.DateTimeField()

    content_object      = GenericForeignKey()
    content_type        = models.ForeignKey(ContentType)
    object_id           = models.PositiveIntegerField()
    
    objects             = ActivityItemManager()

    class Meta:
        ordering            = ['-timestamp']
        unique_together     = [('content_type', 'object_id')]
        get_latest_by       = 'timestamp'
        verbose_name_plural = 'activities'

    def __unicode__(self):
        return "%s: %s" % (self.content_type.model_class().__name__, unicode(self.content_object))

    def get_absolute_url(self):
        """ 
        Use original content object's 
        get_absolute_url method.
        """
        return self.content_object.get_absolute_url()
