from django.contrib import admin

from activity_monitor.models import Activity


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'user', 'content_type', 'timestamp')

admin.site.register(Activity, ActivityAdmin)
