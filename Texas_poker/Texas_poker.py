import random
import rules
import cards
from player import Player
import game_public
from User import DB


class TexasPoke:

    def __init__(self, gh, lt, server, base=2):
        self.queue = []
        self.base = self.current_base = base
        self.__judge = rules.Rules()
        self.__deck = cards.Deck()
        self.__dealer = Player(-1, 100000, None)
        self.players = {}
        self.gh = gh
        self.start = False
        self.player_limitation = lt
        self.__game_players = []  # 0: on table, 1: give up
        self.__game_coins = []  # players' coins of the game
        self.__game_turn_coins = []  # players' coins of this turn
        self.__cur_turn = 0  # turn number
        self.__cur_loop = 0  # which loop of the turn
        self.__loop_max = 0  # how many loops should be in a turn
        self.__cur_max = 0  #
        self.__db_handler = DB(game_public.Db_name)
        self.server = server
        self.__pf = {}

    def playflow(self):
        l = len(max(self.queue, key=lambda x: len(x.id)).id)
        for i in range(len(self.queue)):
            self.__pf[i] = self.queue[i].id + ' ' * (l - len(self.queue[i].id) + 1)

    def join_game(self, player):
        if self.start or player.id in self.players:
            return False
        self.queue.append(player)
        self.players[player.id] = player
        self.gh.broadcast(f'{player.id} joined this game.')
        player.set_handler(self.gh)
        if len(self.queue) == self.player_limitation:
            self.next_step([0, 0, 0])
        return True

    def quit(self, player):
        if player.id in self.players:
            del self.players[player.id]
            player.set_handler(None)
            if not self.start:
                self.queue.remove(player)
            else:
                self.__game_players[self.queue.index(player)] = 1
            self.gh.broadcast(f'{player.id} left this game.')
            self.next_step([player.id, 3, 0])

    def check_winner(self):
        cad = []
        for index, i in enumerate(self.queue):
            i.coins -= self.__game_coins[index]
            if self.__game_players[index] == 0:
                i.cards.extend(self.__dealer.cards)
                i.cards.sort()
                self.gh.broadcast(f'Player {str(i.id)} cards are: {i}')
                cad.append(i)
        winners = self.__judge.winner(cad)
        money = sum(self.__game_coins) // len(winners)
        for p in winners:
            p.coins += money
        t = f'He got {money} coins. His cards are: {winners[0]}'
        if len(winners) > 1:
            t = f'Each of them got {money} coins. Their cards are both: {winners[0].__repr__()}'
        self.gh.broadcast(f'Winners are {" ".join("Player " + str(i.id) for i in winners)}. ' + t)
        for i in self.queue:
            self.__db_handler.insert(i.id, i.coins)
            self.server.set_coins(i.id, i.coins)

    def next_step(self, request):
        """
        :param request: id, operation, gold
        :return:
        """
        if self.start is False:
            self.game_start()
            return '0'
        else:
            return self.turn(request)

    def turn(self, request):
        """
        :param request: id, operation, gold
        :return:
        """
        if self.__game_players[self.__cur_loop % len(self.queue)] == 1:
            self.__cur_loop += 1
            self.gh.broadcast(f'Now is Player {self.queue[self.__cur_loop % len(self.queue)].id}')
            return '1'
        player = self.queue[self.__cur_loop % len(self.queue)]
        if player.id != request[0]:
            return '0'
        if request[1] == 2:
            self.gh.broadcast(f'Player {player.id} followed the value {self.current_base}.')
            self.__game_turn_coins[self.__cur_loop % len(self.queue)] = self.current_base
        elif request[1] == 3:
            player.giveup = True
            self.gh.broadcast(f'Player {player.id} select to quit this game.')
            self.__game_players[self.__cur_loop % len(self.queue)] = 1
        else:
            self.gh.broadcast(f'Player {player.id} wanted to add!')
            value = request[2]
            if self.current_base > value or value > player.coins:
                return '0'
            self.gh.broadcast(f'Player {player.id} rised the value to {value}.')
            self.__game_turn_coins[self.__cur_loop % len(self.queue)] = request[2]
            if value > self.current_base:
                self.current_base = value
                self.__cur_max = self.__cur_loop + len(self.queue)
        self.gh.broadcast(f'Current base is ${self.current_base}')
        self.__cur_loop += 1
        if self.__game_players.count(0) < 2:
            self.turn_conclude()
            self.close_game()
        if self.__cur_loop == self.__cur_max:
            self.turn_conclude()
            if self.__cur_turn == 0:
                for _ in range(2):
                    self.__dealer.add_card(self.__deck.get_card())
            if len(self.__dealer.cards) < 5:
                self.__dealer.add_card(self.__deck.get_card())
                self.gh.broadcast(f'Public cards has been dispatched.')
                self.gh.set_public(self.__dealer.display())
            self.__cur_turn += 1
            self.__cur_loop = 0
            self.__cur_max = len(self.queue)
        if self.__cur_turn == 4:
            self.close_game()
            return '1'
        self.gh.broadcast(f'Now is Player {self.queue[self.__cur_loop % len(self.queue)].id}')
        self.handle_next()
        return '1'

    def close_game(self):
        self.check_winner()
        self.start = False
        q = []
        for j in range(len(self.queue) - 1, -1, -1):
            if self.queue[j].id not in self.players:
                q.append(j)
        for j in q:
            self.queue.pop(j)
        for i in self.queue:
            i.reset()
        self.__dealer.reset()
        self.gh.set_public(self.__dealer.display())

    def turn_conclude(self):
        for i in range(len(self.__game_turn_coins)):
            self.__game_coins[i] += self.__game_turn_coins[i]
        self.gh.broadcast(f'This turn coin deposit is {" ".join(str(i) for i in self.__game_turn_coins)}')
        self.gh.broadcast(f'Total coin deposit is {" ".join(str(i) for i in self.__game_coins)}')
        self.__game_turn_coins = [0] * len(self.queue)

    def game_start(self):
        for i in self.queue:
            if i.id not in self.players:
                self.queue.remove(i)
        if len(self.queue) < self.player_limitation:
            self.gh.broadcast(f'No enough players, players {len(self.queue)} of {self.player_limitation} now')
            return False
        random.shuffle(self.queue)
        self.start = True
        self.gh.broadcast(f'We have {len(self.queue)} players. Start!')
        self.gh.broadcast(''.join('Player ' + str(i.id) + ' has ' + str(i.coins) + ' coins. ' for i in self.queue))
        self.all_set()
        for i in self.queue:
            i.add_card(self.__deck.get_card())
            i.add_card(self.__deck.get_card())
        self.gh.add_personal_cards()
        self.__game_turn_coins = [0] * len(self.queue)
        self.gh.broadcast(f'Player {self.queue[0].id} is Small Blind!')
        self.__game_turn_coins[0] = self.current_base >> 1
        self.gh.broadcast(f'Player {self.queue[1].id} is Big Blind!')
        self.__game_turn_coins[1] = self.current_base
        self.__cur_max = self.__loop_max + 2
        self.__cur_loop = 2
        self.gh.broadcast(f'Now is Player {self.queue[self.__cur_loop % len(self.queue)].id}')

    def all_set(self):
        self.__deck.new_deck()
        self.__game_coins = [0] * len(self.queue)
        self.__game_players = [0] * len(self.queue)
        self.current_base = self.base
        self.__loop_max = len(self.queue)
        self.__cur_turn = 0

    def handle_next(self):
        if not self.start:
            return
        player = self.queue[self.__cur_loop % len(self.queue)]
        while self.__game_players[self.__cur_loop % len(self.queue)] == 1 or player.id not in self.players:
            self.turn([player.id, 3, 0])
            player = self.queue[self.__cur_loop % len(self.queue)]


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