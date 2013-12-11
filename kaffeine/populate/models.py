import mongoengine as me

## Data warehouse mongo engine model ##
class Items(me.Document):

    name = me.StringField()
    latlon =  me.ListField()
    rating = me.StringField()
    subzone = me.StringField()
    tags = me.ListField()
    timings = me.StringField()
    phone = me.StringField()
    highlights = me.ListField()
    highlights_not = me.ListField()
    url = me.StringField()
    cuisines = me.ListField()
    address = me.StringField()
    cost = me.StringField()


    meta = {'collection':'items'}


class RestaurantStatic(me.Document):

    id = me.StringField(primary_key=True)
    name = me.StringField()
    timings = me.StringField()
    phone = me.StringField()
    cost = me.StringField()
    address = me.StringField()

    meta = {
        'collection':'RestaurantStatic',
        'indexes': ['name']
    }

    def save(self, *args, **kwargs):

        if isinstance(self.phone, int):
            self.phone = None

        super(RestaurantStatic, self).save(*args, **kwargs)
