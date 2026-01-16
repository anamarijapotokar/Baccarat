import numpy as np
import matplotlib.pyplot as plt
from bacc import build_shoe, play_bacc
from strategies import simulate_flat, simulate_dalembert, simulate_martingale, simulate_paroli

# --- Settings ---
hands_per_sim = 10000      # number of hands per simulation for plotting
num_simulations = 10      # number of repeated runs for ruin time calculation
initial_bankroll = 100
base_bet = 1
bet_type = "Banker"        
window_var = 100           

strategies = {
    "Flat": simulate_flat,
    "Martingale": simulate_martingale,
    "Paroli": simulate_paroli,
    "D'Alembert": simulate_dalembert
}

# --- Helper functions ---
def ruin_time(path):
    for i, b in enumerate(path, start=1):
        if b <= 0:
            return i
    return None

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
        outcomes = [play_bacc(shoe) for _ in range(hands_per_sim)]
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
