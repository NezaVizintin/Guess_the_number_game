import os
from sqla_wrapper import SQLAlchemy

db_url = os.getenv("DATABASE_URL", "sqlite:///db.sqlite").replace("postgres://", "postgresql://", 1)
database = SQLAlchemy(db_url)

class User(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(20), unique=False)
    email = database.Column(database.String(20), unique=True)
    password = database.Column(database.String(260)) # must be 255 or more for hashing
    number_secret = database.Column(database.Integer, unique=False)
    session_token = database.Column(database.String) # random string that a user can use to prove that they have already been successfully authenticated