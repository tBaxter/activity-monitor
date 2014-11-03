# Try/except to catch 1.7 (has AppConfig) or earlier.
try:
    from django.apps import AppConfig
    default_app_config = 'activity_monitor.apps.ActivityMonitorConfig'
except ImportError:
    from activity_monitor.models import register_app_activity
    register_app_activity()
