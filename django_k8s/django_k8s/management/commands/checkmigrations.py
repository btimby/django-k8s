import time

from django.core.management.base import BaseCommand
from django.db.migrations.executor import MigrationExecutor
from django.db import connections


def pending_migrations():
    "Count the number of migrations not yet applied to database(s)"
    nmigrations = 0
    for db_name in connections:
        connection = connections[db_name]
        connection.prepare_database()
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        nmigrations += len(executor.migration_plan(targets))
    return nmigrations


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('--wait', action='store_true')

    def handle(self, *args, **options):
        while True:
            nmigrations = pending_migrations()

            if nmigrations == 0:
                print('There are no pending migrations')
                exit(0)

            print('There are %i pending migrations' % nmigrations)

            if not options['wait']:
                exit(1)

            time.sleep(5.0)
