from . import models as pm
from . import feature_list

from uuid import uuid4

import ast, pdb
import requests, elasticsearch

def generate_geoff():

    def gen_kwargs(iterable, record, key_format=None, value_format=None, exclude=[]):

        for i,element in enumerate(iterable):
            if element in exclude:
                iterable.pop(i)

        package = {}

        for element in iterable:
            package.update({element if key_format is None else value_format.format(dot=".", _=element):eval(record.element, {}, {'record':record}) if value_format is None else eval(value_format.format(dot=".", _=element), {}, {'record':record})})

        package.update({'features':list(set(feature_list).intersection(set(record.highlights + record.tags)))})
        return package

    g = open('populate.geoff', 'w')
    restaurant_batch_insert = []
    subzone_batch_insert = []

    for record in pm.Items.objects.all():
        _id = uuid4().hex
        #Create restaurant node
        g.write('("{node_name}__{_id}":Restaurant {{"name":"{node_name}", "_id":"{_id}"}})\n'.format(node_name=record.name, _id=_id))
        #Create subzone node
        g.write('("{node_name}":Subzone!name {{"name":"{node_name}"}})\n'.format(node_name=record.subzone))
        #Connect Restaurant with Subzone
        g.write('("{restaurant_name}")-[:NEAR]->("{subzone_name}")\n'.format(restaurant_name=record.name + "__" + _id, subzone_name=record.subzone))

        # restaurant_batch_insert.append(pm.RestaurantStatic(id=_id, name=record.name, timings=record.timings, phone=record.phone, cost=record.cost, address=record.address, subzone=record.subzone))
        restaurant_batch_insert.append(pm.RestaurantStatic(**gen_kwargs(iterable=pm.Items._fields.keys(), value_format="record{dot}{_}", exclude=['url', 'highlights', 'highlights_not', 'tags'], record=record)))
        subzone_batch_insert.append(record.subzone)

        #Create cuisine node if required
        for cuisine in record.cuisines:
            g.write('("{cuisine}__{subzone}":Cuisine:"{cuisine}" {{"subzone":"{subzone}", "name":"{cuisine}"}})\n'.format(cuisine=cuisine, subzone=record.subzone))
            g.write('("{cuisine}__{subzone}")<-[:SERVES!]-("{subzone}")\n'.format(cuisine=cuisine, subzone=record.subzone))
            g.write('("{restaurant_name}__{_id}")-[:SERVES]->("{cuisine}__{subzone}")\n'.format(restaurant_name=record.name, _id=_id, cuisine=cuisine, subzone=record.subzone))

        for feature in list(set(feature_list).intersection(set(record.highlights + record.tags))):
            g.write('("{feature}__{subzone}":Feature:"{feature}" {{"name":"{feature}"}})\n'.format(feature=feature, subzone=record.subzone))
            g.write('("{feature}__{subzone}")<-[:HAS]-("{subzone}")\n'.format(feature=feature, subzone=record.subzone))
            g.write('("{restaurant_name}__{_id}")-[:HAS]->("{feature}__{subzone}")\n'.format(restaurant_name=record.name, _id=_id, feature=feature, subzone=record.subzone))

    g.close()
    payload = open('populate.geoff', 'r')
    response = requests.post('http://127.0.0.1:7474/load2neo/load/geoff', data=payload)
    payload.close()
    es = elasticsearch.Elasticsearch()
    for i,subzone in enumerate(list(set(subzone_batch_insert)),1):
        es.index(
            index="subzone",
            doc_type="static",
            id=i,
            body={
                "name":subzone
            }
        )

    for i,cuisine in enumerate(pm.Items.objects.distinct('cuisines')):
        es.index(
            index="cuisine",
            doc_type="static",
            id=i,
            body={
                "name":cuisine
            }
        )

    for i,feature in enumerate(feature_list):
        es.index(
            index="feature",
            doc_type="static",
            id=i,
            body={
                "name":feature
            }
        )

    pm.RestaurantStatic.objects.insert(restaurant_batch_insert)
    print response.status_code
    print response.text


class PreProcessing(object):

    def __init__(self, tagger):
        """
        Accept incoming POST as tagger and evaluate it into dict
        Call segregator
        :param tagger: Incoming POST (type String)
        """
        print tagger
        tagger = ast.literal_eval(tagger)
        self.errors = {}

        self.segregator(tagger)


    def segregator(self, tagger):
        """
        Use tagger dict to separate out meta contents and tokens
        :param tagger: Dict containing tokens only
        """
        self.meta = tagger.pop('meta')
        self.tokens = tagger


    def getter(self, get):
        """
        This method allows a string input or an iterable input
        and returns their values by checking member values
        """
        if hasattr(get, '__iter__'):
            pass
        else:
            pass

        return None


class Router(PreProcessing):

    graph_routes = {
        ("Dish", "Restaurant"):["Subzone", "Cuisine", "Restaurant", "Feature"],
        ("Dish", "Feature"):["Subzone", "Cuisine", "Restaurant"],
        ("Dish", "Subzone"):["Restaurant", "Cuisine", "Feature"],
        ("Dish", "Cuisine"):["Subzone", "Restaurant", "Feature"],
        ("Dish", "Cuisine", "Restaurant"):["Subzone", "Feature", "Restaurant"],
        ("Dish", "Cuisine", "Feature"): ["Subzone", "Restaurant"],
        ("Dish", "Cuisine", "Subzone"):["Restaurant", "Feature"],
        ("Dish", "Subzone", "Restaurant"):["Cuisine", "Restaurant", "Feature"],
        ("Dish", "Subzone", "Feature"):["Restaurant", "Cuisine"],
        ("Dish", "Feature", "Restaurant"):["Subzone", "Cuisine", "Restaurant"]
    }

    def __init__(self, tagger):

        super(Router, self).__init__(tagger)


    def route_seletor(self):
        """
        Based on received tokens, perform intersection with all possible tokens
        and use graph routes to select route
        """

        def select_valid_keys(key):
            if self.tokens.get(key, None):
                return key


        intersection = set([x for x in self.tokens if not self.tokens[x]]) & set(self.tokens.keys())

        self.route = self.graph_routes[tuple(intersection)]


class QueryAssembler(Router):
    pass