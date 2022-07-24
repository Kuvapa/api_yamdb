"""DB import script."""""
import csv
import sqlite3
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Custom command for DB import."""

    help = 'Script for filling DB by test-data'

    def handle(self, *args, **options):
        """Script body."""
        con = sqlite3.connect("C:/Dev/api_yamdb/api_yamdb/db.sqlite3")
        cur = con.cursor()
        with open(
            'C:/Dev/api_yamdb/api_yamdb/static/data/genre.csv',
            'r', encoding="utf8"
        ) as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['id'], i['name'], i['slug']) for i in dr]
        cur.executemany(
            "INSERT INTO reviews_genres (id, name, slug) VALUES (?, ?, ?);",
            to_db
        )
        con.commit()
        con.close()
