import json
import datetime
import operator
import random

def number_secret_generate():
    secret = random.randint(1, 30)
    return secret

# PREEXISTING CODE FOR REFERENCE
#
# def run_game_easy():
#     wrong_guesses = []
#     name = input("Enter player name: ")
#     attempts = 0
#     while True:
#         print()
#         print("Previous guesses: " + str(wrong_guesses))
#         guess = input("Guess the secret number (between 1 and 30): ")
#         print()
#
#         try:
#             guess = int(guess)
#         except:
#             print("Oops, that's not a valid number. Please enter a number between (including) 1 and 30.")
#
#         if guess == secret:
#             score_list = get_top_score()
#             score_list.append({"attempts": attempts, "date": str(datetime.datetime.now()), "name": name, "wrong_guesses": wrong_guesses})
#             with open("score_list.json", "w") as score_file:
#                 score_file.write(json.dumps(score_list))
#             print("You guessed it! The secret number is " + str(guess))
#             print("Attempts needed: " + str(attempts))
#             break
#         elif guess < secret:
#             wrong_guesses.append(guess)
#             attempts += 1
#             print("Not quite there, try going a bit higher!")
#         elif guess > secret:
#             wrong_guesses.append(guess)
#             attempts += 1
#             print("Not quite there, try going a bit lower!")
#
#
# def run_game_hard():
#     wrong_guesses = []
#     secret = random.randint(1, 30)
#     name = input("Enter player name: ")
#     attempts = 0
#     while True:
#         print()
#         print("Previous guesses: " + str(wrong_guesses))
#         guess = input("Guess the secret number (between 1 and 30): ")
#         print()
#
#         try:
#             guess = int(guess)
#
#             if guess == secret:
#                 score_list = get_top_score()
#                 # -------- improve score list so that it stores game difficulty and shows top results for each  --------
#                 score_list.append({"attempts": attempts, "date": str(datetime.datetime.now()), "name": name, "wrong_guesses": wrong_guesses})
#                 with open("score_list.json", "w") as score_file:
#                     score_file.write(json.dumps(score_list))
#                 print("You guessed it! The secret number is " + str(guess))
#                 print("Attempts needed: " + str(attempts))
#                 break
#             elif guess < secret:
#                 wrong_guesses.append(guess)
#                 attempts += 1
#                 print("Not quite there, try again!")
#             elif guess > secret:
#                 wrong_guesses.append(guess)
#                 attempts += 1
#                 print("Not quite there, try again!")
#         except:
#             print("Oops, that's not a valid number. Please enter a number between (including) 1 and 30.")
#
# def get_top_score(): # retrieves score list
#     with open("score_list.json", "r") as score_file:  # opens score file to read
#         return json.loads(score_file.read())
#
# def top_score(): # prints top 3 scores
#     print("Top scores: ")
#     score_list = get_top_score()
#     if score_list: # checks it score_list is empty
#         score_list.sort(key=operator.itemgetter('attempts')) #sorts score_list by best score ascending
#         for x in range(3): # shows top 5 results
#             print(score_list[x].get("name") + ": " + str(score_list[x]["attempts"]) + " attempts, date: " + score_list[x].get("date"))
