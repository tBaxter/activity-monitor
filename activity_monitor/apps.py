from django.apps import AppConfig
from django.db.models.signals import post_migrate

def register_app_activity():
    """
    Create watchers for models defined in settings.py.
    Once created, they will be passed over
    Activity.objects.follow_model(), which lives in managers.py
    """
    from django.conf import settings
    from django.contrib.contenttypes.models import ContentType

    from .models import Activity

    # TO-DO: Add check for existence of setting
    if not hasattr(settings, 'ACTIVITY_MONITOR_MODELS'):
        return

    for item in settings.ACTIVITY_MONITOR_MODELS:
        try:
            app_label, model = item['model'].split('.', 1)
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            model = content_type.model_class()
            Activity.objects.follow_model(model)

        except ContentType.DoesNotExist:
            pass


class ActivityMonitorConfig(AppConfig):
    name = 'activity_monitor'
    verbose_name = "Activity Monitor"

    def setup(self):
        register_app_activity()
