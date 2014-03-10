from django.db import models
from django.contrib.auth.models import User
from social.apps.django_app.default.models import UserSocialAuth
import mongoengine as me
from datetime import datetime, timedelta

#Common Fields for all models
class Fields(object):
    name = me.StringField(max_length=30)
    latlon =  me.ListField(me.StringField(max_length=20))
    rating = me.StringField(max_length=2)
    subzone = me.StringField(max_length=20)
    timings = me.StringField(max_length=30)
    phone = me.StringField(max_length=40)
    cuisines = me.ListField(me.StringField(max_length=10))
    address = me.StringField(max_length=50)
    cost = me.StringField(max_length=30)


## Data warehouse mongo engine model ##
class Items(Fields, me.Document):

    highlights = me.ListField(me.StringField(max_length=20))
    highlights_not = me.ListField(me.StringField(max_length=20))
    tags = me.ListField(me.StringField(max_length=20))
    url = me.StringField(max_length=200)

    meta = {'collection':'items'}

#Static restaurant data model
class RestaurantStatic(me.Document, Fields):

    id = me.StringField(primary_key=True)
    last_edited = me.DateTimeField(required=True)
    auth_phone = me.StringField(max_length=10, help_text="Phone number of Restaurant manager for Two-Factor auth purposes")
    features = me.ListField(me.StringField(max_length=20), default=[])

    meta = {
        'collection':'RestaurantStatic',
        'indexes': ['id', 'name']
    }

    def save(self, *args, **kwargs):

        if isinstance(self.phone, int):
            self.phone = None

        self.last_edited = datetime.utcnow() + timedelta(hours=5, minutes=30)

        super(RestaurantStatic, self).save(*args, **kwargs)


#POSTGRES model
class FriendData(models.Model):
    """
    This model contains information detailing friends. Who is whos friend
    """

    id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(User, related_name='frienddata_uid')
    friend_id = models.ForeignKey(User, related_name='frienddata_friend_id')

    class Meta:
        unique_together = (("uid", "friend_id"),)