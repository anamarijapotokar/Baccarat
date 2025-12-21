"""
This script analyzes multiple card counting systems for the Baccarat Tie bet.

KEY FINDINGS FROM ORIGINAL RESEARCH:
- Initial hypothesis (even-heavy favors ties) was INCORRECT
- Data shows odd-heavy shoes actually increase tie probability
- This version tests multiple counting systems and provides comprehensive analysis
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

# System 1: Odd-Good (flipped from original - based on empirical findings)
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

# System 3: Peter Griffin's system (weighted by tie impact)
# Based on theoretical analysis of how each card affects tie probability
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
    
    def true_count(self):
        """Return true count (running count / decks remaining)."""
        decks = self.decks_remaining()
        return self.count / decks if decks > 0 else 0
    
    def reset(self):
        """Reset the shoe."""
        self.cards = build_shoe(self.initial_decks)
        self.count = 0

# =============================================================================
# GAME LOGIC WITH COUNTING
# =============================================================================

def first_deal_counted(shoe):
    """Deal initial two cards to player and banker."""
    player = [shoe.draw(), shoe.draw()]
    banker = [shoe.draw(), shoe.draw()]
    return player, banker

def play_bacc_counted(shoe):
    """
    Play one hand of Baccarat with card counting.
    Returns the outcome: 'Player', 'Banker', or 'Tie'
    """
    if shoe.cards_remaining() < 6:
        shoe.reset()
    
    player, banker = first_deal_counted(shoe)
    
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

# =============================================================================
# STATISTICAL ANALYSIS
# =============================================================================

def wilson_confidence_interval(successes, trials, confidence=0.95):
    """
    Calculate Wilson score confidence interval for binomial proportion.
    More accurate than normal approximation for small samples.
    """
    if trials == 0:
        return (0, 0)
    
    p_hat = successes / trials
    z = 1.96  # 95% confidence
    
    denominator = 1 + z**2 / trials
    centre = (p_hat + z**2 / (2*trials)) / denominator
    margin = z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4*trials)) / trials) / denominator
    
    return (centre - margin, centre + margin)

def kelly_fraction(p_win, odds):
    """
    Calculate optimal bet size using Kelly criterion.
    
    
    Returns:
        Fraction of bankroll to bet (0 to 1)
    """
    p_lose = 1 - p_win
    if p_win * odds <= p_lose:
        return 0  # Negative or zero EV
    
    kelly = (p_win * odds - p_lose) / odds
    return max(0, min(kelly, 1.0))  # Cap at 100%

# =============================================================================
# SIMULATION ENGINE
# =============================================================================

def simulate_tie_probability(
    num_hands=1000000,
    number_of_decks=8,
    count_weights=None,
    bin_width=1.0,
    min_true=-10,
    max_true=10
):
    """
    Simulate Baccarat and estimate tie probability by true count.
    
    Args:
        num_hands: Number of hands to simulate
        number_of_decks: Decks in shoe
        count_weights: Dictionary mapping cards to count values
        bin_width: Width of true count bins for grouping
        min_true: Minimum true count to track
        max_true: Maximum true count to track
    
    Returns:
        List of dicts with bin statistics
    """
    total_counts = defaultdict(int)
    tie_counts = defaultdict(int)
    
    shoe = CountedShoe(number_of_decks=number_of_decks, count_weights=count_weights)
    
    for _ in range(num_hands):
        # Reset if shoe is getting low
        if shoe.cards_remaining() < 10:  # Check BEFORE anything else
            shoe.reset()
        
        # Capture true count BEFORE playing the hand
        true_count = shoe.true_count()
        
        # Play the hand (remove reset check from this function)
        player, banker = first_deal_counted(shoe)
        player_total = hand_value(player)
        banker_total = hand_value(banker)
        
        if player_total in {8, 9} or banker_total in {8, 9}:
            outcome = decide_outcome(player_total, banker_total)
        else:
            player_third = None
            if player_total <= 5:
                player_third = shoe.draw()
                player.append(player_third)
                player_total = hand_value(player)
            
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
            
            outcome = decide_outcome(player_total, banker_total)
        
        # Record if in range
        if min_true <= true_count < max_true:
            bin_index = math.floor(true_count / bin_width)
            total_counts[bin_index] += 1
            if outcome == "Tie":
                tie_counts[bin_index] += 1
    
    # Compute results
    results = []
    for bin_index in sorted(total_counts.keys()):
        n = total_counts[bin_index]
        if n == 0:
            continue
        
        ties = tie_counts[bin_index]
        p_hat = ties / n
        
        # EV for Tie bet: win 8 units with prob p, lose 1 unit with prob (1-p)
        tie_ev = 8 * p_hat - (1 - p_hat)  # Simplified: 9*p - 1
        
        # Confidence interval
        ci_lower, ci_upper = wilson_confidence_interval(ties, n)
        
        # Kelly fraction if positive EV
        kelly = kelly_fraction(p_hat, 8) if tie_ev > 0 else 0
        
        bin_left = bin_index * bin_width
        bin_right = bin_left + bin_width
        
        results.append({
            "bin_index": bin_index,
            "bin_left": bin_left,
            "bin_right": bin_right,
            "hands": n,
            "ties": ties,
            "p_tie": p_hat,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "ev_tie": tie_ev,
            "kelly": kelly
        })
    
    return results

# =============================================================================
# VISUALIZATION
# =============================================================================



# =============================================================================
# PRACTICAL ANALYSIS
# =============================================================================

def practical_analysis(results, system_name, base_bet=10, hands_per_hour=60):
    """
    Analyze practical exploitability of the counting system.
    """
    if not results:
        print(f"\nNo data for {system_name}")
        return
    
    total_hands = sum(r['hands'] for r in results)
    positive_ev_results = [r for r in results if r['ev_tie'] > 0]
    positive_hands = sum(r['hands'] for r in positive_ev_results)
    
    print(f"\n{'='*70}")
    print(f"PRACTICAL ANALYSIS: {system_name}")
    print('='*70)
    print(f"Total hands analyzed: {total_hands:,}")
    print(f"Hands with positive EV: {positive_hands:,} ({positive_hands/total_hands*100:.3f}%)")
    
    if not positive_ev_results:
        print("\n NO POSITIVE EV SITUATIONS FOUND")
        print("This counting system does not identify profitable betting opportunities.")
        return
    
    # Find best opportunities
    best_bin = max(positive_ev_results, key=lambda x: x['ev_tie'])
    
    print(f"\n BEST OPPORTUNITY:")
    print(f"  True count range: [{best_bin['bin_left']:.1f}, {best_bin['bin_right']:.1f})")
    print(f"  Tie probability: {best_bin['p_tie']:.4f} ")
    print(f"  Expected Value: {best_bin['ev_tie']:.4f} ")
    print(f"  Kelly bet size: {best_bin['kelly']*100:.2f}% of bankroll")
    print(f"  Hands observed: {best_bin['hands']:,}")
    print(f"  Confidence: [{best_bin['ci_lower']:.4f}, {best_bin['ci_upper']:.4f}]")
    
    # Overall statistics for +EV situations
    avg_ev = sum(r['ev_tie'] * r['hands'] for r in positive_ev_results) / positive_hands
    weighted_kelly = sum(r['kelly'] * r['hands'] for r in positive_ev_results) / positive_hands
    
    print(f"\n PROFIT ANALYSIS:")
    print(f"  Average EV in +EV situations: {avg_ev:.4f} ")
    print(f"  Average Kelly fraction: {weighted_kelly*100:.2f}%")
    
    # Frequency analysis
    freq_pct = (positive_hands / total_hands) * 100
    hands_between = 1 / (positive_hands / total_hands) if positive_hands > 0 else float('inf')
    hours_between = hands_between / hands_per_hour
    
    print(f" \n FREQUENCY:")
    print(f"  Occurrence rate: {freq_pct:.3f}% of hands")
    print(f"  Average hands between +EV: {hands_between:.1f}")
    print(f"  Hours between +EV (at {hands_per_hour}/hr): {hours_between:.2f}")
    
    print(f"\n{'='*70}")
    if freq_pct < 0.5:
        print("  VERDICT: NOT PRACTICALLY EXPLOITABLE")
        print("Positive EV situations are too rare (<0.5% of hands)")
    
    else:
        print(" VERDICT: POTENTIALLY EXPLOITABLE")
        print("Reasonable edge and frequency - further testing recommended")
    print('='*70)

# =============================================================================
# COMPARISON FUNCTION
# =============================================================================

def compare_systems(systems, num_hands=1000000, bin_width=1.0):
    """
    Compare multiple counting systems side by side.
    """
    print("\n" + "="*80)
    print("BACCARAT TIE COUNTING SYSTEM COMPARISON")
    print("="*80)
    print(f"Simulating {num_hands:,} hands per system...\n")
    
    all_results = {}
    
    for system_name, count_weights in systems.items():
        print(f"Testing {system_name}...", end=" ")
        start = time.time()
        
        results = simulate_tie_probability(
            num_hands=num_hands,
            number_of_decks=8,
            count_weights=count_weights,
            bin_width=bin_width,
            min_true=-10,
            max_true=10
        )
        
        elapsed = time.time() - start
        all_results[system_name] = results
        print(f"Done in {elapsed:.1f}s")
    
    # Print detailed results for each system
    for system_name, results in all_results.items():
        print(f"\n{'='*80}")
        print(f"DETAILED RESULTS: {system_name}")
        print('='*80)
        
        for r in results:
            status = "✓ +EV" if r['ev_tie'] > 0 else ""
            print(
                f"TC [{r['bin_left']:5.1f}, {r['bin_right']:5.1f}): "
                f"hands={r['hands']:7,}  p_tie={r['p_tie']:.4f}  "
                f"EV={r['ev_tie']:+.4f}  Kelly={r['kelly']:.2%}  {status}"
            )
        
        practical_analysis(results, system_name)
        
    
    # Summary comparison
    print("\n" + "="*80)
    print("SUMMARY COMPARISON")
    print("="*80)
    print(f"{'System':<20} {'Max EV':<12} {'+EV Freq':<12} {'Best p(Tie)':<12}")
    print("-" * 80)
    
    for system_name, results in all_results.items():
        if results:
            max_ev = max((r['ev_tie'] for r in results), default=0)
            total_hands = sum(r['hands'] for r in results)
            pos_hands = sum(r['hands'] for r in results if r['ev_tie'] > 0)
            freq = (pos_hands / total_hands * 100) if total_hands > 0 else 0
            max_p = max((r['p_tie'] for r in results), default=0)
            
            print(f"{system_name:<20} {max_ev:>+10.4f}  {freq:>10.3f}%  {max_p:>10.4f}")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Configuration
    NUM_HANDS = 10000000  # 10 million hands for good statistical power
    BIN_WIDTH = 1.0       # 1 true count unit per bin
    
    # Run comparison
    compare_systems(
        systems=COUNTING_SYSTEMS,
        num_hands=NUM_HANDS,
        bin_width=BIN_WIDTH
    )
    
    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)

