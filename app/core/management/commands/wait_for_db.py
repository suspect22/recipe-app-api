import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Djange command to pause execution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write('Wait until Database is a availble')
        db_connection = None
        while not db_connection:
            try:
                db_connection = connections['default'].cursor()
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))
