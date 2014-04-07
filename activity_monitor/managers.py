import datetime

from django.db import models
from django.db.models import signals
from django.contrib.contenttypes.models import ContentType

from activity_monitor.signals import create_or_update

class ActivityItemManager(models.Manager):
    
    def __init__(self):
      super(models.Manager, self).__init__()
      self._set_creation_counter()
      self.model = None
      self._inherited = False 
      self.models_by_name = {}
      self._db = 'default'
      
    def remove_orphans(self, instance, **kwargs):
      """
      When an item is deleted, first delete any Activity object that has been created
      on its behalf.
      """
      from activity_monitor.models import Activity
      try:
        instance_content_type = ContentType.objects.get_for_model(instance)
        timeline_item = Activity.objects.get(content_type=instance_content_type, object_id=instance.pk)
        timeline_item.delete()
      except Activity.DoesNotExist:
        return
            
    def follow_model(self, model):
        """
        Follow a particular model class, updating associated Activity objects automatically.
        """
        if model:
          self.models_by_name[model.__name__.lower()] = model
          signals.post_save.connect(create_or_update, sender=model)
          signals.post_delete.connect(self.remove_orphans, sender=model)
        
    def get_for_model(self, model):
        """
        Return a QuerySet of only items of a certain type.
        """
        return self.filter(content_type=ContentType.objects.get_for_model(model))
        
    def get_last_update_of_model(self, model, **kwargs):
        """
        Return the last time a given model's items were updated. Returns the
        epoch if the items were never updated.
        """
        qs = self.get_for_model(model)
        if kwargs:
            qs = qs.filter(**kwargs)
        try:
            return qs.order_by('-timestamp')[0].timestamp
        except IndexError:
            return datetime.datetime.fromtimestamp(0)
