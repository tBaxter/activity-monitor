from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from activity_monitor.models import Activity

"""
Create watchers for models defined in settings.py. Once created, they will be passed over
Activity.objects.follow_model(), which lives in manager.py
"""

for item in settings.ACTIVITY_MONITOR_MODELS:
  try:
    app_label     = item['model'].split('.')[0]
    model         = item['model'].split('.')[1]
    content_type  = ContentType.objects.get(app_label=app_label, model=model)
    model         = content_type.model_class()
    Activity.objects.follow_model(model)
  
  except ContentType.DoesNotExist:
    pass