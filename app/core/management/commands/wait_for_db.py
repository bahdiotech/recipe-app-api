"""
Django command wait for the database to be available.
"""
import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2OpError


class Command(BaseCommand):
    """Django Command to wait for Database."""

    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.stdout.write('Wait for database')
        """ the command self.stdout is for standard output stream"""
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, wait 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))
