from . import models as pm

from uuid import uuid4


def restaurant_node(record):

    """
    Create and save a restaurant node.
    :param record: Mongo record containing raw data
    :return: Restaurant object (node)
    """
    obj = pm.Restaurant(id=uuid4().hex, name=record.name)
    obj.address = record.address
    if len(record.latlon) == 2:
        obj.lat = record.latlon[0]
        obj.lon = record.latlon[1]
    else:
        obj.lat = None
        obj.lon = None
    if record.phone != -1:
        obj.phone = record.phone
    obj.rating = record.rating
    obj.timings = record.timings
    obj.save()

    return obj


def create_and_or_link_subzone(restaurant, res_subzone):

    """
    Find the restaurant subzone OR create it, and link it with a restaurant
    :param restaurant: Restaurant node object
    :param res_subzone: Subzone string of restaurant
    :return: connect relationship object
    """
    subzone = pm.Subzone.index.search(name=res_subzone)

    if not subzone:
        subzone = pm.Subzone(name=res_subzone)
    else:
        subzone = subzone[0]

    if restaurant.lat and restaurant.lon and isinstance(subzone.lat, float) and isinstance(subzone.lon, float):
        subzone.lat = (float(subzone.lat) + float(restaurant.lat))/2
        subzone.lon = (float(subzone.lon) + float(restaurant.lon))/2
    elif restaurant.lat and restaurant.lon and isinstance(subzone.lat, pm.FloatProperty) and isinstance(subzone.lon, pm.FloatProperty):
        subzone.lat = float(restaurant.lat)
        subzone.lon = float(restaurant.lon)

    subzone.save()
    restaurant.near.connect(subzone)

    return subzone


def create_and_or_link_cuisine(restaurant, subzone, cuisines=()):

    """
    Based on number of cuisines available at the restaurant,
    create or find the cuisine connected to the subzone and
    complete connections from restaurant, subzone to cuisine node
    :param cuisines: Iterable cuisines served by restaurant
    :param restaurant: The restaurant node
    :param subzone: The subzone node
    """

    for cuisine in cuisines:
        cuisine_nodes = pm.Cuisine.index.search(name=cuisine)
        cuisine_found = False
        for cuisine_node in cuisine_nodes:

            if subzone.serves.is_connected(cuisine_node):
                restaurant.serves.connect(cuisine_node)
                cuisine_found = True
                break

        if not cuisine_found:
            new_cuisine_node = pm.Cuisine(name=cuisine, subzone=subzone.name).save()
            restaurant.serves.connect(new_cuisine_node)
            subzone.serves.connect(new_cuisine_node)