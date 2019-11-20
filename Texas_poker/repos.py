import random
import time
from collections import deque
import rules
import cards
from player import Player
#from texas_poker_server import GameHandler


class TexasPoke:

    def __init__(self, gh, lt, base=2):
        self.queue = []
        self.base = self.current_base = base
        self.rule = rules.Rules()
        self.deck = cards.Deck()
        self.dealer = Player(-1, 100000, None)
        self.players = {}
        self.gh = gh
        self.start = False
        self.player_limitation = lt
        self.game_players = []
        self.game_coins = []
        self.game_turn_coins = []
        self.cur_turn = 0
        self.cur_loop = 0
        self.loop_max = 0
        self.cur_max = 0
        self.q = []

    def join_game(self, player):
        if player.id in self.players:
            return False
        self.queue.append(player)
        self.players[player.id] = player
        return True

    def quit(self, player):
        if player.id in self.players:
            del self.players[player.id]
            if not self.start:
                self.queue.remove(player)
            else:
                self.game_players[self.queue.index(player)] = 1
            self.q.append(player)

    def check_winner(self):
        cad = []
        for index, i in enumerate(self.queue):
            i.coins -= self.game_coins[index]
            if self.game_players[index] == 0:
                i.cards.extend(self.dealer.cards)
                i.cards.sort()
                self.gh.broadcast(f'Player {str(i.id)} cards are: {i}')
                cad.append(i)
        winners = self.rule.winner(cad)
        money = sum(self.game_coins) // len(winners)
        for p in winners:
            p.coins += money
        t = f'He got {money} coins. His cards are: {winners[0]}'
        if len(winners) > 1:
            t = f'Each of them got {money} coins. Their cards are both: {winners[0].__repr__()}'
        self.gh.broadcast(f'Winners are {" ".join("Player " + str(i.id) for i in winners)}. ' + t)

    def next_step(self, request):
        """
        :param request: id, operation, gold
        :return:
        """
        if self.start is False:
            self.game_start()
        else:
            player = self.queue[self.cur_loop % len(self.queue)]
            while player in self.q:
                self.turn([player.id, 3, 0])
                player = self.queue[self.cur_loop % len(self.queue)]
            return self.turn(request)
        return '0'

    def turn(self, request):
        """
        :param request: id, operation, gold
        :return:
        """
        if self.game_players[self.cur_loop % len(self.queue)] == 1:
            self.cur_loop += 1
            return '1'
        player = self.queue[self.cur_loop % len(self.queue)]
        if player.id != request[0]:
            return '0'
        if request[1] == 2:
            self.gh.broadcast(f'Player {player.id} followed the value {self.current_base}.')
            self.game_turn_coins[self.cur_loop % len(self.queue)] = self.current_base
        elif request[1] == 3:
            player.giveup = True
            self.gh.broadcast(f'Player {player.id} select to quit this game.')
            self.game_players[self.cur_loop % len(self.queue)] = 1
        else:
            self.gh.broadcast(f'Player {player.id} wanted to add!')
            value = request[2]
            if self.current_base > value or value > player.coins:
                return 'Not a valid money. Please input your value: '
            self.gh.broadcast(f'Player {player.id} rised the value to {value}.')
            self.game_turn_coins[self.cur_loop % len(self.queue)] = request[2]
            if value > self.current_base:
                self.current_base = value
                self.cur_max = self.cur_loop + len(self.queue)
        self.gh.broadcast(f'Current base is ${self.current_base}')
        self.cur_loop += 1
        if self.game_players.count(0) < 2:
            self.turn_conclude()
            self.close_game()
        if self.cur_loop == self.cur_max:
            self.turn_conclude()
            if self.cur_turn == 0:
                for _ in range(2):
                    self.dealer.add_card(self.deck.get_card())
            if len(self.dealer.cards) < 5:
                self.dealer.add_card(self.deck.get_card())
                self.gh.broadcast(f'Public cards has been dispatched.')
                self.gh.set_public(self.dealer.display())
            self.cur_turn += 1
            self.cur_loop = 0
            self.cur_max = len(self.queue)
            for i in range(len(self.game_turn_coins)):
                self.game_coins[i] += self.game_turn_coins[i]
        if self.cur_turn == 4:
            self.close_game()
        self.gh.broadcast(f'Now is Player {self.queue[self.cur_loop % len(self.queue)].id}')
        return '1'

    def close_game(self):
        self.check_winner()
        self.start = False
        for p in self.q:
            self.queue.remove(p)
        for i in self.queue:
            i.reset()
        self.dealer.reset()
        self.gh.set_public(self.dealer.display())
        self.gh.clearall()

    def turn_conclude(self):
        for i in range(len(self.game_turn_coins)):
            self.game_coins[i] += self.game_turn_coins[i]
        self.gh.broadcast(f'This turn coin deposit is {" ".join(str(i) for i in self.game_turn_coins)}')
        self.gh.broadcast(f'Total coin deposit is {" ".join(str(i) for i in self.game_coins)}')
        self.game_turn_coins = [0] * len(self.queue)

    def game_start(self):
        for i in self.queue:
            if i.id not in self.players:
                self.queue.remove(i)
        if len(self.queue) < self.player_limitation:
            self.gh.broadcast(f'No enough players, players {len(self.queue)} of {self.player_limitation} now')
            return False
        random.shuffle(self.queue)
        self.q = []
        self.start = True
        self.gh.broadcast(f'We have {len(self.queue)} players. Start!')
        self.gh.broadcast(''.join('Player ' + str(i.id) + ' has ' + str(i.coins) + ' coins. ' for i in self.queue))
        self.deck.new_deck()
        self.game_coins = [0] * len(self.queue)
        self.game_players = [0] * len(self.queue)
        self.current_base = self.base
        self.loop_max = len(self.queue)
        self.cur_turn = 0
        for i in self.queue:
            i.add_card(self.deck.get_card())
            i.add_card(self.deck.get_card())
        self.game_turn_coins = [0] * len(self.queue)
        self.gh.broadcast(f'Player {self.queue[0].id} is Small Blind!')
        self.game_turn_coins[0] = self.current_base >> 1
        self.gh.broadcast(f'Player {self.queue[1].id} is Big Blind!')
        self.game_turn_coins[1] = self.current_base
        self.cur_max = self.loop_max + 2
        self.cur_loop = 2
        self.gh.broadcast(f'Now is Player {self.queue[self.cur_loop % len(self.queue)].id}')


if __name__ == '__main__':
    p1 = Player(1, 1000, None)
    p2 = Player(2, 1000, None)
    p3 = Player(3, 1000, None)
    '''gh = GameHandler(None)
    g = TexasPoke(gh, 3)
    g.join_game(p1)
    g.join_game(p2)
    g.join_game(p3)
    for j in range(300):
        for i in (1, 2, 3):
            g.next_step([i, 2, 5])
        if j == 0:
            print(p1)
            print(p2)
            print(p3)
        print(g.dealer)'''