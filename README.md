# Activity monitor

A sort of tumblelog-y activity feed thing heavily based on other people's work. I'd credit them if I could remember where I got this stuff.

This is *so* untested....

--------

Models you wish to monitor should be registered in your settings.py:

Example:

    ACTIVITY_MONITOR_MODELS = (
      {'model': 'comments.comment',      # Required: the model to watch, in app_label.model format.
        'date_field': 'post_date',     # Optional: the datetime field to watch. Defaults to "created"
        'user_field': 'submitted_by',    # Optional: a related user to watch
        'verb':  "commented on",         # The default verb string to be recorded.
        'check': 'approved',             # Optional: a boolean field that must be true for the activity to register
        'manager': 'SoftDeleteManager'   # Optional: if there is a custom manager, you can use it. If not, defaults to "objects"
       },
     {
        'model': 'djangoratings.vote',
        'date_field': 'date_added',
      },
     {
        'model': 'auth.user',
        'date_field': 'date_joined',
        'check': 'is_active',
      }, 
    )


In the absence of 'user_field', it will assume 'user' is the user.

--------

### About the settings
`Model` is required: it lets Activity Monitor know which models to watch. All models should be registered as `app_label.model`.


`date_field` says when the activity happened -- when the new thing was created or updated. If undefined, Activity Monitor will look for a "created" field. Failing that, it will use the current time.  

`user_field` tells what field the actor can be found in. If undefined, Activity Monitor will look for a 'user' field. If no user field is found at all, Activity Monitor will fall back to request.user. The result is stored as "actor" on the activity.

`verb` is the verb string to use. By default, strings will be output as "{actor} {verb} {model.__unicode__()}", or "Joe Cool commented on '10 reasons beagles are awesome.'"

`override_string` overrides the normal output altogether.

`check` allows you to say, "Make sure this boolean is true on the object before adding the activity." For example, you wouldn't want any activities registering on unpublished blog posts, so you would check against the "published" field. If this field is false for the activity, no activity is registered.

`manager` allows passing a custom manager to be used. Defaults to `objects`.

`filter_superuser` suppresses registering activities if a superuser performed them. Useful if the superuser's changes should go unnoted, particularly if you're watching for updates.

`filter_staff` suppresses registering activities if a staff member performed them. Like `filter_superuser`, this is useful if the changes should go unnoted, particularly if you're watching for updates.



### What happens when the settings are defined

Once the settings are defined, the models are passed to follow_model() in activity_monitor.managers, which will send a signal on object creation or deletion.

When an object is created or deleted, the signal is sent and an activity object is created with the object, 
the user and the time of the event.

This is done in activity_monitor.signals.create_or_update, which does the bulk of the work. Among other things, it:

* Uses the "check" field to determine if an object should or shouldn't be shown.  
* Checks if the user is superuser. If so, you don't want to show it in the user activity monitor.  
* Sorts out user field and determines a valid user object.  
* Checks if the object has a future timestamp (such as future-published blog entries) before adding.  
* Throws away activities if the related object is deleted or otherwise removed.  
* Makes sure the activity does not already exist.  
* Saves who did it (actor), what they did, what they did it to, and when. 

To minimize queries, you can access the related user via 'actor', or just a unicode representation of their name with 'actor_name'. Similarly the target object is available as 'content_object', but a simple unicode representation is available as "target"

### Simple Output
Activity monitor supports several ways to output the activities.
* You can have a simple chronological list
* You can group activities by the target being acted on. In this case, output would be something like "Joe Cool and Conrad commented on Woodstock."

### Customizing output
You can define also define custom template snippets for the target content object. In this case, the template should live in `/templates/activity_monitor/includes/models/applabel_modelname.html`. An example is included. 

You do not have to define all your content types. If you do not, activity monitor will safely fall back on a default output.

**NOTE**: Loading these custom templates can lead to more database queries than you'd like. Custom templates should be used sparingly, and if you have a lot of them, you should at least cache the results.
