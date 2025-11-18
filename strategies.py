from bacc import build_shoe, play_bacc

shoe = build_shoe()
hands_number = 1000

bankroll_flat = 100
bankroll_martingale = 100
bet = 1

# izbereš Banker/Player/TIe
bet_type = "Player"

flat_results = []
martingale_results = []
current_bet = bet

for i in range(1, hands_number + 1):
    result = play_bacc(shoe)

    
    if bankroll_flat <= 0:
        flat_results.append(0)
    else:
        if result == bet_type:
            if bet_type == "Tie":
                bankroll_flat += bet * 8
            else:
                bankroll_flat += bet
        else:
            bankroll_flat -= bet
        flat_results.append(bankroll_flat)

    if bankroll_flat <= 0:
        print(f"Bankrup flat at hand {i}")
        break
else:
    print("Flat didn't bankrupt")

#print(flat_results)
print()

for i in range(1, hands_number + 1):
    result = play_bacc(shoe)

    if bankroll_martingale <= 0:
        martingale_results.append(0)
    else:
        if result == bet_type:
            if bet_type == "Tie":
                bankroll_martingale += current_bet * 8
            else:
                bankroll_martingale += current_bet
            current_bet = bet  
        else:
            bankroll_martingale -= current_bet
            current_bet *= 2  
            if current_bet > bankroll_martingale:
                current_bet = bankroll_martingale
        martingale_results.append(bankroll_martingale)

    
    if  bankroll_martingale <= 0:
        print(f"Bankrupt martingale at hand {i}")
        break
else:
    print("Martingale didn't bankrupt")
#print(martingale_results)