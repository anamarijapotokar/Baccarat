import matplotlib.pyplot as plt
import pandas as pd


# First we define a new function whose output will tell us given what actully happened in the game
# and what we bet on, how much money do we win or lose.
def settle_bet(outcome, bet_type, stake, commission=0.05):

    if bet_type == "Player":
        if outcome == "Player":
            return stake
        elif outcome == "Banker":
            return -stake
        else:
            return 0

    elif bet_type == "Banker":
        if outcome == "Banker":
            return stake * (1 - commission)
        elif outcome == "Player":
            return -stake
        else:
            return 0

    elif bet_type == "Tie":
        if outcome == "Tie":
            return stake * 8
        else:
            return -stake


from bacc import build_shoe, play_bacc

hands_number = 100000
initial_bankroll = 100
base_bet = 1
bet_type = "Player"  # or Player or Tie

# Generating the outcomes once:
shoe = build_shoe()
outcomes = []
for i in range(hands_number):
    outcome = play_bacc(shoe)
    outcomes.append(outcome)

# FIRST STRATEGY: FLAT BETTING
# With this strategy you bet the same amount every hand, so there's no 'system' to recover losses.
def simulate_flat(outcomes, initial_bankroll, base_bet, bet_type):
    bankroll = initial_bankroll
    path = []

    for outcome in outcomes:
        if bankroll <= 0:
            path.append(0)
            continue

        profit = settle_bet(outcome, bet_type, base_bet)
        bankroll += profit
        path.append(bankroll)

    return path

# SECOND STRATEGY: MARTINGALE
# You start with a base bet; if you lose, you double your next bet, and if you win, you reset back to the base bet.
# So the idea is that one win recovers all previous losses and also gives us a small profit.
# The problem is that you very quickly hit either the table limit or your bankroll limit, and then blow up.
def simulate_martingale(outcomes, initial_bankroll, base_bet, bet_type):
   
    bankroll = initial_bankroll
    path = []
    current_bet = base_bet

    for outcome in outcomes:
        if bankroll <= 0:
            path.append(0)
            continue

        # Make sure we don't bet more than what we have
        stake = min(current_bet, bankroll)
        profit = settle_bet(outcome, bet_type, stake)
        bankroll += profit
        path.append(bankroll)

        if profit > 0:
            # Win: reset to base bet
            current_bet = base_bet
        else:
            # Loss: double it, but don't exceed bankroll
            current_bet = min(current_bet * 2, bankroll)

    return path

# THIRD STRATEGY: REVERSE MARTINGALE (PAROLI)
# You start with a base bet; if you win, you double the next bet, and if you lose, you reset back to the base bet.
def simulate_paroli(outcomes, initial_bankroll, base_bet, bet_type, max_bet=None):
    
    bankroll = initial_bankroll
    path = []
    current_bet = base_bet
    if max_bet is None:
        max_bet = initial_bankroll 

    for outcome in outcomes:
        if bankroll <= 0:
            path.append(0)
            continue

        stake = min(current_bet, bankroll)
        profit = settle_bet(outcome, bet_type, stake)
        bankroll += profit
        path.append(bankroll)

        if profit > 0:
            current_bet = min(current_bet * 2, max_bet)
        else:
            current_bet = base_bet

    return path


# FOURTH STRATEGY: D'ALEMBERT/FIBONACCI SYSTEMS
# The common idea is step-wise adjustment. 
#   D'Alembert system: you start with a base bet; after a loss, you increase the bet by 1 unit (1->2->3->...), and after a win, you decrease it but 1 unit (but not below the base).
#                      So the idea is to slowly balance wins and losses instead of huge jumps like Martingale.
#   Fibonacci system: you start with a base bet; after a loss, you go one step forward in the Fibonacci sequence 8(bet more), and after a win, you typically go 2 steps back in the Fibonacci sequence.
#                     It's similar to Martingale in trying to recover past losses, but increases are slower than doubling.
def simulate_dalembert(outcomes, initial_bankroll, base_bet, bet_type):
    
    bankroll = initial_bankroll
    path = []
    current_bet = base_bet

    for outcome in outcomes:
        if bankroll <= 0:
            path.append(0)
            continue

        stake = min(current_bet, bankroll)
        profit = settle_bet(outcome, bet_type, stake)
        bankroll += profit
        path.append(bankroll)

        if profit > 0:
            current_bet = max(base_bet, current_bet - 1)
        else:
            current_bet = current_bet + 1

    return path

# RUNNING AND COMPARING
flat_results = simulate_flat(outcomes, initial_bankroll, base_bet, bet_type)
martingale_results = simulate_martingale(outcomes, initial_bankroll, base_bet, bet_type)
paroli_results     = simulate_paroli(outcomes, initial_bankroll, base_bet, bet_type)
dalembert_results  = simulate_dalembert(outcomes, initial_bankroll, base_bet, bet_type)

# Check if/when each strategy went broke
def ruin_time(path):
    for i, b in enumerate(path, start=1):
        if b <= 0:
            return i
    return None

flat_ruin = ruin_time(flat_results)
martingale_ruin = ruin_time(martingale_results)
paroli_ruin = ruin_time(paroli_results)
dalembert_ruin = ruin_time(dalembert_results)

print(f"Final bankroll Flat: {flat_results[-1]}")
print(f"Final bankroll Martingale: {martingale_results[-1]}")
print(f"Final bankroll Paroli: {paroli_results[-1]}")
print(f"Final bankroll D'Alembert: {dalembert_results[-1]}")
print(f"Flat ruin at hand: {flat_ruin}")
print(f"Martingale ruin at hand: {martingale_ruin}")
print(f"Paroli ruin at hand: {paroli_ruin}")
print(f"D'Alembert ruin at hand: {dalembert_ruin}")

# Now we calculate the expected value per hand for each strategy and variance of bankroll changes.

import statistics as stats
import math

def strategy_stats(path, initial_bankroll):

    # profit/loss per hand
    changes = []
    last = initial_bankroll
    for p in path:
        changes.append(p - last) # for each hand we calculate profit = new - previous bankroll after each round
        last = p

    if len(changes) == 0:
        return 0, 0, 0

    ev_per_hand = stats.mean(changes)
    var_per_hand = stats.variance(changes)
    vol_per_hand = math.sqrt(var_per_hand)

    return ev_per_hand, var_per_hand, vol_per_hand

# Computing the stats for each strategy; ev will be the same for each strategy, the strategies only change how we lose, not how much
flat_ev, flat_var, flat_vol = strategy_stats(flat_results, initial_bankroll)
mart_ev, mart_var, mart_vol = strategy_stats(martingale_results, initial_bankroll)
par_ev, par_var, par_vol = strategy_stats(paroli_results, initial_bankroll)
dal_ev, dal_var, dal_vol = strategy_stats(dalembert_results, initial_bankroll)

print("Approximate stats per hand:")
print(f"Flat: EV = {flat_ev:.5f}, Var = {flat_var:.5f}, Vol = {flat_vol:.5f}")
print(f"Martingale: EV = {mart_ev:.5f}, Var = {mart_var:.5f}, Vol = {mart_vol:.5f}")
print(f"Paroli: EV = {par_ev:.5f}, Var = {par_var:.5f}, Vol = {par_vol:.5f}")
print(f"D'Alembert: EV = {dal_ev:.5f}, Var = {dal_var:.5f}, Vol = {dal_vol:.5f}")



num_simulations = 20      

            
strategies = {
    "Flat": simulate_flat,
    "Martingale": simulate_martingale,
    "Paroli": simulate_paroli,
    "D'Alembert": simulate_dalembert
}


def truncate_at_ruin(path):
    for i, b in enumerate(path, start=1):
        if b <= 0:
            return path[:i]
    return path


average_ruin_times = {}
for name, fn in strategies.items():
    ruin_times = []
    for sim in range(num_simulations):
        shoe = build_shoe()
        outcomes = [play_bacc(shoe) for _ in range(hands_number)]
        path = fn(outcomes, initial_bankroll, base_bet, bet_type)
        t = ruin_time(path)
        if t is not None:
            ruin_times.append(t)
    average_ruin_times[name] = (sum(ruin_times)/len(ruin_times)) if ruin_times else None



print(f"Average time to ruin over {num_simulations} simulations:")
for name, avg_time in average_ruin_times.items():
    if avg_time is not None:
        print(f"{name}: {avg_time:.1f} hands")
    else:
        print(f"{name}: no ruin observed in {num_simulations} simulations")



ruin_df = pd.DataFrame(list(average_ruin_times.items()), columns=["Strategy", "Average_Ruin_Hands"])

# Replace None with a descriptive string if you want
ruin_df["Average_Ruin_Hands"] = ruin_df["Average_Ruin_Hands"].apply(
    lambda x: x if x is not None else "No ruin observed"
)
ruin_df.to_csv("avg_ruin_time.csv", index=False)





max_hands = 3000

plt.figure(figsize=(4,3))
plt.plot(flat_results[:max_hands], label="Flat Betting")
plt.plot(martingale_results[:max_hands], label="Martingale")
plt.plot(paroli_results[:max_hands], label="Paroli")
plt.plot(dalembert_results[:max_hands], label="D'Alembert")

plt.xlabel("Število iger")
plt.ylabel("Bankroll")
plt.title(f"Čas do propada različnih strategij")
plt.legend()
plt.grid(alpha=0.3)

plt.savefig("ruin_time.png", dpi=300, bbox_inches="tight")
plt.show()






