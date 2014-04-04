import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType


now = datetime.datetime.now()
offset = now - datetime.timedelta(days=3)


#def create_or_update(self, instance, timestamp=None, **kwargs):
def create_or_update(sender, **kwargs):
    """
    Create or update an Activity Monitor item from some instance.
    """
    # I can't explain why this import fails unless it's here.
    from activity_monitor.models import Activity
    instance = kwargs['instance']

    # Find this object's content type and model class.
    instance_content_type = ContentType.objects.get_for_model(sender)
    instance_model        = sender
    content_object        = instance_model.objects.get(id=instance.id)

    # check to see if the activity already exists. Will need later.
    try:
        activity = Activity.objects.get(content_type=instance_content_type, object_id=content_object.id)
    except:
        activity = None

    # We now know the content type, the model (sender), content type and content object.
    # We need to loop through ACTIVITY_MONITOR_MODELS in settings for other fields

    for item in settings.ACTIVITY_MONITOR_MODELS:
        this_app_label    = item['model'].split('.')[0]
        this_model_label  = item['model'].split('.')[1]
        this_content_type = ContentType.objects.get(app_label=this_app_label, model=this_model_label)

        if this_content_type == instance_content_type:
            # first, check to see if we even WANT to register this activity.
            # use the boolean 'check' field. Also, delete if needed.
            if 'check' in item:
                if getattr(instance, item['check']) is False:
                    if activity:
                        activity.delete()
                    return

            # does it use the default manager (objects) or a custom manager?
            try:
                manager = item['manager']
            except:
                manager  = 'objects'

            # what field denotes the activity time? created is default
            try:
                timestamp = getattr(instance, item['date_field'])
            except:
                timestamp = getattr(instance, 'created')

            if type(timestamp) == type(now):  # they're both datetimes
                timestamp_check = timestamp
            else:
                timestamp_check = datetime.datetime.combine(timestamp, datetime.time())

            # Make sure it's not a future item, like a future-published blog entry.
            if timestamp_check > datetime.datetime.now():
                return
            if timestamp_check < offset:
                return

            # Find a valid user object
            if 'user_field' in item:  # pull the user object from instance using user_field
                user = getattr(instance, item['user_field'])
            elif this_model_label == 'user' or this_model_label == 'profile':  # this IS auth.user or a Django 1.5 custom user
                user = instance
            else:  # we didn't specify a user, so it must be instance.user
                user = instance.user
                if not user:
                    return

            #if the user is god, don't add to monitor
            if user.is_superuser:
                return

            # build a default string representation
            # note that each activity can get back to the object via get_absolute_url()
            default = ''
            if 'default_string' in item:
                try:
                    default = user.preferred_name + item['default_string']
                except:
                    default = unicode(user) + item['default_string']
                # for votes, comments and other items that refer to a third object
                try:
                    default += unicode(instance.content_object)
                except:
                    default += unicode(instance)

    # MANAGER CHECK
    # Make sure the item "should" be registered, based on the manager argument.
    # If InstanceModel.manager.all() includes this item, then register. Otherwise, return.
    # Also, check to see if it should be deleted.
    try:
        getattr(instance_model, manager).get(pk=instance.pk)
    except instance_model.DoesNotExist:
        try:
            activity.delete()
            return
        except Activity.DoesNotExist:
            return

    if user and timestamp and instance:
        if not activity:  # If the activity didn't already exist, create it.
            activity = Activity(
                user           = user,
                content_type   = instance_content_type,
                object_id      = content_object.id,
                content_object = content_object,
                timestamp      = timestamp,
                default_string = default,
            )
            activity.save()
        return activity
