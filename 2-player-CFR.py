import random
import poker
import config
import time


FOLD, CALL, RAISE, num_actions = 0, 1, 2, 3
action_map = {FOLD: "f", CALL: "c", RAISE: "r"}
nodeMap = {}
dealer = 1

class Node:
    def __init__(self, actions):
        self.num_actions = actions
        self.info_set = ""
        self.strategy = [0 for _ in range(self.num_actions)]
        self.regret_sum = [0 for _ in range(self.num_actions)]
        self.strategy_sum = [0 for _ in range(self.num_actions)]
        self.player, self.cards, self.length = None, None, None



    def getStrategy(self, realization_weight):
        normalizing_sum = 0
        for a in range(self.num_actions):
            self.strategy[a] =  max(self.regret_sum[a],0)
            normalizing_sum += self.strategy[a]
        for a in range(self.num_actions):
            if normalizing_sum > 0:
                self.strategy[a] /= normalizing_sum
            else:
                self.strategy[a] = 1 / self.num_actions
            self.strategy_sum[a] += realization_weight * self.strategy[a]
        return self.strategy
    


    def getAverageStrategy(self):
        average_strategy = [0 for _ in range(self.num_actions)]
        normalizing_sum = 0
        for a in range(self.num_actions):
            normalizing_sum += self.strategy_sum[a]
        for a in range(self.num_actions):
            if normalizing_sum > 0:
                average_strategy[a] = self.strategy_sum[a] / normalizing_sum
            else:
                average_strategy[a] = 1 / self.num_actions
        return average_strategy
    


    def __str__(self) -> str:
        return self.info_set + ": " + str(self.getAverageStrategy())
    


def train(iterations):
    util = 0
    game = poker.Game(config.game_config)
    for i in range(iterations):
        if i%1000 == 0:
            print(i)
        """if i == iterations // 2:
            for node in nodeMap.values():
                node.strategy_sum = [0,0]"""
        game.refresh_deck()
        cards0 = list(game.deal(2))
        cards0.sort()
        
        #cards0 = [4,4]
        #cards1 = [2,6]
        #for card in cards0:
        #    game.deck.remove(card)
        cards1 = list(game.deal(2))
        cards1.sort()
        table_cards = list(game.deal(1))
        table_cards.sort()
        util += cfr(game, cards0, cards1, table_cards, "B", [10, 5], 1, 1)
    print("Average game value:", util/iterations)



def showdown(game, cards0, cards1, table_cards):
    best_player = None
    best_hand, best_qualities, best_rest = 0, 0, 0
    for player, cards in enumerate([cards0, cards1]):
        (hand, qualities, rest) = game.evaluate(cards, table_cards)
        qualities.reverse()
        rest.reverse()
        qualities = game.turn_list_to_number(qualities)
        rest = game.turn_list_to_number(rest)
        if hand > best_hand:
            best_hand, best_qualities, best_rest = hand, qualities, rest
            best_player = player
        elif hand == best_hand:
            if qualities > best_qualities:
                best_hand, best_qualities, best_rest = hand, qualities, rest
                best_player = player
            elif qualities == best_qualities:
                if rest > best_rest:
                    best_hand, best_qualities, best_rest = hand, qualities, rest
                    best_players = player
                elif rest == best_rest:
                    return None
    return best_player
    



def cfr(game, cards0, cards1, table_cards, history, bets, p0, p1):
    #print(history)
    #print(pot)
    #time.sleep(0.5)
    round_history = history.split("S")[-1]
    player = len(round_history)%2
    #print(player)
    opponent = 1 - player
    round_plays = len(round_history.split("B")[-1])
    if player == 0:
        player_cards = cards0
    else:
        player_cards = cards1

    if history[-1] == "f":
        return bets[opponent]
    if round_plays > 1:
        terminal_call = history[-1] == "c"
        if terminal_call:
            if not "S" in history:
                return -cfr(game, cards0, cards1, table_cards, history+"S", bets, p0, p1)
            else:
                if showdown(game, cards0, cards1, table_cards) == player:
                    return bets[player]
                elif showdown(game, cards0, cards1, table_cards) == opponent:
                    return -bets[player]
                else:
                    return 0
        

    if "S" in history:
        info_set = str(player_cards) + ": " + str(table_cards) + ": " + history
    else:
         info_set = str(player_cards) + ": " + str([]) + ": " + history

    amount_to_call = bets[opponent] - bets[player]

    try:
        node = nodeMap[info_set]
    except KeyError:
        if bets[player] > 40 - amount_to_call:
            node = Node(2)
        else:
            node = Node(3)
        node.info_set = info_set
        node.player = player
        node.cards = player_cards
        node.length = len(history)
        nodeMap[info_set] = node

    strategy = node.getStrategy(p0 if player == 0 else p1)
    util = [0 for _ in range(node.num_actions)]
    nodeUtil = 0
    
    
    
    for a in range(node.num_actions):
        action = action_map[a]
        nextHistory = history + action
        bet = 0
        if action == "c":
            bet = amount_to_call
        elif action == "r":
            bet = amount_to_call + 10
        if player == 0:
            util[a] = -cfr(game, cards0, cards1, table_cards, nextHistory, [bets[0]+bet,bets[1]], p0 * strategy[a], p1)
        else:
            util[a] = -cfr(game, cards0, cards1, table_cards, nextHistory, [bets[0],bets[1]+bet], p0, p1 * strategy[a])
        #print(cards0, cards1, table_cards, history, player, action, util[a])
        nodeUtil += strategy[a] * util[a]

    for a in range(node.num_actions):
        regret = util[a] - nodeUtil
        node.regret_sum[a] += (p1 if player == 0 else p0) * regret

    return nodeUtil

game = poker.Game(config.game_config)
print(showdown(game, [2,2], [4,4], [3]))

iterations = 1_000_000
train(iterations)

file_data = open("data.txt", "w")
for value in nodeMap.values():
    file_data.writelines(str(value)+"\n")
file_data.close()
#for node in nodeMap.values():
#    if node.cards == [4,4]:
#        print(node)