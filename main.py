from functions import *
from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, database

app = Flask(__name__)
database.create_all() # creates (new) tables in the database

# TO-DO: naredi response v funkcijo, da samo dodas potrebne argumente (ne da vsakič vse piše)

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
            response = make_response(render_template("index.html", head="main", user=user, incorrect=True, guess="invalid", number_secret=number_secret))
        # if numbers match, makes response, sets a new secret number and creates a cookie with it
        elif number_input == number_secret: # correct guess
            response = make_response(render_template("index.html", head="success", user=user, incorrect=False, number=number_input, number_secret=number_secret))
            user.number_secret = number_secret_generate()
            user.save()
        elif  number_input < number_secret: # user's number is too low
            response = make_response(render_template("index.html", head="main", user=user, incorrect=True, guess="higher", number_secret=number_secret))
        elif number_input > number_secret: # user's number is too high
            response = make_response(render_template("index.html", head="main", user=user, incorrect=True, guess="lower", number_secret=number_secret))

        return response

@app.route("/login", methods=["POST"])
def login():
    # gets data from form
    name = request.form.get("user-name")
    email = request.form.get("user-email")

    try: # tries to save the data in to the database as a new user - if the email already exists this will fail
        user = User(name=name, email=email)  # creates a User object
        user.save() # saves the user object into the database
    except: # if the user exists it creates that user as a a User object
        user = database.query(User).filter_by(email=email).first()

    if not user.number_secret:
        user.number_secret = number_secret_generate()
        user.save()


    response = make_response(redirect(url_for("index"))) # creates response that will redirect to the index function (refreshes the site)
    response.set_cookie("email", email) # sets cookie with the new email (if id doesn't exist yet) or saves the existig email in to a cookie to recognise the user

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
