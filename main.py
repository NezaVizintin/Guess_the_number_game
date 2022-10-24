from functions import *
from flask import Flask, render_template, request, make_response

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET": #what you take from the server
        number_secret = int(request.cookies.get("number_set")) #get the set secret number
        number_secret = number_secret_generate() if not number_secret else number_secret #checks if there already is a secret number and generates one if there isn't

        response = make_response(render_template("index.html", number_secret=number_secret)) #creates a response - renders template including the variable with the secret number
        response.set_cookie("number_set", str(number_secret)) #creates cookie with the secret number

        return response

    elif request.method == "POST": #what you tell the server
        number_secret = int(request.cookies.get("number_set")) #gets cookie with secret number
        number_input = int(request.form.get("number-input")) #gets user input number from website form

        if number_input == number_secret: # if numbers match, makes response, sets a new secret number and creates a cookie with it
            response = make_response(render_template("correct.html"))
            number_secret_new = number_secret_generate()
            response.set_cookie("number_set", str(number_secret_new))

        else:
            response = make_response(render_template("index.html", number=number_input, number_secret=number_secret))

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
