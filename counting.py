# Dealt cards are not replaced, so the composition of the remaining shoe changes with each played game.
# After many hands, some values are over represented and some are under represented.
# Therefore, the probability of each outcome conditional on the remaining shoe is slighlty different from
# the unconditional probabilities.
# We call cards with values in {0, 2, 4, 6, 8} even cards and {1, 3, 5, 7, 9} odd cards.
# If the shoe becomes even-heavy, then both hands are more likely to end up with totals of the same parity: sum of (mostly) even numbers plus a small number of odds is still more likely to be even than odd.
# Matching parity isn't enough for a tie, but it's a necessary condition; pushing both totals into a narrower subset of 0-9 naturally increases the chance they land on the same number.
# So an even-heavy shoe can increase the odds of betting on a tie. We will see if this bet can become theoretically profitable.

from bacc import build_shoe

# First, we define a simple counting system: even/zero cards are good for Tie, and odd cards are bad for Tie.
count_weights = {
    'A': -1,
    '2': +1,
    '3': -1,
    '4': +1,
    '5': -1,
    '6': +1,
    '7': -1,
    '8': +1,
    '9': -1,
    '10': +1,
    'J': +1,
    'Q': +1,
    'K': +1
}

# We will define a new class called CountedShoe, which will contain the cards, the running count and the logic to update that count when you draw a card.
class CountedShoe:
    def __init__(self, number_of_decks=8, count_weights=None):
        self.cards = build_shoe(number_of_decks) # for storing the list of cards
        self.count = 0 # for keeping the count
        self.count_weights = count_weights # dictionary so that draw will know how to update the count when a card is drawn

    def draw(self):
        card = self.cards.pop() # takes one card from the end of self.cards
        if self.count_weights is not None: # if a counting system was provided
            self.count += self.count_weights[card] # we look up the weight assigned to that card and update the running count
        return card

    def cards_remaining(self): # to see how many cards are left
        return len(self.cards)

    def decks_remaining(self): # to see approximately how many decks are left
        return len(self.cards) / 52


