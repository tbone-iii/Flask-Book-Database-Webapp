import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set.")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# db.execute("CREATE TABLE accounts(\
#   id SERIAL PRIMARY KEY,\
#   username VARCHAR NOT NULL,\
#   password VARCHAR NOT NULL\
# );\
# CREATE TABLE books(\
#   id SERIAL PRIMARY KEY,\
#   title VARCHAR NOT NULL,\
#   author VARCHAR NOT NULL,\
#   year INTEGER NOT NULL,\
#   isbn VARCHAR NOT NULL\
# );")


@app.route("/")
def index():
    if "username" in session:
        username = session["username"]
        print(f"This is the session username: {session['username']}")
        books = db.execute("SELECT * FROM books").fetchall()
    else:
        username = None
        print(username)
    for account in db.execute("SELECT * FROM accounts").fetchall():
        print(account)

    return render_template("index.html", username=username, books=books)


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/registered", methods=["POST"])
def registered():
    username = request.form.get("username")
    password = request.form.get("password")
    if password.replace(" ", "") is not password:
        return render_template("error.html", message="Invalid password.")
    elif username.replace(" ", "") is not username:
        return render_template("error.html", message="Invalid username.")

    # If the username already exists
    if check_for_username(username):
        return render_template(
            "error.html", message="Username already exists!")
    else:
        db.execute("INSERT INTO accounts (username, password) VALUES "
                   "(:username, :password)",
                   {"username": username, "password": password})
        db.commit()
        session["username"] = username
        return render_template(
            "success.html", message="You have sucessfully registered!")


@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/sign-in", methods=["POST"])
def sign_in():
    username = request.form.get("username")
    password = request.form.get("password")
    if username and password:
        # See if account with username and password exists
        account_exists = db.execute(
            "SELECT username FROM accounts WHERE "
            "username = :username AND password = :password",
            {"username": username, "password": password}).fetchone()
        # If account exists, log them in
        if account_exists:
            session["username"] = username
            return render_template(
                "success.html",
                message=f"You have successfully logged in as {username}!")
        # Wrong password or username
        else:
            return render_template(
                "error.html", message="Wrong username or password!")
    # Did not fill in the form properly
    else:
        return render_template(
            "error.html",
            message="You must input a valid username and password.")


@app.route("/loggedout")
def signout():
    session["username"] = None
    session["password"] = None
    return render_template("success.html", message="Succesfully logged out!")


@app.route("/results", methods=["POST"])
def book_search():
    """ Gives the search results for the books. """
    search_value = request.form.get("search_value")
    book_results = db.execute(
        f"SELECT * FROM books WHERE title LIKE '%{search_value}%' "
        f"OR author LIKE '%{search_value}%' "
        f"OR isbn LIKE '%{search_value}%'").fetchall()
    # If there are no results
    if book_results is None:
        return render_template("error.html", message="No books found.")
    return render_template("results.html", book_results=book_results)


@app.route("/books/<book_isbn>")
def book(book_isbn):
    """ List details about a single book. """
    # Make sure the book exists.
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",
                      {"isbn": book_isbn}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book.")

    # Get all the reviews for the book
    # reviews = db.execute("SELECT review FROM ")
    return render_template("book.html", book=book)  # , reviews=reviews)


def check_for_username(username: str):
    """ Checks to see if the username is in the database. """
    account = db.execute(
        "SELECT * FROM accounts WHERE username = :username",
        {"username": username}).fetchone()
    return account


if __name__ == '__main__':
    app.run()
