import os
from sqla_wrapper import SQLAlchemy

db_url = os.getenv("DATABASE_URL", "sqlite:///db.sqlite").replace("postgres://", "postgresql://", 1)
database = SQLAlchemy(db_url)

class User(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(20), unique=True)
    email = database.Column(database.String(20), unique=True)
    number_secret = database.Column(database.Integer, unique=False)