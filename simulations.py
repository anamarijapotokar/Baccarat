from bacc import build_shoe, play_bacc

shoe = build_shoe()

hands_number = 100000

banker_win = 0
player_win = 0
tie = 0


for i in range(hands_number):
    result = play_bacc(shoe)
    if result == "Player":
        player_win += 1
    elif result == "Banker":
        banker_win += 1
    else:
        tie += 1



print("Banker wins", banker_win)
print("Player wins", player_win)
print("Ties", tie)
print()
print("Percentages")
print("Banker", banker_win / hands_number * 100, "%")
print("Player", player_win / hands_number * 100, "%")
print("Tie", tie / hands_number * 100, "%")