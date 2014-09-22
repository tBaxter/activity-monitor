import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType


def create_or_update(sender, **kwargs):
    """
    Create or update an Activity Monitor item from some instance.
    """
    now = datetime.datetime.now()

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
    for activity_setting in settings.ACTIVITY_MONITOR_MODELS:
        this_app_label    = activity_setting['model'].split('.')[0]
        this_model_label  = activity_setting['model'].split('.')[1]
        this_content_type = ContentType.objects.get(app_label=this_app_label, model=this_model_label)

        if this_content_type == instance_content_type:
            # first, check to see if we even WANT to register this activity.
            # use the boolean 'check' field. Also, delete if needed.
            if 'check' in activity_setting:
                if getattr(instance, activity_setting['check']) is False:
                    if activity:
                        activity.delete()
                    return

            # does it use the default manager (objects) or a custom manager?
            try:
                manager = activity_setting['manager']
            except:
                manager  = 'objects'

            # what field denotes the activity time? created is default
            try:
                timestamp = getattr(instance, activity_setting['date_field'])
            except:
                timestamp = getattr(instance, 'created')

            # if the given time stamp is a daterather than datetime type,
            # normalize it out to a datetime
            if type(timestamp) == type(now):
                clean_timestamp = timestamp
            else:
                clean_timestamp = datetime.datetime.combine(timestamp, datetime.time())

           # Find a valid user object
            if 'user_field' in activity_setting:  # pull the user object from instance using user_field
                user = getattr(instance, activity_setting['user_field'])
            elif this_model_label == 'user' or this_model_label == 'profile':  # this IS auth.user or a Django 1.5 custom user
                user = instance
            else:  # we didn't specify a user, so it must be instance.user
                user = instance.user

            # BAIL-OUT CHECKS
            # Determine all the reasons we would want to bail out.
            # Make sure it's not a future item, like a future-published blog entry.
            if clean_timestamp > now:
                return
            # or some really old content that was just re-saved for some reason
            if clean_timestamp < (now - datetime.timedelta(days=3)):
                return
            # or there's not a user object
            if not user:
                return
            # or the user is god or staff, and we're filtering out, don't add to monitor
            if user.is_superuser and 'filter_superuser' in activity_setting:
                return
            if user.is_staff and 'filter_staff' in activity_setting:
                return

            # build a default string representation
            # note that each activity can get back to the object via get_absolute_url()
            verb = activity_setting.get('verb', None)
            override_string = activity_setting.get('override_string', None)


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

    if user and clean_timestamp and instance:
        if not activity:  # If the activity didn't already exist, create it.
            activity = Activity(
                actor          = user,
                content_type   = instance_content_type,
                object_id      = content_object.id,
                content_object = content_object,
                timestamp      = clean_timestamp,
                verb = verb,
                override_string = override_string,
            )
            activity.save()
        return activity
