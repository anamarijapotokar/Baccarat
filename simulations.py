from bacc import build_shoe, play_bacc
import matplotlib.pyplot as plt
import pandas as pd

# We repeated the simulation multiple times and the estimates were stable within about 0.1 percentage point, so we use random.seed for the sake of reproducibility of our results.
import random
random.seed(42)

# We simulate the game of Baccarat and compute the share of wins for each hand.
# From that, we calculate the house edge for each hand.

shoe = build_shoe()

hands_number = 10000

banker_win = 0
player_win = 0
tie = 0

banker_share = 0
player_share = 0
tie_share = 0

checkpoints = []
banker_ev_history = []
player_ev_history = []
tie_ev_history = []

step = 100

for i in range(1, hands_number + 1):
    result = play_bacc(shoe)
    if result == "Player":
        player_win += 1
    elif result == "Banker":
        banker_win += 1
    else:
        tie += 1
    
    if i % step == 0:
        # EV calculations
        banker_ev = (player_win * (-1) + banker_win * 0.95) / i
        player_ev = (player_win * 1 + banker_win * (-1)) / i
        tie_ev    = (tie * 8 + (i - tie) * (-1)) / i

        checkpoints.append(i)
        banker_ev_history.append(banker_ev)
        player_ev_history.append(player_ev)
        tie_ev_history.append(tie_ev)

# We calculate the share of wins for each bet.
banker_share = banker_win / hands_number
player_share = player_win / hands_number
tie_share = tie / hands_number

# We calcluate the house edge for each bet.
player_ev = (player_win * 1 + banker_win * (-1) + tie * 0) / hands_number
banker_ev = (player_win * (-1) + banker_win * 0.95 + tie * 0) / hands_number
tie_ev = (tie * 8 + (hands_number - tie) * (-1)) / hands_number
banker_no_commission_ev = (player_win * (-1) + banker_win * 1 + tie * 0) / hands_number

player_house_edge = -player_ev
banker_house_edge = -banker_ev
tie_house_edge    = -tie_ev
banker_no_commision_house_edge = -banker_no_commission_ev

print("Banker wins:", banker_win)
print("Player wins:", player_win)
print("Ties:", tie)
print()
print("Percentages")
print("Banker:", banker_share * 100, "%")
print("Player:", player_share * 100, "%")
print("Tie:", tie_share * 100, "%")
print()
print("EV per hand (Player bet):", player_ev)
print("EV per hand (Banker bet):", banker_ev)
print("EV per hand (Tie bet):", tie_ev)
print("EV per hand (Banker no commision bet):", banker_no_commission_ev)
print()
print("House edge estimates:")
print("Player bet:",  player_house_edge * 100, "%")
print("Banker bet:",  banker_house_edge * 100, "%")
print("Tie bet:   ",  tie_house_edge * 100, "%")
print("Banker no commision bet:",  banker_no_commision_house_edge * 100, "%")

df = pd.DataFrame({
    "Outcome": ["Player", "Banker", "Tie"],
    "Win percentage": [player_share, banker_share, tie_share]
    
})

df.to_csv("baccarat_results.csv", index=False)

df2 = pd.DataFrame({
    "Outcome": ["Player", "Banker", "Tie"],
    "Expected value": [player_ev, banker_ev, tie_ev]
    
})

df2.to_csv("baccarat_EV.csv", index=False)


bets = ["Player", "Banker", "Tie", "Banker brez comisson"]

evs = [player_ev, banker_ev, tie_ev, banker_no_commission_ev]

        


plt.figure(figsize=(4,3))
plt.bar(bets, evs)
plt.axhline(0, linewidth=1)
plt.title("EV na stavo")
plt.xticks(rotation=15)
plt.grid(axis="y", alpha=0.3)

plt.savefig("ev_per_bet.png", dpi=300, bbox_inches="tight")
plt.close()



plt.figure(figsize=(4,3))

plt.plot(checkpoints, banker_ev_history, label="Banker")
plt.plot(checkpoints, player_ev_history, label="Player")
plt.plot(checkpoints, tie_ev_history, label="Tie")

plt.axhline(0, linewidth=1)

plt.xlabel("Število iger")
plt.ylabel("EV na stavo")
plt.title("EV konvergenca")
plt.legend()
plt.grid(alpha=0.3)

plt.savefig("ev_konvergenca.png", dpi=300, bbox_inches="tight")
plt.close()
