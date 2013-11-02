from neomodel import StructuredNode, StructuredRel, RelationshipTo, RelationshipFrom, StringProperty, FloatProperty

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


## Relationship models ##
class NearRel(StructuredRel):
    pass


class ServesRel(StructuredRel):
    pass


## Node type models ##
class Restaurant(StructuredNode):
    """
    Metadata for all restaurant node assets

    Node Attributes:
        id: The UUID generated object(Object)
        name: The restaurant name(String)
        address: The restaurant address(String)
        phone: Phone numbers(comma separated values)
        timings: Restaurant timings(String)
        rating: Restaurant rating(String)
        latlon: Restaurant latlon(String, Comma separated values lat,lon)

    Relation Attributes:
        near: Outgoing relationship to subzone
        serves: Outgoing relationship to cuisine
    """

    id = StringProperty(unique_index=True, required=True)
    name = StringProperty(index=True, required=True)
    address = StringProperty()
    phone = StringProperty()
    timings = StringProperty()
    rating = StringProperty()
    lat = FloatProperty()
    lon = FloatProperty()

    near = RelationshipTo('Subzone', 'NEAR', model=NearRel)
    serves = RelationshipTo('Cuisine', 'SERVES', model=ServesRel)


class Subzone(StructuredNode):
    """
    Metadata for subzone node assets

    Node Attributes:
        name: Subzone name (String)
        latlon: Average latlon of restaurant in the subzone

    Relation Attributes:
        near: Receiving relationship from Restaurant
        serves: Outgoing relationship to Cuisine
    """

    name = StringProperty(unique_index=True, required=True)
    lat = FloatProperty()
    lon = FloatProperty()

    near = RelationshipFrom('Restaurant', 'NEAR', model=NearRel)
    serves = RelationshipTo('Cuisine', 'SERVES', model=ServesRel)


class Cuisine(StructuredNode):
    """
    Metadata for cuisine node assets

    Node Attributes:
        name: Cuisine name (String)
        subzone: Subzone to which the cuisine belongs to (String)

    Relation Attributes:
        serves: Receiving relationship from Restaurant and Subzone
    """

    name = StringProperty(index=True)
    subzone = StringProperty()

    serves = RelationshipFrom(['Restaurant', 'Subzone'], 'SERVES', model=ServesRel)
