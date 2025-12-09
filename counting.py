# Dealt cards are not replaced, so the composition of the remaining shoe changes with each played game.
# After many hands, some values are over represented and some are under represented.
# Therefore, the probability of each outcome conditional on the remaining shoe is slighlty different from
# the unconditional probabilities.
# We call cards with values in {0, 2, 4, 6, 8} even cards and {1, 3, 5, 7, 9} odd cards.
# If the shoe becomes even-heavy, then both hands are more likely to end up with totals of the same parity: sum of (mostly) even numbers plus a small number of odds is still more likely to be even than odd.
# Matching parity isn't enough for a tie, but it's a necessary condition; pushing both totals into a narrower subset of 0-9 naturally increases the chance they land on the same number.
# So an even-heavy shoe can increase the odds of betting on a tie. We will see if this bet can become theoretically profitable.

from bacc import build_shoe, hand_value, decide_outcome, banker_draws_third
cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
values = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 0, 'J': 0, 'Q': 0, 'K': 0}

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

# We update two original functions so they use .draw; everything else is reused from the original script.
def first_deal2(shoe):
    player = [shoe.draw(), shoe.draw()]
    banker = [shoe.draw(), shoe.draw()]
    return player, banker

def play_bacc2(shoe):

    if shoe.cards_remaining() < 6:
        shoe.cards = build_shoe(8)
        shoe.count = 0 

    player, banker = first_deal2(shoe)

    player_total = hand_value(player)
    banker_total = hand_value(banker)

    if player_total in {8, 9} or banker_total in {8, 9}:
        return decide_outcome(player_total, banker_total)
    
    else:
        player_third = None
        if player_total <= 5:
            player_third = shoe.draw()
            player.append(player_third)
            player_total = hand_value(player)

        banker_third = None

        if player_third is None:
            if banker_total <= 5:
                banker_third = shoe.draw()
                banker.append(banker_third)
                banker_total = hand_value(banker)
        
        else:
            player_third_value = values[player_third]
            if banker_draws_third(banker_total, player_third_value):
                banker_third = shoe.draw()
                banker.append(banker_third)
                banker_total = hand_value(banker)

        return decide_outcome(player_total, banker_total)

# Our simulations yield the probability of winning with a Tie right off the bat is around 9.5%. The goal of counting is to find situations where the condtitional probability of winning on Tie when we have a high count = even-heavy remaining shoe is higher than that 9.5%;
# to be more precise: for a fair bet (without the house edge), EV=0=8*p-1*(1-p) --> p=1/9, so the actual minimum probability we need for Tie to not be losing in expectation is 1/9.

import math
from collections import defaultdict

# We define a function that estimates how likely a Tie is depending on the true count before a hand.
# true count is the ratio of running count to decks remaining, because if we get for example shoe.count=10, that means that we've seen more even than odd cards, but if we still have 7 decks remaining, thats a really small bias vs. if we only have 1 deck remaining, that's a big skew in composition; so true_count normalizes the running count by the number of decks left
# In short: running count=total imbalance so far, true count=imbalance per remaining deck.
# We expect higher true counts to be places where P(Tie|true count) is higher than usual.
def simulate_tie_probability(
        num_hands=500000, # how many hands we want to simulate in total
        number_of_decks=8, # number of decks in a shoe
        count_weights=count_weights, # dictionary for our counting system
        # Since true_count is some real number (x), we never see exactly the same value twice with enough precision and we cannot estimate the probability for each exact value x (we would have at most 1 sample per x), so we group similar x-es together into intervals and then estimate the probability within that interval.
        # So for each bin (=range of true_count) we estimate P(Tie|true_count \in bin). That will tell us at what count the Tie bet has the best chance of winning.
        # For smaller bin_width we can see more precise dependence on true_count, however we get fewer hands per bin --> less stable estimates
        bin_width=1.0,
        # We set a range for the true_count variable as something that is reasonably likely to occur (very large absolute true counts are very rare, especially in an 8 deck game, so our simulation will have almost no hands in those regions; any probability estimates based on a few hands are very noisy and not useful). However, even if the true_count < min_true or > max_true, we still play the hand, just not record it, so that cards still get drawn and the count gets updated (we want the shoe to remain natural).
        min_true=-10,
        max_true=10
    ):
    # Bins: integer keys representing intervals [k, k+bin_width).
    # We use defaultdict to create two dictionaries so that if a key doesn't exist yet, it is autmoatically created with the value int().
    # The dictionaries' keys are "indexes" of bins. We define those later. 
    total_counts = defaultdict(int) # how many hands started in a specific range
    tie_counts = defaultdict(int) # how many of those hands were ties

    # Creating the shoe:
    shoe = CountedShoe(number_of_decks=number_of_decks, count_weights=count_weights)

    for i in range(num_hands):
        if shoe.cards_remaining() < 6:
            shoe.cards = build_shoe(number_of_decks)
            shoe.count = 0

        # Compute true count before the hand. This needs to be done before dealing the next hand to refelct the shoe composition at the decision time.
        decks_left = shoe.decks_remaining()
        if decks_left == 0:  # probably don't need this
            continue
        
        true_count = shoe.count / decks_left

        # Only record if within interesting range.
        if true_count < min_true or true_count >= max_true:
            # Still play the hand to keep simulation realistic, but don't store.
            outcome = play_bacc2(shoe)
            continue

        # We map a continious true_count to a discrete bin (=grouping similar true counts together).
        bin_index = math.floor(true_count / bin_width)

        # Play the hand.
        outcome = play_bacc2(shoe)

        total_counts[bin_index] += 1
        if outcome == "Tie":
            tie_counts[bin_index] += 1

    # Compute estimated probabilities per bin.
    results = []

    for bin_index in sorted(total_counts.keys()):
        n = total_counts[bin_index] # number of hands in this bin
        if n == 0: # probablu uneccessary
            continue # tie_counts[bin_index]=number of hands in this bin that resulted in Tie
        p_hat = tie_counts[bin_index] / n # estimating the probability of Tie 
        # corresponding EV for Tie bet: 9p - 1
        tie_ev = 9 * p_hat - 1
        bin_left = bin_index * bin_width
        bin_right = bin_left + bin_width
        results.append({
            "bin_left": bin_left,
            "bin_right": bin_right,
            "hands": n,
            "p_tie": p_hat,
            "ev_tie": tie_ev
        })
    
    return results

results = simulate_tie_probability(
    num_hands=1000,
    number_of_decks=8,
    count_weights=count_weights,
    bin_width=1.0,
    min_true=-8,
    max_true=8
)

for r in results:
    print(
        f"True count in [{r['bin_left']:.1f}, {r['bin_right']:.1f}): "
        f"hands={r['hands']}, p_tie={r['p_tie']:.4f}, EV_tie={r['ev_tie']:.4f}"
    )
