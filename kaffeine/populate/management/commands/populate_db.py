from django.core.management.base import BaseCommand

from populate import utils as pu
from populate.models import Items

import pdb


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (

    )
    help = "Help text goes here"

    def handle(self, **options):
        # try:
        #     graph_db = neo4j.GraphDatabaseService('http://127.0.0.1:7474/db/data/')
        # except SocketError as e:
        #     raise CommandError('Socket Error. Cannot Connect' + str(e))

        print "Starting Population..."

        for record in Items.objects.all():

            try:
                restaurant = pu.restaurant_node(record)
                subzone = pu.create_and_or_link_subzone(restaurant, record.subzone)
                pu.create_and_or_link_cuisine(restaurant, subzone, record.cuisines)
            except Exception as e:
                print "Exception occured:" + str(e)
                pdb.set_trace()