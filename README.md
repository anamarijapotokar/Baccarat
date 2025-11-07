# Baccarat

## Overview
This project analyzes betting strategies in the casino game Baccarat using statistical simulation and probabilistic modeling. The primary goal is to examine how different betting systems affect expected outcomes, risk of ruin, and bankroll variance, despite Baccarat being a negative-expectation game. While all wagers in Baccarat have a built-in house edge, which will also be calculated for different bets, the analysis explores how various strategies influence short-term volatility and duration of play.

## Objectives
1. Simulate Baccarat rounds using realistic probabilities for Player, Banker, and Tie outcomes.  
2. Implement and compare betting strategies, including:
   - Flat betting,  
   - Martingale,  
   - Reverse Martingale (Paroli),  
   - Fibonacci / D’Alembert systems.  
3. Measure and visualize:
   - expected value per bet,  
   - probability and time to ruin (bankruptcy),  
   - variance and volatility of bankroll,  
   - expected bankroll over time.  

4. Confirm theoretically that the long-run expected bankroll converges to 0 due to the house edge.

## Advanced topics
Baccarat is typically considered an unbeatable game due to its fixed dealing rules and large shoe size (6–8 decks). Unlike Blackjack, card counting is generally ineffective for the Banker and Player bets. However, some rare card compositions (e.g., an excess of even cards) can drastically increase the odds on the Tie bet, creating occasional high-value betting opportunities. By assigning values to odd/even cards, players can track these rare favorable conditions and adjust their wagers accordingly, and these are the situations we will also be analysing in our project.
