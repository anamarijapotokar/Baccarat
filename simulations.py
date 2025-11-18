from bacc import build_shoe, play_bacc
import matplotlib.pyplot as plt

shoe = build_shoe()

hands_number = 10000

banker_win = 0
player_win = 0
tie = 0

banker_share = []
player_share = []
tie_share = []

for i in range(1, hands_number + 1):
    result = play_bacc(shoe)
    if result == "Player":
        player_win += 1
    elif result == "Banker":
        banker_win += 1
    else:
        tie += 1
    
    banker_share.append(banker_win / i)
    player_share.append(player_win / i)
    tie_share.append(tie / i)



print("Banker wins", banker_win)
print("Player wins", player_win)
print("Ties", tie)
print()
print("Percentages")
print("Banker", banker_win / hands_number * 100, "%")
print("Player", player_win / hands_number * 100, "%")
print("Tie", tie / hands_number * 100, "%")


plt.plot(banker_share, label="Banker %")
plt.plot(player_share, label="Player %")
plt.plot(tie_share, label="Tie %")

plt.xlabel("Hands played")
plt.ylabel("Win %")
plt.title("Share of wins")
plt.legend()
plt.show()