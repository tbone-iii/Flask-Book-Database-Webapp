import os

from csv import reader
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
# import requests

# TODO: Example request review json with API key.
# res = requests.get("https://www.goodreads.com/book/review_counts.json",
#                    params={"key": "F2M8MNUf2zeU1DceZWdXuw",
#                            "isbns": "9781632168146"})
# print(res.json())


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

db.execute("DROP TABLE books;")
db.execute(
    "CREATE TABLE books("
    # "   id SERIAL PRIMARY KEY,"
    "   isbn VARCHAR NOT NULL,"
    "   author VARCHAR NOT NULL,"
    "   title VARCHAR NOT NULL,"
    "   year INTEGER NOT NULL,"
    "   average_rating INTEGER,"
    "   number_of_ratings INTEGER"
    ");"
)

with open("books.csv", "r") as csvfile:
    csv_reader = reader(csvfile)
    # Skips the header
    next(csv_reader)
    var = 0
    for line in csv_reader:
        var += 1
        if var % 500 == 0:
            print(var)
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES"
                   "(:isbn, :title, :author, :year)",
                   {"isbn": line[0], "title": line[1], "author": line[2],
                    "year": int(line[3])})
    db.commit()
