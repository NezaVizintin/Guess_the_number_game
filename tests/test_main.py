import os
import pytest
from models import User

# important: this line needs to be set BEFORE the "app" import
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from main import app, database

@pytest.fixture
# takes the Flask app from main.py and prepares it for testing
def client_empty_database():
    client = app.test_client()

    cleanup()  # deletes the database before every test (so that we have a clean slate before every test)

    database.create_all() # tests do not use your real localhost database (localhost.sqlite), but instead create a temporary database that lives only inside computer's RAM (sqlite:///:memory:)

    yield client # https://www.pythonforbeginners.com/basics/difference-between-yield-and-return-in-python#htoc-what-is-yield-and-return-in-python

@pytest.fixture
def client_with_database_entry():
    client = app.test_client()

    cleanup()

    database.create_all()
    user = User(name="existing user", email="existing@email.com", password="existingPassword", number_secret="8") # creates single entry in database
    user.save()

    yield client

# index logged in/logged out

def test_index_not_logged_in(client_empty_database): #  the name of the function and the name of the test file starts with test_. This tells the pytest library that these are our automated tests
    response = client_empty_database.get('/') #  sends a GET request to the / URL (where the index() handler is located) and receives back a response

    assert b'Enter your username' in response.data # this is the actual test. Checks (assert) if the data in the response (in our case, the HTML document) has a string 'Enter your name' inside.
                                                   # the b in front of a string just means that Python will convert the string into byte code since that's the format of response.data

def test_index_logged_in(client_empty_database):
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True) # In the post request specify both the handler URL and also the data you want to send into the handler.
                                                                                        # For login we sent "user-name", "user-email" and "user-password"
    response = client_empty_database.get('/')
    assert b'Guess and press enter' in response.data

# login fail tests

def test_index_log_in_existing_name(client_with_database_entry):
    client_with_database_entry.post('/login', data={"user-name": "existing user", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)

    assert b'it looks like that username already exists'

def test_index_log_in_wrong_password(client_with_database_entry):
    client_with_database_entry.post('/login', data={"user-name": "existing user", "user-email": "existing@email.com",
                                                    "user-password": "password123"}, follow_redirects=True)

    return b'WRONG PASSWORD'

# guesses tests

def test_index_guess_correct(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)

    user = database.query(User).first() # gets the only user
    user.number_secret = 8
    user.save() # sets and saves secret number so we know what it is

    response = client_empty_database.post('/', data={"number-input": "8"}) # enters correct number and gets back response
                                                                           # (must be in the same line! if you first post the data and then get a response it does not work)

    assert b'Great success' in response.data

def test_index_guess_too_high(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)

    user = database.query(User).first() # gets the only user
    user.number_secret = 8
    user.save() # sets and saves secret number so we know what it is

    response = client_empty_database.post('/', data={"number-input": "9"}) # enters higher number and gets back response

    assert b'too high!' in response.data

def test_index_guess_too_low(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)

    user = database.query(User).first() # gets the only user
    user.number_secret = 8
    user.save() # sets and saves secret number so we know what it is

    response = client_empty_database.post('/', data={"number-input": "7"}) # enters lower number and gets back response

    assert b'too low!' in response.data

# profile tests

def test_profile(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                              "user-password": "password123"}, follow_redirects=True)
    user = database.query(User).first() # gets the only user

    # encodes user information in to bytes (same as b'' does)
    user_name = user.name.encode('UTF8')
    email = user.email.encode('UTF8')

    response = client_empty_database.get("/profile")

    # tests if correct user name and email are displayed (and correct page with it)
    assert user_name in response.data
    assert email in response.data

def test_profile_edit(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)

    # changes (posts) new user name and email
    response = client_empty_database.post('/profile/edit', data={"profile-name": "Test User 2",
                                                  "profile-email": "test2@user.com"}, follow_redirects=True) #

    assert b'Test User 2' in response.data
    assert b'test2@user.com' in response.data

 ## add tests

# cleans up/deletes the database (drop all tables in the database)
def cleanup():
    database.drop_all()