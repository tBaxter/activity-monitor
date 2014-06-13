from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import CommandError
from django.core.management.base import BaseCommand
        
class Command(BaseCommand):
    help = "Registers existing content for a new installation of the timelines app."

    def handle(self, **kwargs):
      """
      Simply re-saves all objects from models listed in settings.TIMELINE_MODELS. Since the timeline
      app is now following these models, it will register each item as it is re-saved. The purpose of this
      script is to register content in your database that existed prior to installing the timeline app.
      """
      for item in settings.TIMELINES_MODELS:
        app_label     = item['model'].split('.')[0]
        model         = item['model'].split('.')[1]
        content_type  = ContentType.objects.get(app_label=app_label, model=model)
        model         = content_type.model_class()
        #print "Resaving all " + unicode(content_type) + " objects."
        objects = model.objects.all()
        for object in objects:
          try:
            object.save()
          except:
            pass