"""
This script registers the models with the Moderation app
"""
from moderation import moderation
from moderation.moderator import GenericModerator
from .models import *
from .signals import *
from django.contrib.auth.models import User,Group

class Moderator(GenericModerator):
    fields_exclude=['updated','hits']
    visible_until_rejected=False
    auto_approve_for_superusers=True
    auto_approve_for_staff=True
    notify_user=False
    notify_moderator=False

    def is_auto_approve(self, obj, user):
        if obj.state == "raw":
            return self.reason('Not Submitted Yet !')
        g=Group.objects.get(name="Trusted Users")
        if g in user.groups.all():
            return self.reason('Trusted User !')
        super(Moderator, self).is_auto_approve(obj, user)

    def is_auto_reject(self, obj, user):
        g=Group.objects.get(name="Banned Users")
        if g in user.groups.all():
            return self.reason('Banned User !')
        super(Moderator, self).is_auto_approve(obj, user)

moderation.register(Tutorial,Moderator)
moderation.register(Snippet,Moderator)
moderation.register(Wiki,Moderator)
moderation.register(Blog,Moderator)
moderation.register(Announcement,Moderator)
moderation.register(News,Moderator)
moderation.register(Package,Moderator)
moderation.register(Event,Moderator)
moderation.register(EducationalResource,Moderator)