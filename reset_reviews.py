import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

db.execute("DROP TABLE reviews;")
db.execute(
    "CREATE TABLE reviews("
    "   id SERIAL PRIMARY KEY,"
    "   review VARCHAR NOT NULL,"
    "   username VARCHAR NOT NULL,"
    "   isbn VARCHAR NOT NULL,"
    "   date TIMESTAMP NOT NULL,"
    "   rating INTEGER NOT NULL"
    ");"
)
db.commit()

print('\a')
