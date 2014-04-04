from django.conf import settings
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from activity_monitor.managers import ActivityItemManager

UserModel = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class Activity(models.Model):
    user                = models.ForeignKey(UserModel, related_name="timeline_items")
    content_type        = models.ForeignKey(ContentType)
    object_id           = models.PositiveIntegerField()
    content_object      = GenericForeignKey()
    timestamp           = models.DateTimeField()
    default_string      = models.CharField(blank=True, max_length=255)

    objects             = ActivityItemManager()

    class Meta:
        ordering            = ['-timestamp']
        unique_together     = [('content_type', 'object_id')]
        get_latest_by       = 'timestamp'
        verbose_name_plural = 'activities'

    def __unicode__(self):
        return "%s: %s" % (self.content_type.model_class().__name__, unicode(self.content_object))

    def get_absolute_url(self):
        """ Call get_absolute_url method of this object's original content object. """
        return self.content_object.get_absolute_url()

    def save(self, force_insert=False, force_update=False):
        super(Activity, self).save(force_insert=force_insert, force_update=force_update)
