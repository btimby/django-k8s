import time

from django.core.management.base import BaseCommand
from django.db import connections

try:
    from django import __version__
except ImportError:
    from django import VERSION as __version__


def test_connections():
    for db_name in connections:
        connection = connections[db_name]
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT (1)')

        finally:
            cursor.close()


def count_migrations_1_4():
    return 0


def count_migrations_1_7():
    from django.db.migrations.executor import MigrationExecutor

    nmigrations = 0
    for db_name in connections:
        connection = connections[db_name]


        try:
            connection.prepare_database()
        except AttributeError:
            pass

        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        nmigrations += len(executor.migration_plan(targets))
    return nmigrations


def count_migrations():
    "Count the number of migrations not yet applied to database(s)"
    # South is external.
    if __version__[0] == 1 and __version__[1] < 7:
        return count_migrations_1_4()
    else:
        return count_migrations_1_7()



class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('--wait', action='store_true')

    def handle(self, *args, **options):
        while True:
            if test_connections():
                nmigrations = count_migrations()

                if nmigrations == 0:
                    print('There are no pending migrations')
                    exit(0)

                print('There are %i pending migrations' % nmigrations)

            else:
                print('Database connections not ready')

            if not options['wait']:
                exit(1)

            time.sleep(5.0)
