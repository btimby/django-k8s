import time

from django.core.management.base import BaseCommand
from django.db import connections, DEFAULT_DB_ALIAS

try:
    from django import __version__
except ImportError:
    from django import VERSION as __version__


def check_databases():
    for db_name in connections:
        connection = connections[db_name]
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT (1)')
            return True

        except:
            return False

        finally:
            cursor.close()


def _count_migrations_1_4_db(db_name):
    from south.models import MigrationHistory
    from south.migration import all_migrations

    apps = all_migrations()
    applied_migrations = MigrationHistory.objects.filter(
        app_name__in=[app.app_label() for app in apps])
    if db_name != DEFAULT_DB_ALIAS:
        applied_migrations = applied_migrations.using(db_name)
    applied_migrations_lookup = dict()

    nmigrations = 0
    for app in apps:
        for migration in app:
            full_name = migration.app_label() + '.' + migration.name()
            if full_name not in applied_migrations_lookup:
                nmigrations += 1
    return nmigrations


def count_migrations_1_4():
    nmigrations = 0
    for db_name in connections:
        nmigrations += _count_migrations_1_4_db(db_name)
    return nmigrations


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
            if check_databases():
                nmigrations = count_migrations()

                if nmigrations == 0:
                    print('Migrations complete')
                    exit(0)

                print('There are %i pending migrations' % nmigrations)

            else:
                print('Database connections not ready')

            if not options['wait']:
                exit(1)

            time.sleep(5.0)
