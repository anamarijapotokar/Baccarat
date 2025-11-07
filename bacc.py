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

# We then define drawing cards from a shoe. If there aren't enough cards left to finish a game of Baccarat, we rebuild a fresh shoe.
def draw(shoe):
    if len(shoe) < 6:
        shoe[:] = build_shoe(number_of_decks = 8)
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

# def banker_draws_third(banker_total, player_third):
#     if player_third is None:
#         return banker_total <= 
