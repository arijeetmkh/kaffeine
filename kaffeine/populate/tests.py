"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.utils import unittest
from django.test import LiveServerTestCase, Client
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from .utils import QueryFactory

from itertools import imap
import pdb


class IntegrationTests(LiveServerTestCase):

    host = "http://myapp.localhost:8000"

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(IntegrationTests, cls).setUpClass()


    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(IntegrationTests, cls).tearDownClass()


    def test_homepage(self):

        client = Client()
        response = client.get('%s%s' % (self.host, '/home/'))
        self.assertEqual(response.status_code, 200)


    def test_search(self):

        search_options = ["italian", "chinese near sda", "sda serving chinese", "sda"]

        for option in search_options:

            self.selenium.get('%s%s' % (self.live_server_url, '/home'))
            searchInput = self.selenium.find_element_by_name("searchInput")
            searchInput.send_keys(option)
            searchInput.send_keys(Keys.ENTER)
            id = self.selenium.find_element_by_id("id")
            self.assertTrue(id.text, "Async ID Not Returned")
            elements = None
            try:
                elements = WebDriverWait(self.selenium, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))
            except TimeoutException:
                self.assertTrue(elements, "No results returned. Failed for case - %s" % option)

# class QueryTest(unittest.TestCase):
#
#     def setUp(self):
#
#         self.route_query = {
#             ("Dish", "Restaurant"):'MATCH (s:Subzone) WHERE s.name =~ "Naraina" WITH s MATCH (s)--(c:Cuisine) WHERE c.name =~ "Chinese" WITH c MATCH (c)--(r:Restaurant)-[:HAS]-> (f:Feature) WHERE f.name =~ "Bar Available" RETURN r._id LIMIT 20;',
#             ("Dish", "Feature"):'MATCH (s:Subzone) WHERE s.name =~ "Naraina" WITH s MATCH (s)--(c:Cuisine) WHERE c.name =~ "Chinese" WITH c MATCH (c)--(r:Restaurant) RETURN collect(r._id) LIMIT 20;',
#             ("Dish", "Subzone"):'MATCH (r:Restaurant) WHERE r.name =~ "Subway" WITH r MATCH (r)--(c:Cuisine) WHERE c.name =~ "American" WITH r MATCH (r)--(f:Feature) WHERE f.name =~ "Home Delivery" RETURN collect(r._id) LIMIT 20;',
#             ("Dish", "Cuisine"):'MATCH (s:Subzone) WHERE s.name =~ "Naraina" WITH s MATCH (s)--(r:Restaurant) WHERE r.name =~ "Subway" WITH r MATCH (r)--(f:Feature) WHERE f.name =~ "Home Delivery" RETURN r._id LIMIT 20;',
#             ("Dish", "Cuisine", "Restaurant"):'MATCH (s:Subzone) WHERE s.name =~"Naraina" WITH s MATCH (s)--(f:Feature)--(r:Restaurant) WHERE f.name =~ "Home Delivery" RETURN r._id LIMIT 20;',
#             ("Dish", "Cuisine", "Feature"): 'MATCH (s:Subzone) WHERE s.name =~ "Naraina" WITH s MATCH (s)--(r:Restaurant) WHERE r.name =~ "Subway" RETURN collect(r._id) LIMIT 20;',
#             ("Dish", "Cuisine", "Subzone"):'MATCH (r:Restaurant) WHERE r.name =~ "Subway" WITH r MATCH (r)--(f:Feature) WHERE f.name =~ "Home Delivery" RETURN collect(r._id) LIMIT 20;',
#             ("Dish", "Subzone", "Restaurant"):'MATCH (c:Cuisine) WHERE c.name =~ "Chinese" WITH c MATCH (c)--(r:Restaurant) WITH r MATCH (r)--(f:Feature) WHERE f.name =~ "Bar Available" RETURN r.name LIMIT 20;',
#             ("Dish", "Subzone", "Feature"):'MATCH (r:Restaurant) WHERE r.name =~ "Subway" WITH r MATCH (r)--(c:Cuisine WHERE c.name =~ "Chinese" RETURN collect(r._id) LIMIT 20;',
#             ("Dish", "Feature", "Restaurant"):'MATCH (s:Subzone) WHERE s.name =~ "Naraina" WITH s MATCH (s)--(c:Cuisine) WHERE c.name =~ "Chinese" WITH c MATCH (c)--(r:Restaurant) RETURN collect(r._id) LIMIT 20;'
#         }
#
#         self.POST_FORMAT = {
#                 'meta':{
#                     'q':'',
#                     'last_token':''
#                 },
#                 'Restaurant':[],
#                 'Subzone':[],
#                 'Feature':[],
#                 'Cuisine':[],
#                 'Dish':[]
#         }
#
#         self.POST = self.POST_FORMAT
#
#         self.restaurant = "Subway"
#         self.cuisine = "American"
#         self.feature = "Home Delivery"
#         self.subzone = "Naraina"
#         self.dish = None
#
#
#     def test_query_controller(self):
#
#             for route in self.route_query.keys():
#
#                 for node in imap(str ,route):
#
#                     self.POST[node].append(getattr(self, node))
#
#                 qf = QueryFactory(str(self.POST))
#                 qf.route_seletor()
#                 qf.query_controller()
#
#                 self.assertEqual(qf.query, self.route_query[route])
#
#                 self.POST = self.POST_FORMAT
