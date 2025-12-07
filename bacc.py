import random

cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
values = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 0, 'J': 0, 'Q': 0, 'K': 0}

# Building the dealer's shoe. Since we only care about card values and not their suits, we append 4 same cards for each deck.
# We then shuffle the shoe.
def build_shoe(number_of_decks = 8):
    shoe = []
    for i in range(number_of_decks):
        for card in cards:
            for suit in range(4):
                shoe.append(card)
    random.shuffle(shoe)
    return shoe

# We then define drawing cards from a shoe.
def draw(shoe):
    return shoe.pop()

# Computing hand values.
def hand_value(hand):
    total = 0
    for card in hand:
        total += values[card]
    return total % 10

# Dealing two cards to Player and Banker from our shoe.
def first_deal(shoe):
    player = [draw(shoe), draw(shoe)]
    banker = [draw(shoe), draw(shoe)]
    return player, banker

# The Banker draws third card rules.
def banker_draws_third(banker_total, player_third_value):
    if banker_total <= 2:
        return True
    if banker_total == 3:
        return player_third_value != 8
    if banker_total == 4:
        return player_third_value in {2, 3, 4, 5, 6, 7}
    if banker_total == 5:
        return player_third_value in {4, 5, 6, 7}
    if banker_total == 6:
        return player_third_value in {6, 7}
    else:
        return False
    
def decide_outcome(player_total, banker_total):
    if player_total > banker_total:
        return 'Player'
    elif banker_total > player_total:
        return 'Banker'
    else:
        return 'Tie'
    
def play_bacc(shoe):

    # Ensure enough cards before the hand starts.
    if len(shoe) < 6:
        shoe[:] = build_shoe(8)
    # We first deal the initial two hands.
    player, banker = first_deal(shoe)

    # Computing the initial values of each hand.
    player_total = hand_value(player)
    banker_total = hand_value(banker)

    # Natural wins:
    if player_total in {8, 9} or banker_total in {8, 9}:
        return decide_outcome(player_total, banker_total) # tuki bi lahko mogoče returnala use statse po koncu igre?
    
    else:
        player_third = None
        if player_total <= 5:
            player_third = draw(shoe)
            player.append(player_third)
            player_total = hand_value(player)

        banker_third = None

        if player_third is None:
            # Player didn't draw a third card
            # Banker draws on 0–5, stands on 6–7
            if banker_total <= 5:
                banker_third = draw(shoe)
                banker.append(banker_third)
                banker_total = hand_value(banker)
        
        else:
            # Player drew a third card
            player_third_value = values[player_third]
            if banker_draws_third(banker_total, player_third_value):
                banker_third = draw(shoe)
                banker.append(banker_third)
                banker_total = hand_value(banker)

        return decide_outcome(player_total, banker_total)  

        



