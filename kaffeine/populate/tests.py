"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.utils import unittest

from .utils import QueryFactory

from itertools import imap

class QueryTest(unittest.TestCase):

    def setUp(self):

        self.route_query = {
            ("Dish", "Restaurant"):'MATCH (s:Subzone) WHERE s.name =~ "Naraina" WITH s MATCH (s)--(c:Cuisine) WHERE c.name =~ "Chinese" WITH c MATCH (c)--(r:Restaurant)-[:HAS]-> (f:Feature) WHERE f.name =~ "Bar Available" RETURN r._id LIMIT 20;',
            ("Dish", "Feature"):'MATCH (s:Subzone) WHERE s.name =~ "Naraina" WITH s MATCH (s)--(c:Cuisine) WHERE c.name =~ "Chinese" WITH c MATCH (c)--(r:Restaurant) RETURN collect(r._id) LIMIT 20;',
            ("Dish", "Subzone"):'MATCH (r:Restaurant) WHERE r.name =~ "Subway" WITH r MATCH (r)--(c:Cuisine) WHERE c.name =~ "American" WITH r MATCH (r)--(f:Feature) WHERE f.name =~ "Home Delivery" RETURN collect(r._id) LIMIT 20;',
            ("Dish", "Cuisine"):'MATCH (s:Subzone) WHERE s.name =~ "Naraina" WITH s MATCH (s)--(r:Restaurant) WHERE r.name =~ "Subway" WITH r MATCH (r)--(f:Feature) WHERE f.name =~ "Home Delivery" RETURN r._id LIMIT 20;',
            ("Dish", "Cuisine", "Restaurant"):'MATCH (s:Subzone) WHERE s.name =~"Naraina" WITH s MATCH (s)--(f:Feature)--(r:Restaurant) WHERE f.name =~ "Home Delivery" RETURN r._id LIMIT 20;',
            ("Dish", "Cuisine", "Feature"): 'MATCH (s:Subzone) WHERE s.name =~ "Naraina" WITH s MATCH (s)--(r:Restaurant) WHERE r.name =~ "Subway" RETURN collect(r._id) LIMIT 20;',
            ("Dish", "Cuisine", "Subzone"):'MATCH (r:Restaurant) WHERE r.name =~ "Subway" WITH r MATCH (r)--(f:Feature) WHERE f.name =~ "Home Delivery" RETURN collect(r._id) LIMIT 20;',
            ("Dish", "Subzone", "Restaurant"):'MATCH (c:Cuisine) WHERE c.name =~ "Chinese" WITH c MATCH (c)--(r:Restaurant) WITH r MATCH (r)--(f:Feature) WHERE f.name =~ "Bar Available" RETURN r.name LIMIT 20;',
            ("Dish", "Subzone", "Feature"):'MATCH (r:Restaurant) WHERE r.name =~ "Subway" WITH r MATCH (r)--(c:Cuisine WHERE c.name =~ "Chinese" RETURN collect(r._id) LIMIT 20;',
            ("Dish", "Feature", "Restaurant"):'MATCH (s:Subzone) WHERE s.name =~ "Naraina" WITH s MATCH (s)--(c:Cuisine) WHERE c.name =~ "Chinese" WITH c MATCH (c)--(r:Restaurant) RETURN collect(r._id) LIMIT 20;'
        }

        self.POST_FORMAT = {
                'meta':{
                    'q':'',
                    'last_token':''
                },
                'Restaurant':[],
                'Subzone':[],
                'Feature':[],
                'Cuisine':[],
                'Dish':[]
        }

        self.POST = self.POST_FORMAT

        self.restaurant = "Subway"
        self.cuisine = "American"
        self.feature = "Home Delivery"
        self.subzone = "Naraina"
        self.dish = None


    def test_query_controller(self):

            for route in self.route_query.keys():

                for node in imap(str ,route):

                    self.POST[node].append(getattr(self, node))

                qf = QueryFactory(str(self.POST))
                qf.route_seletor()
                qf.query_controller()

                self.assertEqual(qf.query, self.route_query[route])

                self.POST = self.POST_FORMAT
