import csv, sqlite3

con = sqlite3.connect("C:/Dev/api_yamdb/api_yamdb/db.sqlite3")
#Указываем абсолютный путь до таблицы db.sqlite3, ВНИМАТЕЛЬНО смотри куда наколнены слэши
cur = con.cursor()
with open('C:/Dev/api_yamdb/api_yamdb/static/data/genre.csv','r', encoding="utf8") as fin:
    #Указываем абсолютный путь до файла с датасетом, ВНИМАТЕЛЬНО смотри куда наколнены слэши
    dr = csv.DictReader(fin)
    to_db = [(i['id'], i['name'], i['slug']) for i in dr]
    #Указываем имена полей, все имена что есть в БД для данной таблицы
cur.executemany(
    "INSERT INTO reviews_genres (id, name, slug) VALUES (?, ?, ?);", to_db
    )
    #Указываем имена полей, количество '?' должно совпадать с количеством полей
con.commit()
con.close()