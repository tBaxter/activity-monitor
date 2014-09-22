import datetime

from collections import OrderedDict


def group_activities(queryset):
    """
    Given a queryset of activity objects, will group them by actors and return an OrderedDict including:

    item: The original target item being acted upon (activity.content_object)
    actors: a list of all actors who have acted upon the target.
    actor_count: zero-indexed count of actors. Useful for "Joe and {{ actor_count }} others have..."
    verb: the item's verb string, to avoid extra lookups
    last_modified: the time the target was last acted upon.

    The string version of the target is also available as the dict key.
    """
    actions = OrderedDict()
    for item in queryset:
        # current is defined as within the past day.
        if item.timestamp >= datetime.datetime.now() - datetime.timedelta(days=1):
            current_item = True
        else:
            current_item = False
        if item.target not in actions.keys():
            actions[item.target] = {
                'item': item,
                'actors': [item.actor_name],
                'actor_count': 0,
                'verb': item.override_string if item.override_string else item.verb,
                'last_modified': item.timestamp,
                'current_item': current_item
            }
        else: # item was previously added, but we need to update attributes
            if item.actor_name not in actions[item.target]['actors']:
                actions[item.target]['actors'].append(item.actor_name)
                actions[item.target]['actor_count'] += 1
            if actions[item.target]['last_modified'] < item.timestamp:
                actions[item.target]['last_modified'] = item.timestamp

    return actions
