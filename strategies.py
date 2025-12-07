
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

    else:
        raise ValueError(f"Unknown bet_type: {bet_type}")

from bacc import build_shoe, play_bacc

hands_number = 100000
initial_bankroll = 100
base_bet = 1
bet_type = "Banker"  # or Player or Tie

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
            path.append(0.0)
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

# RUNNING AND COMPARING THE TWO
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

print(f"Final bankroll Flat: {flat_results[-1]:.2f}")
print(f"Final bankroll Martingale: {martingale_results[-1]:.2f}")
print(f"Final bankroll Paroli: {paroli_results[-1]:.2f}")
print(f"Final bankroll D'Alembert: {dalembert_results[-1]:.2f}")
print(f"Flat ruin at hand: {flat_ruin}")
print(f"Martingale ruin at hand: {martingale_ruin}")
print(f"Paroli ruin at hand: {paroli_ruin}")
print(f"D'Alembert ruin at hand: {dalembert_ruin}")

# from bacc import build_shoe, play_bacc

# shoe = build_shoe()
# hands_number = 10000000

# bankroll_flat = 100
# bankroll_martingale = 100
# bet = 1

# # izbereš Banker/Player/TIe
# bet_type = "Banker"

# flat_results = []
# martingale_results = []
# current_bet = bet

# for i in range(1, hands_number + 1):
#     result = play_bacc(shoe)

    
#     if bankroll_flat <= 0:
#         flat_results.append(0)
#     else:
#         if result == bet_type:
#             if bet_type == "Tie":
#                 bankroll_flat += bet * 8
#             else:
#                 bankroll_flat += bet
#         else:
#             bankroll_flat -= bet
#         flat_results.append(bankroll_flat)

#     if bankroll_flat <= 0:
#         print(f"Bankrup flat at hand {i} by betting on {bet_type}")
#         break
# else:
#     print(f"Flat didn't bankrupt by betting on {bet_type}")

# #print(flat_results)
# print()

# for i in range(1, hands_number + 1):
#     result = play_bacc(shoe)

#     if bankroll_martingale <= 0:
#         martingale_results.append(0)
#     else:
#         if result == bet_type:
#             if bet_type == "Tie":
#                 bankroll_martingale += current_bet * 8
#             else:
#                 bankroll_martingale += current_bet
#             current_bet = bet  
#         else:
#             bankroll_martingale -= current_bet
#             current_bet *= 2  
#             if current_bet > bankroll_martingale:
#                 current_bet = bankroll_martingale
#         martingale_results.append(bankroll_martingale)

    
#     if  bankroll_martingale <= 0:
#         print(f"Bankrupt martingale at hand {i} by betting on {bet_type}")
#         break
# else:
#     print(f"Martingale didn't bankrupt by betting on {bet_type}")
# #print(martingale_results)