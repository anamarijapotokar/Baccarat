"""
BACCARAT TIE BET CARD COUNTING ANALYSIS
========================================
Comparing TRUE COUNT vs RUNNING COUNT methods

This script analyzes card counting for Baccarat Tie bets using both methods:
1. TRUE COUNT: running_count / decks_remaining (Blackjack-style)
2. RUNNING COUNT: raw accumulated count (simpler, more stable)

KEY INSIGHT:
True count becomes unstable in Baccarat due to:
- Large shoe size (8 decks = 416 cards)
- Division by small numbers near shoe end

Running count may be more practical for Baccarat analysis.
"""

from bacc import build_shoe, hand_value, decide_outcome, banker_draws_third
import math
from collections import defaultdict
import matplotlib.pyplot as plt
import time

# Card definitions
cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
values = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
          '10': 0, 'J': 0, 'Q': 0, 'K': 0}

# =============================================================================
# COUNTING SYSTEMS TO TEST
# =============================================================================

# System 1: Odd-Good (based on empirical findings)
system_odd_good = {
    'A': +1, '3': +1, '5': +1, '7': +1, '9': +1,  
    '2': -1, '4': -1, '6': -1, '8': -1,            
    '10': -1, 'J': -1, 'Q': -1, 'K': -1            
}

# System 2: Even-Good (original hypothesis)
system_even_good = {
    'A': -1, '3': -1, '5': -1, '7': -1, '9': -1,
    '2': +1, '4': +1, '6': +1, '8': +1,
    '10': +1, 'J': +1, 'Q': +1, 'K': +1
}

system_griffin = {
    'A': -2, '2': +1, '3': -2, '4': +2, '5': -2,
    '6': +2, '7': -1, '8': +2, '9': -1,
    '10': +1, 'J': +1, 'Q': +1, 'K': +1
}

# System 4: Zero-Heavy (zeros create 0-0 ties)
system_zero_heavy = {
    'A': -1, '2': -1, '3': -1, '4': -1, '5': -1,
    '6': -1, '7': -1, '8': -1, '9': -1,
    '10': +3, 'J': +3, 'Q': +3, 'K': +3
}

# System 5: Balanced Approach (combining insights)
system_balanced = {
    'A': +1, '2': -1, '3': +2, '4': 0, '5': +1,
    '6': 0, '7': +1, '8': -1, '9': +2,
    '10': +1, 'J': +1, 'Q': +1, 'K': +1
}

COUNTING_SYSTEMS = {
    'Odd-Good': system_odd_good,
    'Even-Good': system_even_good,
    'Griffin': system_griffin,
    'Zero-Heavy': system_zero_heavy,
    'Balanced': system_balanced
}

# =============================================================================
# COUNTED SHOE CLASS
# =============================================================================

class CountedShoe:
    """Shoe with card counting capability."""
    
    def __init__(self, number_of_decks=8, count_weights=None):
        self.cards = build_shoe(number_of_decks)
        self.count = 0
        self.count_weights = count_weights or {}
        self.initial_decks = number_of_decks
        
    def draw(self):
        """Draw a card and update the count."""
        if len(self.cards) == 0:
            raise ValueError("Cannot draw from empty shoe")
        
        card = self.cards.pop()
        if card in self.count_weights:
            self.count += self.count_weights[card]
        return card
    
    def cards_remaining(self):
        """Return number of cards left."""
        return len(self.cards)
    
    def decks_remaining(self):
        """Return approximate number of decks remaining."""
        return len(self.cards) / 52
    
    def true_count(self, min_decks=1.5):
        
        decks = max(self.decks_remaining(), min_decks)
        return self.count / decks
    
    def reset(self):
        """Reset the shoe."""
        self.cards = build_shoe(self.initial_decks)
        self.count = 0

# =============================================================================
# GAME LOGIC
# =============================================================================

def play_hand_counted(shoe):
    """
    Play one hand of Baccarat.
    Returns outcome: 'Player', 'Banker', or 'Tie'
    """
    # Deal initial cards; in reality the dealer alternates between them but it doesnt matter here
    player = [shoe.draw(), shoe.draw()]
    banker = [shoe.draw(), shoe.draw()]
    
    player_total = hand_value(player)
    banker_total = hand_value(banker)
    
    # Natural 8 or 9
    if player_total in {8, 9} or banker_total in {8, 9}:
        return decide_outcome(player_total, banker_total)
    
    # Player draws third card rule
    player_third = None
    if player_total <= 5:
        player_third = shoe.draw()
        player.append(player_third)
        player_total = hand_value(player)
    
    # Banker draws third card rule
    if player_third is None:
        if banker_total <= 5:
            banker.append(shoe.draw())
            banker_total = hand_value(banker)
    else:
        player_third_value = values[player_third]
        if banker_draws_third(banker_total, player_third_value):
            banker.append(shoe.draw())
            banker_total = hand_value(banker)
    
    return decide_outcome(player_total, banker_total)

# =============================================================================
# SIMULATION: TRUE COUNT METHOD
# =============================================================================

def simulate_true_count(
    num_hands=1000000,
    number_of_decks=8,
    count_weights=None,
    bin_width=1.0,
    min_true=-10,
    max_true=10
):
    """
    Simulate using TRUE COUNT (running_count / decks_remaining).
    More volatile, becomes unstable near end of shoe.
    """
    total_counts = defaultdict(int)
    tie_counts = defaultdict(int)
    
    shoe = CountedShoe(number_of_decks=number_of_decks, count_weights=count_weights)
    
    skipped_unstable = 0
    hands_recorded = 0
    
    for _ in range(num_hands):
        # Reset at 1.5 decks (78 cards) - conservative cutoff
        if shoe.cards_remaining() < 78:
            shoe.reset()
        
        # Get true count BEFORE playing
        true_count = shoe.true_count()
        
        # Play the hand
        outcome = play_hand_counted(shoe)
        
        # Skip if true count is unstable (None)
        if true_count is None:
            skipped_unstable += 1
            continue
        
        # Record if within range
        if min_true <= true_count < max_true:
            bin_index = math.floor(true_count / bin_width)
            total_counts[bin_index] += 1
            if outcome == "Tie":
                tie_counts[bin_index] += 1
            hands_recorded += 1
    
    # Compute results
    results = []
    for bin_index in sorted(total_counts.keys()):
        n = total_counts[bin_index]
        if n == 0:
            continue
        
        ties = tie_counts[bin_index]
        p_hat = ties / n
        tie_ev = 8 * p_hat - (1 - p_hat)
        
        bin_left = bin_index * bin_width
        bin_right = bin_left + bin_width
        
        results.append({
            "bin_index": bin_index,
            "bin_left": bin_left,
            "bin_right": bin_right,
            "hands": n,
            "ties": ties,
            "p_tie": p_hat,
            "ev_tie": tie_ev,
        })
    
    print(f"    Recorded: {hands_recorded:,} hands ({hands_recorded/num_hands*100:.1f}%)")
    print(f"    Skipped (unstable): {skipped_unstable:,}")
    
    return results

# =============================================================================
# SIMULATION: RUNNING COUNT METHOD
# =============================================================================

def simulate_running_count(
    num_hands=1000000,
    number_of_decks=8,
    count_weights=None,
    bin_width=5,
    min_count=-60,
    max_count=60
):
    """
    Simulate using RUNNING COUNT (raw accumulated count).
    More stable, doesn't require division, simpler to use.
    """
    total_counts = defaultdict(int)
    tie_counts = defaultdict(int)
    
    shoe = CountedShoe(number_of_decks=number_of_decks, count_weights=count_weights)
    
    hands_recorded = 0
    
    for _ in range(num_hands):
        # Reset at 1.5 deck (78 cards)
        if shoe.cards_remaining() < 78:
            shoe.reset()
        
        # Get running count BEFORE playing
        running_count = shoe.count
        
        # Play the hand
        outcome = play_hand_counted(shoe)
        
        # Record if within range
        if min_count <= running_count < max_count:
            bin_index = math.floor(running_count / bin_width)
            total_counts[bin_index] += 1
            if outcome == "Tie":
                tie_counts[bin_index] += 1
            hands_recorded += 1
    
    # Compute results
    results = []
    for bin_index in sorted(total_counts.keys()):
        n = total_counts[bin_index]
        if n == 0:
            continue
        
        ties = tie_counts[bin_index]
        p_hat = ties / n
        tie_ev = 8 * p_hat - (1 - p_hat)
        
        bin_left = bin_index * bin_width
        bin_right = bin_left + bin_width
        
        results.append({
            "bin_index": bin_index,
            "bin_left": bin_left,
            "bin_right": bin_right,
            "hands": n,
            "ties": ties,
            "p_tie": p_hat,
            "ev_tie": tie_ev,
        })
    
    print(f"    Recorded: {hands_recorded:,} hands ({hands_recorded/num_hands*100:.1f}%)")
    
    return results

# =============================================================================
# VISUALIZATION
# =============================================================================

def plot_comparison(true_results, running_results, system_name):
    """Create side-by-side comparison of true count vs running count - EV only."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # TRUE COUNT - Expected Value
    if true_results:
        tc_bins = [r['bin_left'] for r in true_results]
        tc_evs = [r['ev_tie'] for r in true_results]
        tc_hands = [r['hands'] for r in true_results]
        
        colors = ['red' if ev < 0 else 'green' for ev in tc_evs]
        ax1.scatter(tc_bins, tc_evs, s=[min(h/100, 200) for h in tc_hands], 
                   alpha=0.6, c=colors)
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=2, label='Break-even')
        ax1.set_xlabel('True Count', fontsize=12)
        ax1.set_ylabel('Expected Value (per $1 bet)', fontsize=12)
        ax1.set_title(f'TRUE COUNT Method - {system_name}', 
                     fontsize=13, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
    
    # RUNNING COUNT - Expected Value
    if running_results:
        rc_bins = [r['bin_left'] for r in running_results]
        rc_evs = [r['ev_tie'] for r in running_results]
        rc_hands = [r['hands'] for r in running_results]
        
        colors = ['red' if ev < 0 else 'green' for ev in rc_evs]
        ax2.scatter(rc_bins, rc_evs, s=[min(h/100, 200) for h in rc_hands], 
                   alpha=0.6, c=colors)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=2, label='Break-even')
        ax2.set_xlabel('Running Count', fontsize=12)
        ax2.set_ylabel('Expected Value (per $1 bet)', fontsize=12)
        ax2.set_title(f'RUNNING COUNT Method - {system_name}', 
                     fontsize=13, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()  # Display the graph instead of saving

# =============================================================================
# ANALYSIS
# =============================================================================

def analyze_results(results, method_name, system_name):
    """Analyze and print results for one method."""
    
    if not results:
        print(f"\n No results for {method_name}")
        return
    
    total_hands = sum(r['hands'] for r in results)
    positive_ev = [r for r in results if r['ev_tie'] > 0]
    pos_hands = sum(r['hands'] for r in positive_ev)
    
    print(f"\n{'='*70}")
    print(f"{method_name} - {system_name}")
    print('='*70)
    print(f"Total hands: {total_hands:,}")
    print(f"Positive EV hands: {pos_hands:,} ({pos_hands/total_hands*100:.3f}%)")
    
    if not positive_ev:
        print(" No positive EV situations found")
        return
    
    # Best opportunity
    best = max(positive_ev, key=lambda x: x['ev_tie'])
    print(f"\n Best Opportunity:")
    print(f"  Count range: [{best['bin_left']:.1f}, {best['bin_right']:.1f})")
    print(f"  P(Tie): {best['p_tie']:.4f} ({best['p_tie']*100:.2f}%)")
    print(f"  EV: {best['ev_tie']:.4f} ({best['ev_tie']*100:.2f}%)")
    print(f"  Sample size: {best['hands']:,} hands")
    
    # Average in +EV situations
    avg_ev = sum(r['ev_tie'] * r['hands'] for r in positive_ev) / pos_hands
    print(f"\n Average EV (in +EV situations): {avg_ev:.4f} ({avg_ev*100:.2f}%)")
    
    # Frequency
    freq = pos_hands / total_hands * 100
    print(f"\n  Frequency: {freq:.3f}% of hands")
    print(f"  (~1 in {int(100/freq) if freq > 0 else 'inf'} hands)")

# =============================================================================
# MAIN COMPARISON
# =============================================================================

def compare_methods(systems, num_hands=1000000):
    """
    Compare TRUE COUNT vs RUNNING COUNT for multiple systems.
    """
    print("\n" + "="*80)
    print("TRUE COUNT vs RUNNING COUNT COMPARISON")
    print("="*80)
    print(f"\nSimulating {num_hands:,} hands per system per method...\n")
    
    for system_name, count_weights in systems.items():
        print(f"\n{'='*80}")
        print(f"SYSTEM: {system_name}")
        print('='*80)
        
        # Test TRUE COUNT method
        print("\n[1] Testing TRUE COUNT method...")
        start = time.time()
        true_results = simulate_true_count(
            num_hands=num_hands,
            count_weights=count_weights,
            bin_width=1.0,
            min_true=-10,
            max_true=10
        )
        print(f"    Time: {time.time() - start:.1f}s")
        
        # Test RUNNING COUNT method
        print("\n[2] Testing RUNNING COUNT method...")
        start = time.time()
        running_results = simulate_running_count(
            num_hands=num_hands,
            count_weights=count_weights,
            bin_width=5,
            min_count=-60,
            max_count=60
        )
        print(f"    Time: {time.time() - start:.1f}s")
        
        # Analyze both
        analyze_results(true_results, "TRUE COUNT", system_name)
        analyze_results(running_results, "RUNNING COUNT", system_name)
        
        # Visualize comparison
        #plot_comparison(true_results, running_results, system_name)
    
    

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    NUM_HANDS = 1000000  # 1 million
    
    compare_methods(
        systems=COUNTING_SYSTEMS,
        num_hands=NUM_HANDS
    )
    
### True counts go towards +- infinity when the number of decks decreases which means that blackjack style of coutning is not the best 
