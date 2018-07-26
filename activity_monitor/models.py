from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import cached_property

from .managers import ActivityItemManager


class Activity(models.Model):
    """
    Stores an action that occurred that is being tracked
    according to ACTIVITY_MONITOR settings.
    """
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="subject",
        on_delete="CASCADE"
    )
    timestamp = models.DateTimeField()

    verb = models.CharField(blank=True, null=True, max_length=255, editable=False)
    override_string = models.CharField(blank=True, null=True, max_length=255, editable=False)

    target = models.CharField(blank=True, null=True, max_length=255, editable=False)
    actor_name = models.CharField(blank=True, null=True, max_length=255, editable=False)

    content_object = GenericForeignKey()
    content_type = models.ForeignKey(ContentType, on_delete="CASCADE")
    object_id = models.PositiveIntegerField()

    objects = ActivityItemManager()

    class Meta:
        ordering = ['-timestamp']
        unique_together = [('content_type', 'object_id')]
        get_latest_by = 'timestamp'
        verbose_name_plural = 'actions'

    def __unicode__(self):
        return "{0}: {1}".format(self.content_type.model_class().__name__, self.content_object)

    def save(self, *args, **kwargs):
        """
        Store a string representation of content_object as target
        and actor name for fast retrieval and sorting.
        """
        if not self.target:
            self.target = str(self.content_object)
        if not self.actor_name:
            self.actor_name = str(self.actor)
        super(Activity, self).save()

    def get_absolute_url(self):
        """
        Use original content object's
        get_absolute_url method.
        """
        return self.content_object.get_absolute_url()

    @cached_property
    def short_action_string(self):
        """
        Returns string with actor and verb, allowing target/object
        to be filled in manually.

        Example:
        [actor] [verb] or
        "Joe cool posted a comment"
        """
        output = "{0} ".format(self.actor)
        if self.override_string:
            output += self.override_string
        else:
            output += self.verb
        return output

    @cached_property
    def full_action_string(self):
        """
        Returns full string with actor, verb and target content object.

        Example:
        [actor] [verb] [content object/target] or
        Joe cool posted a new topic: "my new topic"
        """
        output = "{} {}".format(self.short_action_string, self.content_object)
        return output

    @cached_property
    def image(self):
        """
        Attempts to provide a representative image from a content_object based on
        the content object's get_image() method.

        If there is a another content.object, as in the case of comments and other GFKs,
        then it will follow to that content_object and then get the image.

        Requires get_image() to be defined on the related model even if it just
        returns object.image, to avoid bringing back images you may not want.

        Note that this expects the image only. Anything related (caption, etc) should be stripped.

        """
        obj = self.content_object
        # First, try to get from a get_image() helper method
        try:
            image = obj.get_image()
        except AttributeError:
            try:
                image = obj.content_object.get_image()
            except:
                image = None

        # if we didn't find one, try to get it from foo.image
        # This allows get_image to take precedence for greater control.
        if not image:
            try:
                image = obj.image
            except AttributeError:
                try:
                    image = obj.content_object.image
                except:
                    return None

        # Finally, ensure we're getting an image, not an image object
        # with caption and byline and other things.
        try:
            return image.image
        except AttributeError:
            return image
