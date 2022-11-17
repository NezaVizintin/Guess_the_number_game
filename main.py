from functions import *
from flask import Flask, render_template, request, make_response, redirect, url_for, session
from models import User, database
import uuid, hashlib

app = Flask(__name__)
database.create_all() # creates (new) tables in the database

# TO-DO: naredi response v funkcijo, da samo dodas potrebne argumente (ne da vsakič vse piše), izboljšave (glej discord temo)

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

@app.route("/login", methods=["POST"])
def login():
    # gets data from form
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    user = database.query(User).filter_by(email=email).first()
    hashed_password = hashlib.sha3_256(password.encode()).hexdigest() # hashes the password

    if not user:
        # create a User object
        user = User(name=name, email=email, password=hashed_password)
        user.save()

    if not user.number_secret:
        user.number_secret = number_secret_generate()
        user.save()

    if hashed_password != user.password: # check if password is incorrect
        return "WRONG PASSWORD! Go back and try again."
    elif hashed_password == user.password:
        # creates a random session token for this user
        session_token = str(uuid.uuid4())

        # saves it in the database
        user.session_token = session_token
        user.save()

        # creates response
        response = make_response(redirect(url_for("index"))) # creates response that will redirect to the index function (refreshes the site)
        response.set_cookie("session_token", session_token, httponly=True, samesite="Strict") # sets cookie with the new email (if id doesn't exist yet) or saves the existig email in to a cookie to recognise the user
                                                                                            # httponly=True - cookie cannot be accessed via JavaScript. JS can be used to hack the site
                                                                                            # Thirdly you can also add secure=True, which would mean cookies can only be sent via HTTPS. Internet protocols that are NOT HTTPS are not secure.
                                                                                            # But beware that this would mean cookies would not work on localhost, because your localhost uses HTTP (and not HTTPS).
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
