import random
import time
from collections import deque
import rules
import cards
import threading
from player import Player
import game_public


class TexasPoke(threading.Thread):

    def __init__(self, gh, base=2):
        super(TexasPoke, self).__init__()
        self.queue = []
        self.base = self.current_base = base
        self.rule = rules.Rules()
        self.deck = cards.Deck()
        self.dealer = Player(-1, 100000, None)
        self.players = {}
        self.gh = gh

    def join_game(self, players):
        for p in players:
            self.queue.append(players[p])
            self.players[players[p].id] = players[p]
        random.shuffle(self.queue)

    def start_game(self):

        def proccess(i, ind):
            c = 0
            if players[ind % len(turn_coins)] == 1:
                return 0
            value = i.add_value(self.current_base)
            if value == 0:
                players[ind % len(turn_coins)] = 1
            else:
                turn_coins[ind % len(turn_coins)] = value
                if value > self.current_base:
                    c = 1
                    self.current_base = value
            return c

        def oneturn(beg, tl):
            while beg < tl:
                i = self.queue[beg % len(turn_coins)]
                c = proccess(i, beg)
                if players.count(0) < 2:
                    for i in range(len(coins)):
                        coins[i] += turn_coins[i]
                    return self.check_winner(coins, players)
                if c == 1:
                    tl = len(self.queue) + beg
                self.gh.broadcast(f'Current base is ${self.current_base}')
                beg += 1

        self.gh.start = True
        self.gh.broadcast(f'We have {len(self.queue)} players. Start!')
        self.gh.broadcast(''.join('Player ' + str(i.id) + ' has ' + str(i.coins) + ' coins. ' for i in self.queue))
        self.deck.new_deck()
        players = [0] * len(self.queue)
        coins = [0] * len(self.queue)
        self.current_base = self.base
        for i in self.queue:
            i.add_card(self.deck.get_card())
            i.add_card(self.deck.get_card())

        turn_coins = [0] * len(self.queue)
        turn_length = len(self.queue)
        self.gh.broadcast(f'Player{self.queue[0].id} is Small Blind!')
        turn_coins[0] = self.current_base >> 1
        self.gh.broadcast(f'Player {self.queue[1].id} is Big Blind!')
        turn_coins[1] = self.current_base
        oneturn(2, turn_length + 2)

        for i in range(len(coins)):
            coins[i] += turn_coins[i]

        for _ in range(3):
            self.dealer.add_card(self.deck.get_card())
        self.gh.broadcast(f'Public cards has been dispatched.')
        self.gh.set_public(self.dealer.display())

        for _ in range(3):
            turn_coins = [0] * len(self.queue)
            turn_length = len(self.queue)
            oneturn(0, turn_length)
            for i in range(len(coins)):
                coins[i] += turn_coins[i]
            if len(self.dealer.cards) < 5:
                self.dealer.add_card(self.deck.get_card())
                self.gh.broadcast(f'Public cards has been dispatched.')
                self.gh.set_public(self.dealer.display())

        return self.check_winner(coins, players)

    def check_winner(self, coins, players):
        cad = []
        for index, i in enumerate(self.queue):
            i.coins -= coins[index]
            if players[index] == 0:
                i.cards.extend(self.dealer.cards)
                i.cards.sort()
                self.gh.broadcast(f'Player {str(i.id)} cards are: {i}')
                cad.append(i)
        winners = self.rule.winner(cad)
        money = sum(coins) // len(winners)
        for p in winners:
            p.coins += money
        t = f'He got {money} coins. His cards are: {winners[0]}'
        if len(winners) > 1:
            t = f'Each of them got {money} coins. Their cards are: {"".join(winners)}'

        self.gh.broadcast(f'Winners are {" ".join("Player " + str(i.id) for i in winners)}. ' + t)

    def gamp_loop(self):
        while True:
            while len(self.gh.players) == game_public.player_limitation:
                if len(self.gh.players) == game_public.player_limitation:
                    self.join_game(self.gh.players)
                    self.start_game()
                    self.gh.broadcast('')
                    self.gh.start = False
                    for i in self.queue:
                        i.reset()
                    self.dealer.reset()
                    self.gh.set_public(self.dealer.display())
                    self.gh.clearall()
                    self.queue = deque([])
                else:
                    self.gh.broadcast('No enough players')
            time.sleep(0.5)

    def run(self) -> None:
        self.gamp_loop()


if __name__ == '__main__':
    pass


