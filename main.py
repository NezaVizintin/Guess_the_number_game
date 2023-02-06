from functions import *
from flask import Flask, render_template, request, redirect, url_for
from models import User, database
import uuid

app = Flask(__name__)
database.create_all() # creates (new) tables in the database

#TODO izboljšave (glej discord temo)

# creates main page, takes user input (number guesses) and generates appropriate response
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET": # what you take from the server
        user = user_check() # checks if there is a cookie with the user's email and creates a user object if there is
        response = response_number_guesses("index.html", "main", user, None, None, None) # creates a response - renders template including the variable with the secret number

        return response

    # secret number game
    elif request.method == "POST": # what you tell the server
        user = user_check()
        number_secret = user.number_secret # gets secret number for this user from the database
        number_input = int(request.form.get("number-input")) # gets user input number from website form

        # checks the secret number and creates appropriate response
        if number_input >= 30 or number_input <= 0: # user entered invalid number
            response = response_number_guesses("index.html", "main", user, True, "invalid", None)
        elif number_input == number_secret: # correct guess
            response = response_number_guesses("index.html", "success", user, False, None, number_input)
            # if numbers match, makes response, sets a new secret number and creates a cookie with it
            user.number_secret = number_secret_generate()
            user.save()
        elif  number_input < number_secret: # user's number is too low
            response = response_number_guesses("index.html", "main", user, True, "higher", None) #TODO: če sam "success" namesto "main", test ne zazna napake
        elif number_input > number_secret: # user's number is too high
            response = response_number_guesses("index.html", "main", user, True, "lower", None)

        return response

# takes input from user (name, email, password) and reloads the page with given information:
@app.route("/login", methods=["POST"])
def login():
    # gets data from form
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    user = database.query(User).filter_by(email=email).first() # checks if user already exists using the user entered email and creates user object
    hashed_password = password_hash(password) # hashes the user entered password
    number_secret = number_secret_generate() # generates secret number

# POPRAVI! ČE VPIŠEM NAROBNO IME IN MATCHING PASSWORD IN EMAIL ME VPIŠE

    if not user: # if a user with that email doesn't exist
        if database.query(User).filter_by(name=name).first(): # checks if there is already a user with the name the current user entered and responds
            return "Gosh, it looks like that username already exists with a different email." \
                   " If you already have an account login using the right email. Otherwise try another name to create a new account."
        else: # if the NEW user entered a unique name
            # creates the new User object in the database
            user = User(name=name, email=email, password=hashed_password, number_secret=number_secret)
            user.save()

    if name != user.name:
        return "Gosh, it looks like that name already exists." \
                " If you already have an account login using the right name. Otherwise try another email to create a new account." # AVTOMATIZIRAJ TEST

    elif hashed_password != user.password: # check if password is incorrect
        return "WRONG PASSWORD! :O Go back and try again."

    if hashed_password == user.password:
        # creates a random session token for this user
        session_token = str(uuid.uuid4())

        # saves session_token in the database
        user.session_token = session_token
        user.save()

        # creates response, saves session token in a cookie
        response = response_redirect_index() # creates response that will redirect to the index function (refreshes the site)
        response.set_cookie("session_token", session_token, httponly=True, samesite="Strict") # sets cookie with the session token to recognise the user until the session expires or they log out
                                                                                            # httponly=True - cookie cannot be accessed via JavaScript. JS can be used to hack the site
                                                                                            # secure=True can be added, which would mean cookies can only be sent via HTTPS. Internet protocols that are NOT HTTPS are not secure.
                                                                                            # Beware - this would mean cookies would not work on localhost, because localhost uses HTTP (and not HTTPS).
        return response

# renders logged in user's profile
@app.route("/profile", methods=["GET"])
def profile():
    user = user_check()

    if user:
        return render_template("profile.html", user=user)
    else:
        return response_redirect_index()

# edits logged in user's information
@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    user = user_check()

    if request.method == "GET": # checks the type of the request
        if user:  # if user is found
            return render_template("profile_edit.html", user=user)
        else:
            return response_redirect_index()
    elif request.method == "POST":
        # gets form input
        name = request.form.get("profile-name")
        email = request.form.get("profile-email")
        password_old = request.form.get("profile-password-old")
        password_new_1 = request.form.get("profile-password-new-1")
        password_new_2 = request.form.get("profile-password-new-2")

        # checks if password fields were entered correctly and if they were updates user object with new password, if not an appropriate response is given
        if password_old and password_new_1 and password_new_2:
            password_old = password_hash(password_old)
            password_new_1 = password_hash(password_new_1)
            password_new_2 = password_hash(password_new_2)
            if password_old == user.password:
                if password_new_1 == password_new_2:
                    user.password = password_new_1
                else:
                    return "The new passwords you entered do not match. Please go back and try again."
            else:
                return "The old (current) password you entered is not correct. Please go back and try again."
        elif password_old or password_new_1 or password_new_2:
            return "You didn't enter all three passwords. You must enter your old (current) password and your new password TWICE. Please go back and try again."

        # updates the user object and stores changes
        user.name = name
        user.email = email
        user.save()

        return redirect(url_for("profile"))

# fake deletes logged in user's profile
@app.route("/profile/delete", methods=["GET", "POST"])
def profile_delete():
    user = user_check()

    if request.method == "GET":
        if user:
            return render_template("profile_delete.html", user=user)
        else:
            return response_redirect_index()
    elif request.method == "POST":
        # user.delete()  deletes user from the database forever
        user.deleted = True # fake deletes the user in the database (they no longer show up but can be reactivated)
        user.save()

        return response_redirect_index()

# renders page displaying all users
@app.route("/users", methods=["GET"])
def users():
    user = user_check()

    if user:
        users = user_get_all()

        return render_template("users.html", users=users)
    else:
        return response_redirect_index()

# renders page for each user using their ID
@app.route("/user/<user_id>", methods=["GET"]) # <user_id> takes whatever is entered (in this case through users.html) and puts it into the user_id variable
                                               # So if the id 3 is entered here, it will store 3 in the user_id variable. We can then use user_id in our handler code (to get the user object from the database).
def user_details(user_id):
    user = user_get_with_id(user_id)

    return render_template("user_details.html", user=user)

# deletes session and reloads page
@app.route("/logout", methods=["GET"])
def logout():
    response = response_redirect_index()
    response.set_cookie("session_token", "session_token", expires=0)

    return response

if __name__ == "__main__":
    app.run(use_reloader=True)

# PREEXISTING CODE FOR REFERENCE
# while True:
#     main_menu = str(input("Would you like to A) play a new game, B) see the best scores, or C) quit? ")).lower()
#
#     if main_menu == "a":
#        print()
#        game_difficulty = str(input("Do you want to play the game with hints? (Y/N) ")).lower()
#        if game_difficulty == "y":
#            run_game_easy()
#        elif game_difficulty == "n":
#            run_game_hard()
#        else:
#            print()
#            print("Oh jeez, worng input. Next time select 'y' for YES and 'n' for NO.")
#            print()
#            continue
#
#     elif main_menu == "b":
#         top_score()
#     elif main_menu == "c":
#         break
#     else:
#         print("Oh no, wrong input. Please enter 'a', 'b', or 'c'.")
