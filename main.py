from functions import *
from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, database
import uuid

app = Flask(__name__)
database.create_all() # creates (new) tables in the database

# TO-DO: naredi response v funkcijo, da samo dodas potrebne argumente (ne da vsakič vse piše), izboljšave (glej discord temo)

# creates main page, takes user input (number guesses) and generates appropriate response
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET": # what you take from the server
        user = user_check() # checks if there is a cookie with the user's email and creates a user object if there is
        response = make_response(render_template("index.html", head="main", user=user)) # creates a response - renders template including the variable with the secret number

        return response

    elif request.method == "POST": # what you tell the server
        user = user_check()
        number_secret = user.number_secret # gets secret number for this user from the database
        number_input = int(request.form.get("number-input")) # gets user input number from website form

        # checks the secret number and creates appropriate response
        if number_input >= 30 or number_input <= 0: # user entered invalid number
            response = make_response(render_template("index.html", head="main", user=user, incorrect=True, guess="invalid"))
        # if numbers match, makes response, sets a new secret number and creates a cookie with it
        elif number_input == number_secret: # correct guess
            response = make_response(render_template("index.html", head="success", user=user, incorrect=False, number=number_input))
            user.number_secret = number_secret_generate()
            user.save()
        elif  number_input < number_secret: # user's number is too low
            response = make_response(render_template("index.html", head="main", user=user, incorrect=True, guess="higher"))
        elif number_input > number_secret: # user's number is too high
            response = make_response(render_template("index.html", head="main", user=user, incorrect=True, guess="lower"))

        return response

# takes input from user (name, email, password) and reloads the page with given information:
@app.route("/login", methods=["POST"])
def login():
    # gets data from form
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    user = database.query(User).filter_by(email=email).first() # sees if user already exists
    hashed_password = password_hash(password) # hashes the password
    number_secret = number_secret_generate() # generates secret number

    if not user:
        # create a User object
        user = User(name=name, email=email, password=hashed_password, number_secret=number_secret)
        user.save()

    if hashed_password != user.password: # check if password is incorrect
        return "WRONG PASSWORD! Go back and try again."
    elif hashed_password == user.password:
        # creates a random session token for this user
        session_token = str(uuid.uuid4())

        # saves session_token in the database
        user.session_token = session_token
        user.save()

        # creates response, saves session token in a cookie
        response = make_response(redirect(url_for("index"))) # creates response that will redirect to the index function (refreshes the site)
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
        return redirect(url_for("index"))

# edits logged in user's information
@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    user = user_check()

    if request.method == "GET": # checks the type of the request
        if user:  # if user is found
            return render_template("profile_edit.html", user=user)
        else:
            return redirect(url_for("index"))
    elif request.method == "POST":
        # gets form input
        name = request.form.get("profile-name")
        email = request.form.get("profile-email")
        password_old = password_hash(request.form.get("profile-password-old"))
        password_new_1 = password_hash(request.form.get("profile-password-new-1"))
        password_new_2 = password_hash(request.form.get("profile-password-new-2"))

        # checks if password fields were entered correctly and if they were updates user object with new password, if not an appropriate response is given
        if password_old and password_new_1 and password_new_2:
            if password_old == user.password:
                if password_new_1 == password_new_2:
                    user.password = password_new_1
                else:
                    return "The new passwords you entered do not match. Please go back and try again."
            else:
                return "The old (current) password you entered is not correct. Please go back and try again."
        else:
            return "You forgot to enter all three password fields. You must enter your old (current) password and your new password TWICE. Please go back and try again."

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
            return redirect(url_for("index"))
    elif request.method == "POST":
        # user.delete()  deletes user from the database forever
        user.deleted = True # fake deletes the user in the database (they no longer show up but can be reactivated)
        user.save()

        return redirect(url_for("index"))

# renders page displaying all users
@app.route("/users", methods=["GET"])
def users():
    users = user_get_all()

    return render_template("users.html", users=users)

# renders page for each user using their ID
@app.route("/user/<user_id>", methods=["GET"]) # <user_id> takes whatever is entered (in this case through users.html) and puts it into the user_id variable
                                               # So if the id 3 is entered here, it will store 3 in the user_id variable. We can then use user_id in our handler code (to get the user object from the database).
def user_details(user_id):
    user = user_get_with_id(user_id)

    return render_template("user_details.html", user=user)

# deletes session and reloads page
@app.route("/logout", methods=["GET"])
def logout():
    response = make_response(redirect(url_for("index")))
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
