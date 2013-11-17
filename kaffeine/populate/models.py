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


class HasFeature(StructuredRel):
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
        restaurant_near_subzone: Outgoing relationship to subzone
        restaurant_serves_cuisine: Outgoing relationship to cuisine
    """

    id = StringProperty(unique_index=True, required=True)
    name = StringProperty(index=True, required=True)
    address = StringProperty()
    phone = StringProperty()
    timings = StringProperty()
    rating = StringProperty()
    lat = FloatProperty()
    lon = FloatProperty()

    restaurant_near_subzone = RelationshipTo('Subzone', 'NEAR', model=NearRel)
    restaurant_serves_cuisine = RelationshipTo('Cuisine', 'SERVES', model=ServesRel)
    restaurant_has_feature = RelationshipTo('Feature', 'HAS', model=HasFeature)


class Subzone(StructuredNode):
    """
    Metadata for subzone node assets

    Node Attributes:
        name: Subzone name (String)
        latlon: Average latlon of restaurant in the subzone

    Relation Attributes:
        subzone_near_restaurant: Receiving relationship from Restaurant
        subzone_serves_cuisine: Outgoing relationship to Cuisine
        subzone_has_features: Outgoing relationship to Feature
    """

    name = StringProperty(unique_index=True, required=True)
    lat = FloatProperty()
    lon = FloatProperty()

    subzone_near_restaurant = RelationshipFrom('Restaurant', 'NEAR', model=NearRel)
    subzone_serves_cuisine = RelationshipTo('Cuisine', 'SERVES', model=ServesRel)
    subzone_has_feature = RelationshipTo('Feature', 'HAS', model=HasFeature)


class Cuisine(StructuredNode):
    """
    Metadata for cuisine node assets

    Node Attributes:
        name: Cuisine name (String)
        subzone: Subzone to which the cuisine belongs to (String)

    Relation Attributes:
        cuisine_serves: Receiving relationship from Restaurant and Subzone
    """

    name = StringProperty(index=True)
    subzone = StringProperty()

    cuisine_serves = RelationshipFrom(['Restaurant', 'Subzone'], 'SERVES', model=ServesRel)


## Fearure Models (Self explanatory) ##
class Feature(StructuredNode):
    """
    Metadata for Features
    All relationships have common model available HasFeature

    Node Attributes:
        name: Feature name (String)

    Relation Attributes:
        feature_has_subzone: Receiving relationship from Subzone
        feature_has_restaurant: Receiving relationship from Restaurant
    """
    name = StringProperty(index=True)
    subzone = StringProperty()

    feature_has_subzone = RelationshipFrom('Subzone', 'HAS', model=HasFeature)
    feature_has_restaurant = RelationshipFrom('Restaurant', 'HAS', model=HasFeature)

# ########### BELOW CODE RECENTLY REMOVED. KEEP FOR NOW JUST IN CASE ################
# class Bar(StructuredNode):
#     """
#     Metadata for Bar Feature
#     All relationships have common model available HasFeature
#
#     Relation Attributes:
#         subzone_has_bar: Receiving relationship from Subzone
#         restaurant_has_bar: Receiving relationship from Restaurant
#     """
#     subzone_has_bar = RelationshipFrom('Subzone', 'HAS', model=HasFeature)
#     restaurant_has_bar = RelationshipFrom('Restaurant', 'HAS', model=HasFeature)
#
#
# class DineIn(StructuredNode):
#     """
#     Metadata for DineIn Feature
#
#     All relationships have common model available HasFeature
#
#     Relation Attributes:
#         subzone_has_dinein: Receiving relationship from Subzone
#         restaurant_has_dinein: Receiving relationship from Restaurant
#     """
#     subzone_has_dinein = RelationshipFrom('Subzone', 'HAS', model=HasFeature)
#     restaurant_has_dinein = RelationshipFrom('Restaurant', 'HAS', model=HasFeature)
#
#
# class HomeDelivery(StructuredNode):
#     """
#     Metadata for HomeDelivery Feature
#
#     All relationships have common model available HasFeature
#
#     Relation Attributes:
#         subzone_has_homedelivery: Receiving relationship from Subzone
#         restaurant_has_homedelivery: Receiving relationship from Restaurant
#     """
#     subzone_has_homedelivery = RelationshipFrom('Subzone', 'HAS', model=HasFeature)
#     restaurant_has_homedelivery = RelationshipFrom('Restaurant', 'HAS', model=HasFeature)
#
#
# class NonVeg(StructuredNode):
#     """
#     Metadata for NonVeg Feature
#
#     All relationships have common model available HasFeature
#
#     Relation Attributes:
#         subzone_has_nonveg: Receiving relationship from Subzone
#         restaurant_has_nonveg: Receiving relationship from Restaurant
#     """
#     subzone_has_nonveg = RelationshipFrom('Subzone', 'HAS', model=HasFeature)
#     restaurant_has_nonveg = RelationshipFrom('Restaurant', 'HAS', model=HasFeature)
#
#
# class Seating(StructuredNode):
#     """
#     Metadata for Seating Feature
#
#     All relationships have common model available HasFeature
#
#     Relation Attributes:
#         subzone_has_seating: Receiving relationship from Subzone
#         restaurant_has_seating: Receiving relationship from Restaurant
#     """
#     subzone_has_seating = RelationshipFrom('Subzone', 'HAS', model=HasFeature)
#     restaurant_has_seating = RelationshipFrom('Restaurant', 'HAS', model=HasFeature)
#
#
# class AirConditioned(StructuredNode):
#     """
#     Metadata for AirConditioned Feature
#
#     All relationships have common model available HasFeature
#
#     Relation Attributes:
#         subzone_has airconditioning: Receiving relationship from Subzone
#         restaurant_has_airconditioning: Receiving relationship from Restaurant
#     """
#     subzone_has_airconditioning = RelationshipFrom('Subzone', 'HAS', model=HasFeature)
#     restaurant_has_airconditioning = RelationshipFrom('Restaurant', 'HAS', model=HasFeature)
#
# class OutdoorSeating(StructuredNode):
#     """
#     Metadata for OutdoorSeating Feature
#
#     All relationships have common model available HasFeature
#
#     Relation Attributes:
#         subzone_has_outdoorseating: Receiving relationship from Subzone
#         restaurant_has_outdoorseating: Receiving relationship from Restaurant
#     """
#     subzone_has_outdoorseating = RelationshipFrom('Subzone', 'HAS', model=HasFeature)
#     restaurant_has_outdoorseating = RelationshipFrom('Restaurant', 'HAS', model=HasFeature)
#
#
# class Wifi(StructuredNode):
#     """
#     Metadata for Wifi Feature
#
#     All relationships have common model available HasFeature
#
#     Relation Attributes:
#         subzone_has_wifi: Receiving relationship from Subzone
#         restaurant_has_wifi: Receiving relationship from Restaurant
#     """
#     subzone_has_wifi = RelationshipFrom('Subzone', 'HAS', model=HasFeature)
#     restaurant_has_wifi = RelationshipFrom('Restaurant', 'HAS', model=HasFeature)
#
#
# class SmokingArea(StructuredNode):
#     """
#     Metadata for SmokingArea Feature
#
#     All relationships have common model available HasFeature
#
#     Relation Attributes:
#         subzone_has_smokingarea: Receiving relationship from Subzone
#         restaurant_has_smokingarea: Receiving relationship from Restaurant
#     """
#     subzone_has_amokingarea = RelationshipFrom('Subzone', 'HAS', model=HasFeature)
#     restaurant_has_smokingarea = RelationshipFrom('Restaurant', 'HAS', model=HasFeature)
#
#
# class Sheesha(StructuredNode):
#     """
#     Metadata for Sheesha Feature
#
#     All relationships have common model available HasFeature
#
#     Relation Attributes:
#         subzone_has_sheesha: Receiving relationship from Subzone
#         restaurant_has_sheesha: Receiving relationship from Restaurant
#     """
#     subzone_has_sheesha = RelationshipFrom('Subzone', 'HAS', model=HasFeature)
#     restaurant_has_sheesha = RelationshipFrom('Restaurant', 'HAS', model=HasFeature)