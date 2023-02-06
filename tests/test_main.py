import os
import pytest

# important: this line needs to be set BEFORE the "app" import AND User import (otherwise it imports and pytest edits the database, not the virtual one)
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from main import app, database
from models import User


@pytest.fixture
# takes the Flask app from main.py and prepares it for testing
def client_empty_database():
    client = app.test_client()

    cleanup()  # deletes the database before every test (so that we have a clean slate before every test)

    database.create_all()  # NOTE: tests do not use your real localhost database (localhost.sqlite), but instead create a temporary database that lives only inside computer's RAM (sqlite:///:memory:)

    yield client  # NOTE: https://www.pythonforbeginners.com/basics/difference-between-yield-and-return-in-python#htoc-what-is-yield-and-return-in-python


@pytest.fixture
def client_with_database_entry():
    client = app.test_client()

    cleanup()

    database.create_all()
    user = User(name="existing user", email="existing@email.com", password="existingPassword",
                number_secret="8")  # creates single entry in database
    user.save()

    yield client

# ----- basic page rendering tests -----

def test_index_not_logged_in(client_empty_database):  # the name of the function and the name of the test file starts with test_.
                                                      # NOTE: This tells the pytest library that these are our automated tests
    response = client_empty_database.get('/')  # sends a GET request to the / URL (where the index() handler is located) and receives back a response

    assert b'Enter your username' in response.data  # NOTE: this is the actual test. Checks (assert) if the data in the response (in our case, the HTML document) has a string 'Enter your name' inside.
                                                    # NOTE: the b in front of a string just means that Python will convert the string into byte code since that's the format of response.data

def test_profile(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)

    user = database.query(User).first()  # gets the only user

    # encodes user information in to bytes (same as b'' does) NOTE: unnecessary but I wanted to try it
    user_name = user.name.encode('UTF8')
    email = user.email.encode('UTF8')

    response = client_empty_database.get("/profile") # gets profile page

    # tests if correct user name and email are displayed (and correct page with it)
    assert user_name in response.data
    assert email in response.data


def test_all_users(client_with_database_entry):
    # logs in
    client_with_database_entry.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)

    response = client_with_database_entry.get('/users') # gets all users page

    # tests if both user names are displayed
    assert b'Test User' in response.data
    assert b'existing user' in response.data

def test_user_details(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)

    response = client_empty_database.get('/user/1') # gets user details page from only user

    assert b'test@user.com' in response.data # tests if user's email is displayed

# ----- log in/log out tests -----

def test_index_logged_in(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)  # NOTE: In the post request specify both the handler URL and also the data you want to send into the handler.
                                                                                                        # NOTE: For login we sent "user-name", "user-email" and "user-password"
    response = client_empty_database.get('/') # gets index page

    assert b'Guess and press enter' in response.data # tests if correct page is rendered

def test_index_log_in_with_existing_name(client_with_database_entry):
    # logs in with existing name and new email
    response = client_with_database_entry.post('/login', data={"user-name": "existing user","user-email": "test@user.com",
                                                               "user-password": "password123"}, follow_redirects=True)

    assert b'it looks like that username already exists' in response.data # tests if appropriate error response is given


def test_index_log_in_wrong_password(client_with_database_entry):
    # logs in with incorrect password
    response = client_with_database_entry.post('/login', data={"user-name": "existing user", "user-email": "existing@email.com",
                                                     "user-password": "password123"}, follow_redirects=True)

    assert b'WRONG PASSWORD' in response.data # tests if appropriate error response is given


def test_log_out(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)

    response = client_empty_database.get('/logout', follow_redirects=True) # logs user out

    assert b'Enter your username' in response.data # tests if login page is rendered (user is logged out)


# guesses tests

def test_index_guess_correct(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)

    user = database.query(User).first()  # gets the only user
    # sets and saves secret number so we know what it is
    user.number_secret = 8
    user.save()

    response = client_empty_database.post('/', data={"number-input": "8"})  # enters correct number and gets back response
                                                                            # NOTE: must be in the same line! if you first post the data and then get a response it does not work

    assert b'Great success' in response.data


def test_index_guess_too_high(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)

    user = database.query(User).first()  # gets the only user
    # sets and saves secret number so we know what it is
    user.number_secret = 8
    user.save()

    response = client_empty_database.post('/', data={"number-input": "9"})  # enters higher number and gets back response

    assert b'too high!' in response.data


def test_index_guess_too_low(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)

    user = database.query(User).first()  # gets the only user
    # sets and saves secret number so we know what it is
    user.number_secret = 8
    user.save()

    response = client_empty_database.post('/', data={"number-input": "7"})  # enters lower number and gets back response

    assert b'too low!' in response.data

#TODO def test_index_guess_wrong_input


# edit and delete profile tests

def test_profile_edit_name_and_email(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)

    # changes (posts) new user name and email
    response = client_empty_database.post('/profile/edit', data={"profile-name": "Test User 2",
                                                                 "profile-email": "test2@user.com"}, follow_redirects=True)

    # tests if new user data was changed correctly
    assert b'Test User 2' in response.data
    assert b'test2@user.com' in response.data


def test_profile_edit_password_missing_fields(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)


    response = client_empty_database.post('/profile/edit', data={"profile-password-old": "password123"}, follow_redirects=True) # posts one password field

    assert b'You must enter your old (current) password and your new password TWICE' in response.data # tests if user gets correct error message


def test_profile_edit_password_new_passwords_not_matching(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)

    # posts correct old password and new passwords that don't match
    response = client_empty_database.post('/profile/edit', data={"profile-password-old": "password123",
                                                                 "profile-password-new-1": "password123456",
                                                                 "profile-password-new-2": "password"}, follow_redirects=True)

    assert b'The new passwords you entered do not match' in response.data # tests if user gets correct error message


def test_profile_edit_password_old_password_not_correct(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)

    # posts wrong current user password
    response = client_empty_database.post('/profile/edit', data={"profile-password-old": "passwordWRONG",
                                                                 "profile-password-new-1": "password123",
                                                                 "profile-password-new-2": "password123"}, follow_redirects=True)

    assert b'The old (current) password you entered is not correct.' in response.data


def test_profile_delete(client_empty_database):
    # logs in
    client_empty_database.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                               "user-password": "password123"}, follow_redirects=True)

    # deletes profile
    response = client_empty_database.post('/profile/delete', follow_redirects=True)

    assert b'Enter your username' in response.data # tests if log in is now requested



# def test_profile_edit_password_correctly(client_with_database_entry): KAKO TESTIRAT, ČE SE JE SHRANIL NOV PASSWORD? ČE SE USER IZPIŠE TEST NIKAKOR NE FAILA Z NAPAČNIMI PODATKI (SE BAZAZBRIŠE?)
#     # logs in
#     client_with_database_entry.post('/login', data={"user-name": "existing user", "user-email": "existing@email.com",
#                                                "user-password": "existingPassword"}, follow_redirects=True)
#
#     response = client_with_database_entry.post('/profile/edit', data={"profile-password-old": "existingPassword", "profile-password-new-1": "password1234",
#                                                                  "profile-password-new-2": "password1234"}, follow_redirects=True)
#
#     assert b'Your name' in response.data

# client_with_database_entry.get('/logout', follow_redirects=True)
#
# response = client_with_database_entry.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
#                                            "user-password": "password1234"}, follow_redirects=True)
#
# assert b'Guess and press enter' in response.data

## add tests

# cleans up/deletes the database (drop all tables in the database)
def cleanup():
    database.drop_all()
