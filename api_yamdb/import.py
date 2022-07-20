"""DB import script."""""
import csv
import sqlite3

con = sqlite3.connect("C:/Dev/api_yamdb/api_yamdb/db.sqlite3")
cur = con.cursor()
with open(
    'C:/Dev/api_yamdb/api_yamdb/static/data/genre.csv',
    'r', encoding="utf8"
) as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'], i['name'], i['slug']) for i in dr]
cur.executemany(
    "INSERT INTO reviews_genres (id, name, slug) VALUES (?, ?, ?);", to_db
)
con.commit()
con.close()
