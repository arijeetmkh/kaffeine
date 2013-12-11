from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from populate import utils as pu
from populate import models as pm

from py2neo import neo4j
from py2neo.rest import SocketError


class Command(BaseCommand):

    clear_db = False

    feature_list = [
        "Dine-In Available",
        "Home Delivery",
        "Serves Non Veg",
        "Bar Available",
        "Seating Available",
        "Air Conditioned",
        "Outdoor Seating",
        "Wifi Internet Available",
        "Smoking Area",
        "Sheesha"
    ]

    option_list = BaseCommand.option_list + (
        make_option('--clear', '-c', dest='clear', help="Clear db initially?"),
    )

    help = """
        Options:
            Clear Database initially: --clear OR -c
    """

    def handle(self, **options):

        if options['clear']:
            self.clear_db()

        self.populate()


    def clear_db(self):
        print "Attempting to empty database"
        try:
            graph_db = neo4j.GraphDatabaseService('http://127.0.0.1:7474/db/data/')
            graph_db.clear()
            print "Database empty!"
        except SocketError as e:
            raise CommandError('Socket Error. Cannot Connect' + str(e))


    def populate(self):
        print "Starting Population..."

        for i,record in enumerate(pm.Items.objects.all()):
            print i
            try:
                restaurant = pu.restaurant_node(record)
                subzone = pu.create_and_or_link_subzone(restaurant, record.subzone)
                pu.create_and_or_link_cuisine(restaurant, subzone, record.cuisines)
                #pu.create_and_or_link_features("restaurant", "subzone", [self.feature_dict.get(t, None) for t in record.highlights + record.tags if self.feature_dict.has_key(t)])
                pu.create_and_or_link_features(restaurant, subzone, list(set(self.feature_list).intersection(set(record.highlights + record.tags))))
            except Exception as e:
                print "Exception occured:" + str(e)