Models you wish to monitor should be registered in your settings.py:

Example:

    ACTIVITY_MONITOR_MODELS = (
      {'model': 'comments.comment',      # Required: the model to watch.
        'date_field': 'submit_date',     # Optional: the datetime field to watch. Defaults to "created"
        'user_field': 'submitted_by',    # Optional: a related user to watch
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

In the absence of either 'user_field', it will assume 'user' is the user.

--------

Once the settings are defined, the models are passed to follow_model() in activity_monitor.managers, which will send a signal on object creation or deletion.

When an object is created or deleted, the signal is sent and an activity object is created with the object, 
the user and the time of the event.

This is done in activity_monitor.signals.create_or_update, which does the bulk of the work. Among other things, it:
	* Uses the "check" field to determine if an object should or shouldn't be shown
	* Checks if the user is superuser. If so, you don't want to show it in the user activity monitor.
	* Sorts out user field, profile field, etc. and determines a valid user object
	* Checks if the object has a future timestamp (such as future-published blog entries) before adding
	* Throws away activities if the related object is deleted or otherwise removed.
	* Makes sure the activity does not already exist.
	* Saves who did it, what they did it to, and when
