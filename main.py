from functions import *
from flask import Flask, render_template, request, make_response

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET": #what you take from the server
        number_secret = request.cookies.get("number_set") #get the set secret number
        if not isinstance(number_secret, str) or not number_secret.isnumeric():
            number_secret = number_secret_generate() #checks if there already is a secret number and generates one if there isn't

        response = make_response(render_template("index.html", head="main", number_secret=number_secret)) #creates a response - renders template including the variable with the secret number
        response.set_cookie("number_set", str(number_secret)) #creates cookie with the secret number

        return response

    elif request.method == "POST": #what you tell the server
        number_secret = int(request.cookies.get("number_set")) #gets cookie with secret number
        number_input = int(request.form.get("number-input")) #gets user input number from website form

        if number_input >= 30 or number_input <= 0:
            response = make_response(render_template("index.html", head="main", incorrect=True, guess="invalid", number_secret=number_secret))
        elif number_input == number_secret: # if numbers match, makes response, sets a new secret number and creates a cookie with it
            response = make_response(render_template("index.html", head="success", incorrect=False, number=number_input, number_secret=number_secret))
            number_secret_new = number_secret_generate()
            response.set_cookie("number_set", str(number_secret_new))
        elif  number_input < number_secret:
            response = make_response(render_template("index.html", head="main", incorrect=True, guess="higher", number_secret=number_secret))
        elif number_input > number_secret:
            response = make_response(render_template("index.html", head="main", incorrect=True, guess="lower", number_secret=number_secret))

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
