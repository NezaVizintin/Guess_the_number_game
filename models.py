import os
from sqla_wrapper import SQLAlchemy

# the replace method is needed due to this issue: https://help.heroku.com/ZKNTJQSK/why-is-sqlalchemy-1-4-x-not-connecting-to-heroku-postgres
# SQLAlchemy .Column documentation: https://docs.sqlalchemy.org/en/14/core/metadata.html#sqlalchemy.schema.Column

db_url = os.getenv("DATABASE_URL", "sqlite:///db.sqlite")#.replace("postgres://", "postgresql://", 1)
database = SQLAlchemy(db_url)

class User(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(20), unique=True)
    email = database.Column(database.String(20), unique=True)
    password = database.Column(database.String(260)) # must be 255 or more for hashing
    number_secret = database.Column(database.Integer, unique=False)
    session_token = database.Column(database.String) # random string that a user can use to prove that they have already been successfully authenticated
    deleted = database.Column(database.Boolean, default=False) # sets the user as deleted. It's set as False when a new user is created