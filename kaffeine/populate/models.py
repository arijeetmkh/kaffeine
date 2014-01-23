import mongoengine as me
from . import feature_list
import pdb


class Fields(object):
    name = me.StringField()
    latlon =  me.ListField()
    rating = me.StringField()
    subzone = me.StringField()
    timings = me.StringField()
    phone = me.StringField()
    url = me.StringField()
    cuisines = me.ListField()
    address = me.StringField()
    cost = me.StringField()


## Data warehouse mongo engine model ##
class Items(Fields, me.Document):

    highlights = me.ListField()
    highlights_not = me.ListField()
    tags = me.ListField()

    meta = {'collection':'items'}


class RestaurantStatic(me.Document, Fields):

    id = me.StringField(primary_key=True)

    features = me.ListField(default=[])

    meta = {
        'collection':'RestaurantStatic',
        'indexes': ['name']
    }

    def save(self, *args, **kwargs):

        if isinstance(self.phone, int):
            self.phone = None

        super(RestaurantStatic, self).save(*args, **kwargs)