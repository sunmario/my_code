# Write your code here

from random import choice
default_options = ["rock", "paper", "scissors"]
players_name = input("Enter your name: ")
# [rock,gun,lightning,devil,dragon,water,air,paper,sponge,wolf,tree,human,snake,scissors,fire]
print("Hello, {}".format(players_name))
options = input()
if options == "":
    seq = default_options
else:
    seq = options.split(",")
print("Okay, let's start")
file = open("rating.txt", "r")
ratings = file.readlines()
file.close()
your_score = 0
for i in range(len(ratings)):
    if ratings[i].startswith(players_name):
        your_score = int(ratings[i].split(" ")[1])
        break


def determine_choices(choices, made_choice):
    choices_copy = choices.copy()
    chosen = 0
    for i in range(len(choices_copy)):
        if choices_copy[i] == made_choice:
            del choices_copy[i]
            chosen = i
            break
    choices_copy = choices_copy[chosen:] + choices_copy[:chosen]
    win = choices_copy[:len(choices_copy)//2]
    lose = choices_copy[len(choices_copy)//2:]
    #print(win)
    #print(lose)
    return win, lose



players_choice = input("Your turn: ").lower()

while players_choice != "!exit":
    if players_choice == "!rating":
        print("Your rating: {}".format(your_score))
    else:
        if players_choice in seq:
            computer_choice = choice(seq)
            win_over, lose_over = determine_choices(seq, computer_choice)
            if players_choice == computer_choice:
                print("There is a draw", players_choice)
                your_score += 50
            elif players_choice in lose_over:
                print("Sorry, but the computer chose {}".format(computer_choice))
            elif players_choice in win_over:
                print("Well done. The computer chose {} and failed".format(computer_choice))
                your_score += 100
        else:
            print("Invalid input")
    players_choice = input().lower()
final_score = players_name + " " + str(your_score)
for i in range(len(ratings)):
    if ratings[i].startswith(players_name):
        ratings[i] = final_score
    else:
        ratings.append(final_score)
file = open("rating.txt", "w")
for i in ratings:
    file.write(i)
file.close()

