# 18-card-poker

## Introduction

18 card poker is my own version of Texas Holdem poker that uses a deck of only 18 cards (6 distinct numerical cards with 2 more non-suited duplicates). Every player is dealt 2 cards hidden from the other players and players with strong cards must force other players to fold from the hand and forfeit their current stake in the pot or call with a potentially weaker hand and risk losing more money. After 1 round of betting, a single flop comes of 3 cards and a final round of betting occurs based on who belives they have the best 5 carded hand (their 2 cards + the middle 3 cards). The aim of the game is to get players with likely weaker hands (based off your strong hand) to stake big money into the pot for you to take or for you to scare off stronger players by forfeiting a large portion of your own stake to make them believe you indeed have the stronger hand. However, strong handed players will call your bluff so your expected value is P(they fold to your bluff) * pot + P(they call your bluff and you win on the flop) * (pot + bet size) - P(they call your bluff and you lose) * (pot + bet size) - P(they raise and you fold) * (pot + bet size) + Value Gain(they are conditioned to call your strong hands now). Poker is about maximising that expected value by calculating the probabilities and adjusting your bet size PDF(fold: p1, call: p2, min raise: p3, big raise: p4), p1 + .. + p4 = 1.

The motivation behind this project is to use a simplified game of Texas Holdem poker as a test area for game theory AI algorithms on an imperfect information game. I hope to optimise a machine learning approach until I have an AI that can consistenly gain positive reward against an experienced strategy game player like myself. This will be an amazing learning opportunity for me to test every modern approach to game theory and deepen my knowledge on the area and the application of the area.

Aproaches / Algorithms:
- ML PDF to narrow ranges (like human play)
- Using nashpy to estimate a nash equilibrium from a determined payoff matrix
- CFR
- MCCFR+

## Instructions for running

I have used the following installed python modules:
- pygame (to install: pip3 install pygame)
  
  
1. Run the poker.py file to load up a 3 player game of poker with Alice, Bob and Charlie.
2. Use the keys C (call / check), R (raise) and F (fold) to make a move for the current player (highlighted in yellow).

## To do

Implement an all in feature that allows players to go all in without going into negative stacks.

