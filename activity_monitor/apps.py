from django.apps import AppConfig

from activity_monitor import register_app_activity

class ActivityMonitorConfig(AppConfig):
    name = 'activity_monitor'
    verbose_name = "Activity_Monitor"

    def ready(self):
        register_app_activity()
