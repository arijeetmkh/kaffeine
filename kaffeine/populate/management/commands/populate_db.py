from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from populate import utils as pu
from populate.models import Items

from py2neo import neo4j
from py2neo.rest import SocketError


class Command(BaseCommand):

    clear_db = False

    option_list = BaseCommand.option_list + (
        make_option('--clear', '-c', dest='clear', help="Clear db initially?"),
    )

    help = """
        Options:
            Clear Database initially: --clear OR -c
    """

    def handle(self, **options):
        # try:
        #     graph_db = neo4j.GraphDatabaseService('http://127.0.0.1:7474/db/data/')
        # except SocketError as e:
        #     raise CommandError('Socket Error. Cannot Connect' + str(e))
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

        for i,record in enumerate(Items.objects.all()):
            print i
            try:
                restaurant = pu.restaurant_node(record)
                subzone = pu.create_and_or_link_subzone(restaurant, record.subzone)
                pu.create_and_or_link_cuisine(restaurant, subzone, record.cuisines)
            except Exception as e:
                print "Exception occured:" + str(e)