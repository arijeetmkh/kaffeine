from . import models as pm
from . import feature_list
# from kaffeine.settings import graph_db_conn

from uuid import uuid4
from py2neo import neo4j

import ast, pdb,json
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
        del package['id'] #ToDo Improve this!

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
        restaurant_batch_insert.append(pm.RestaurantStatic(id=_id, **gen_kwargs(iterable=pm.Items._fields.keys(), value_format="record{dot}{_}", exclude=['url', 'highlights', 'highlights_not', 'tags'], record=record)))
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
        tagger = json.loads(tagger)
        # tagger = ast.literal_eval(tagger)
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

    route = None

    def __init__(self, tagger):

        super(Router, self).__init__(tagger)


    def route_seletor(self):
        """
        Based on received tokens, perform intersection with all possible tokens
        and use graph routes to select route
        """

        def select_valid_keys(key):
            """
            Unused at the moment
            """
            if self.tokens.get(key, None):
                return key

        if sum(map(bool, self.tokens.values())) != 1:
            intersection = set([x for x in self.tokens if not self.tokens[x]]) & set(self.tokens.keys())
            self.route = self.graph_routes[tuple(intersection)]
        else:
            for key in self.tokens.keys():
                if bool(self.tokens[key]):
                    self.route = ["Restaurant"] if key == "Restaurant" else [key, "Restaurant"]
                    break


class QueryFactory(Router):

    query = ""

    def __init__(self, tagger, logger):
        self.graph_db_conn = neo4j.GraphDatabaseService()
        self.logger = logger
        super(QueryFactory, self).__init__(tagger)

    def query_controller(self):
        """
        Handles the dispatch of all queries
        """
        #ToDo Add error checking
        self.query_assembler()
        self.query_post_processing()
        self.query_executer()


    def query_assembler(self):
        """
        Use selected route to assemble the query
        """
        #ToDo Document this method properly

        def loop_next(iterator, i=None):
            if i:
                try:
                    to_return = iterator[i]
                    return to_return
                except IndexError:
                    return None
            else:
                return None

        route_len = len(self.route)
        with_ident = False

        for i,node_type in enumerate(self.route,1):
            # self.logger.debug(self.query)

            if node_type is "Restaurant" and not bool(self.tokens['Restaurant']):
                continue

            self.query += "MATCH "

            if with_ident:
                self.query += "({with_ident})--".format(with_ident=with_ident)

            ident = node_type[0].lower()
            where_params = []

            self.query += '({ident}:{node_type})'.format(ident=ident, node_type=node_type)

            for token in self.tokens[node_type]:
                where_params.append('({token})'.format(token=token))
            else:
                if loop_next(self.route, i) is "Restaurant" and not bool(self.tokens['Restaurant']):
                    # If the next node is Restaurant, and its tokens are empty, do the following..
                    # 1. Append --(r:Restaurant) to it
                    # 2. Perform any where operations
                    # 3. Set new with_ident to 'r' beacuse we have MATCHed forcefully to Restaurant
                    # 4. Add the with_ident to the query string
                    self.query += "--(r:Restaurant)"
                    self.query += ' WHERE {ident}.name =~ "{where_params}"'.format(ident=ident, where_params="|".join(where_params))
                    with_ident = 'r'
                    self.query += " WITH {with_ident}".format(with_ident=with_ident)
                elif where_params:
                    # Next item is either NOT a restaurant OR is a restaurant and has empty where params for restaurant
                    self.query += ' WHERE {ident}.name =~ "{where_params}"'.format(ident=ident, where_params="|".join(where_params))

                    # Enter only IF:
                        #   Current iteration is at most two less than total in route AND
                        #   Next Loop iteration exists in route
                        #   OR
                        #   Current iteration is atmost one less than total in route AND
                        #   Next Loop iteration is not Restaurant
                    # Else:
                        #
                    # if (i < route_len-1 and loop_next(self.route, i)) or (i < route_len and loop_next(self.route, i) is not "Restaurant"):
                    if loop_next(self.route, i):
                        # Set with_ident to 'r' if Restaurant has occured already
                        with_ident = ident if "Restaurant" not in self.route[:i] else 'r'
                        self.query += " WITH {with_ident}".format(with_ident=with_ident)
                    # else:
                    #     with_ident = ident
                    #     self.query += " WITH {with_ident}".format(with_ident=with_ident)

            self.query += " "

        self.query = self.query.strip()



    def query_post_processing(self):
        """
        Apply RETURN, SKIP and LIMIT operations to tail end of query
        """
        #ToDo Check to see if r._id will always return correctly (r.NUM needed?)
        self.query += " RETURN collect(r._id) LIMIT 20;"


    def query_executer(self):
        """
        This method is responsible for using py2neo to run the queries
        """
        self.cypher_query_object = neo4j.CypherQuery(self.graph_db_conn, self.query)
        self.results = self.cypher_query_object.execute()

    def get_results_or_errors(self):
        """
        Returns self.results if results found, else give out errors, NotFound, DB Errors, etc
        """
        return self.results.data[0]._values[0]

        # return self.results

#ToDo Add getter and setters
#ToDo Add overall superclass for control of flow
#ToDo Add pagination class member options
#Use filter to weed out None keys