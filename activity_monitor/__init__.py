# Try/except to catch 1.7 (has AppConfig) or earlier.
try:
    from django.apps import AppConfig
    default_app_config = 'activity_monitor.apps.ActivityMonitorConfig'
except ImportError:
<<<<<<< HEAD
    from activity_monitor.models import register_app_activity
=======
    from . apps import register_app_activity
>>>>>>> parent of 06c03d4... let's get explicit
    register_app_activity()
