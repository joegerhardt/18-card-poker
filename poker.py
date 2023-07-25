import random
#from itertools import cycle
#import pokerAI as ai
import config
from display import Display
import pygame
import json
import time



hand_quality = ['high_card', 'pair', 'two_pair', 'three_of_a_kind', 'straight', 'full_house', 'four_of_a_kind']



class Player:
    def __init__(self, name, stack):

        self.name = name
        self.stack = stack
        self.hand = ()
        self.active = True

        #next and previous pointers to players at table
        self.next = None 
        self.prev = None

        #next and previous pointers to players in hand
        self.next_active = None
        self.prev_active = None



    def __str__(self) -> str:

        return str(self.name)
    


class Game:
    def __init__(self, params):

        #---game parameters---

        #add players to game
        self.players = [Player(player, params['stack']) for player in params['player_names']]
        for index, player in enumerate(self.players):
            player.next = self.players[(index+1)%len(self.players)]
            player.prev = self.players[index-1]
        
        #static variables
        self.starting_stack = params['stack']
        self.small_blind_amount = params['small_blind']
        self.big_blind_amount = params['big_blind']
        self.card_values = [i for i in range(2, 2+params['range'])]
        self.card_duplicates = params['suits']
        self.min_straight_length = params['min_straight_length']
        self.betting_stage_public_cards = params['betting_stage_public_cards']
        self.hand_size = params['hand_size']

        #create deck
        self.deck = []
        self.table_cards = ()
        
        self.betting_round = 0
        self.total_bets = {player:0 for player in self.players}
        self.pot = 0
        self.num_hands = -1
        self.scores = {player:0 for player in self.players}

        self.busted_players = []
        self.active_players = []
        self.players_moved_this_round = []
    
        self.current_player = None
        self.dealer = self.players[0]
        self.small_blind_player = None
        self.big_blind_player = None
        self.history = ""
        



    def add_player(self):

        player = Player('', self.starting_stack)

        #add player to list of players
        self.players.append(player)

        #update linked list of players
        if len(self.players) > 1:
            self.players[0].prev = player
            self.players[-2].next = player
            player.next = self.players[0]
            player.prev = self.players[-2]

    

    def set_blinds(self):

        #if game is heads up the dealer gets the small blind
        if len(self.players) == 2:
            self.small_blind_player = self.dealer
            self.big_blind_player = self.small_blind_player.next

        #else the player after the dealer gets the small blind
        else:
            self.small_blind_player = self.dealer.next
            self.big_blind_player = self.small_blind_player.next



    def give_pot_to(self, players):
        reward = self.pot//len(players)
        for player in players:
            player.stack += reward



    def fold(self):

        self.history += "f"

        player = self.current_player

        #remove player from hand
        player.hand = ()

        if len(self.active_players) == 2:
            #give pot to winning player
            self.give_pot_to([player.next_active])
            #start a new hand
            self.new_hand()
        else:
            #update active player list
            self.active_players.remove(player)

            #update active player linked list
            player.next_active.prev_active = player.prev_active
            player.prev_active.next_active = player.next_active

            self.current_player = player.next_active

            player.next_active = None
            player.prev_active = None

            if not player in self.players_moved_this_round:
                self.players_moved_this_round.append(player)

            if self.total_bets[self.current_player] == max(self.total_bets.values()) and self.allPlayersMoved():
                if self.betting_round == len(self.betting_stage_public_cards) - 1:
                    #show down
                    self.showdown()
                    self.new_hand()
                else:
                    self.new_round()
                    self.history += "S"



    def bet(self, player, amount):
        paid = min(amount, player.stack)
        player.stack -= paid
        self.total_bets[player] += paid
        self.pot += paid



    def min_raise(self):
        self.history += "r"
        player = self.current_player
        call_amount = max(self.total_bets.values()) - self.total_bets[player]
        amount = call_amount + self.big_blind_amount
        self.bet(self.current_player, amount)
        self.next_player()
        if not player in self.players_moved_this_round:
            self.players_moved_this_round.append(player)



    def call(self):
        self.history += "c"
        player = self.current_player
        call_amount = max(self.total_bets.values()) - self.total_bets[player]
        self.bet(player, call_amount)
        self.next_player()
        if not player in self.players_moved_this_round:
            self.players_moved_this_round.append(player)
        if self.total_bets[self.current_player] == max(self.total_bets.values()) and self.allPlayersMoved():
            if self.betting_round == len(self.betting_stage_public_cards) - 1:
                #show down
                self.showdown()
                self.new_hand()
            else:
                self.new_round()
                self.history += "S"


    def turn_list_to_number(self, a):
        a = "0".join(list(map(str, a)))
        if a == '':
            return 0
        return int(a)
    

    def showdown(self):
        #needs work
        best_hand, best_qualities, best_rest = 0, 0, 0
        best_players = []
        for player in self.active_players:
            (hand, qualities, rest) = self.evaluate(player.hand, self.table_cards)
            qualities.reverse()
            rest.reverse()
            qualities = self.turn_list_to_number(qualities)
            rest = self.turn_list_to_number(rest)
            if hand > best_hand:
                best_hand, best_qualities, best_rest = hand, qualities, rest
                best_players = [player]
            elif hand == best_hand:
                if qualities > best_qualities:
                    best_hand, best_qualities, best_rest = hand, qualities, rest
                    best_players = [player]
                elif qualities == best_qualities:
                    if rest > best_rest:
                        best_hand, best_qualities, best_rest = hand, qualities, rest
                        best_players = [player]
                    elif rest == best_rest:
                        best_players.append(player)
        for player in best_players:
            print(player.name, "wins with", player.hand)
        self.give_pot_to(best_players)
                

    def allPlayersMoved(self):
        for player in self.active_players:
            if not player in self.players_moved_this_round:
                return False
        return True



    def new_round(self):

        self.players_moved_this_round = []

        #clear bets off table
        self.total_bets = {player:0 for player in self.players}

        #new betting round
        self.betting_round += 1

        #deal table cards for the current betting round
        self.table_cards += self.deal(self.betting_stage_public_cards[self.betting_round])

        #update current player
        self.current_player = self.find_active_player_after_dealer()



    def find_active_player_after_dealer(self):
        player = self.dealer.next
        while True:
            if player in self.active_players:
                return player
            player = player.next




    def new_hand(self):

        self.history = "B"

        #take players cards
        for player in self.players:
            player.hand = ()

        #clear table
        self.table_cards = ()

        self.num_hands += 1
        for player in self.players:
            self.scores[player] += player.stack - self.starting_stack
            player.stack = self.starting_stack

        #reset active player pool
        self.active_players = self.players[:]
        for player in self.players:
            player.next_active = player.next
            player.prev_active = player.prev

        self.players_moved_this_round = []

        self.betting_round = -1
        self.pot = 0

        #move dealer button along
        self.next_dealer()
        
        #set blinds
        self.set_blinds()

        self.new_round()

        #pay blinds
        self.bet(self.small_blind_player, self.small_blind_amount)
        self.bet(self.big_blind_player, self.big_blind_amount)

        self.set_current_player_to_after_bb()

        #new deck
        self.refresh_deck()

        #deal player cards
        for player in self.players:
            player.hand = self.deal(self.hand_size)

        



    def set_current_player_to_after_bb(self):

        self.current_player = self.big_blind_player.next



    def next_dealer(self):

        self.dealer = self.dealer.next


    def next_player(self):

        self.current_player = self.current_player.next_active



    def refresh_deck(self):

        self.deck = self.card_values*self.card_duplicates



    def deal(self, num):
        dealt = ()
        deck_size = len(self.deck)-1
        for i in range(num):
            dealt += (self.deck.pop(random.randint(0,deck_size-i)),)
        return dealt



    def check_pair_in_ordered(self, cards):
        for index, card in enumerate(cards[0:-1]):
            if card == cards[index+1]:
                return True, card, cards[0:index] + cards[index+2:len(cards)]
        return False, None, cards



    def check_3_of_a_kind_in_ordered(self, cards):
        for index, card in enumerate(cards[0:-2]):
            if card == cards[index+1] and card == cards[index+2]:
                return True, card, cards[0:index] + cards[index+3:len(cards)]
        return False, None, cards
    


    def check_4_of_a_kind_in_ordered(self, cards):
        for index, card in enumerate(cards[0:-3]):
            if card == cards[index+1] and card == cards[index+2] and card == cards[index+3]:
                return True, card, cards[0:index] + cards[index+4:len(cards)]
        return False, None, cards



    def check_straight_in_ordered(self, cards):
        straight_length = 0
        last_card = 0
        for card in cards:
            if card - last_card == 1:
                straight_length += 1
            elif card - last_card > 1:
                straight_length = 1
            if straight_length == self.min_straight_length:
                return True, card, []
            last_card = card
        return False, None, []



    def evaluate(self, hand, table_cards):
        hand = list(hand + table_cards)
        hand.sort()
        if self.card_duplicates >= 4 and len(hand) >= 4:
            valid, value, remaining = self.check_4_of_a_kind_in_ordered(hand)
            if valid:
                return 6, [value], remaining
        if self.card_duplicates >= 3 and len(hand) >= 5:
            valid, value, remaining = self.check_3_of_a_kind_in_ordered(hand)
            if valid:
                valid, value2, remaining = self.check_pair_in_ordered(remaining)
                if valid:
                    return 5, [value, value2], remaining
        if len(hand) >= self.min_straight_length:
            valid, value, remaining = self.check_straight_in_ordered(hand)
            if valid:
                return 4, [value], remaining
        if self.card_duplicates >= 3 and len(hand) >= 3:
            valid, value, remaining = self.check_3_of_a_kind_in_ordered(hand)
            if valid:
                return 3, [value], remaining
        if self.card_duplicates >= 2 and len(hand) >= 2:
            valid, value, remaining = self.check_pair_in_ordered(hand)
            if valid:
                valid, value2, remaining2 = self.check_pair_in_ordered(remaining)
                if valid:
                    return 2, [value2, value], remaining2
                return 1, [value], remaining
        return 0, [remaining[-1]], remaining[0:-2]

if __name__ == "__main__":
    X = Game(config.game_config)
    X.new_hand()

    D = Display(X)
    D.update()

    AI = {}

    file_data = open("data.txt", "r")
    for line in file_data.readlines():
        line_data = line.split(": ")
        values = line_data[-1][:-1].strip('][').split(', ')
        for value in values:
            value = float(value)
        key = []
        for data in line_data[:-1]:
            key.append(data)

        AI[str(key)] = values




    #main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    print(X.current_player.name, "fold")
                    X.fold()
                    D.update()
                elif event.key == pygame.K_c:
                    print(X.current_player.name, "call")
                    X.call()
                    D.update()
                elif event.key == pygame.K_r:
                    if max(X.total_bets.values()) - X.total_bets[X.current_player] < X.current_player.stack:
                        print(X.current_player.name, "raise")
                        X.min_raise()
                        D.update()
                elif event.key == pygame.K_a:
                    hand = list(X.current_player.hand)
                    hand.sort()
                    values = AI["['" + str(hand)+ "', '" + str(list(X.table_cards)) + "', '" + X.history + "']"]
                    ran = random.random()
                    #print(values)
                    if ran < float(values[0]):
                        print(X.current_player.name, "fold")
                        X.fold()
                        
                    elif ran < float(values[0]) + float(values[1]):
                        print(X.current_player.name, "call")
                        X.call()
                        
                    else:
                        print(X.current_player.name, "raise")
                        X.min_raise()
                        
                    D.update()
            if event.type == pygame.QUIT:
                running = False
        
        if X.current_player.name == "bob":
            time.sleep(1)
            hand = list(X.current_player.hand)
            hand.sort()
            try:
                values = AI["['" + str(hand)+ "', '" + str(list(X.table_cards)) + "', '" + X.history + "']"]
            except KeyError:
                print("key error! " + "['" + str(hand)+ "', '" + str(list(X.table_cards)) + "', '" + X.history + "']")
                values = [0.333, 0.333, 0.333]
            ran = random.random()
            #print(values)
            if ran < float(values[0]):
                print(X.current_player.name, "fold")
                X.fold()
                
            elif ran < float(values[0]) + float(values[1]):
                print(X.current_player.name, "call")
                X.call()
                
            else:
                print(X.current_player.name, "raise")
                X.min_raise()
                
            D.update()

    pygame.quit()



"""
counts = {hand:0 for hand in hand_quality}

iterations = 1_000_000
for i in range(iterations):
    deck = card_values*card_duplicates
    flop, deck = deal(deck, 3)
    hand, deck = deal(deck, 2)
    value, _, _ = evaluate(hand, flop)
    counts[value] += 1/iterations

print(counts)
"""


