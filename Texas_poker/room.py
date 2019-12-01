import game_public
from Texas_poker import TexasPoke as tp


class Room:
    def __init__(self, gh, room_number, size):
        self.gh = gh
        self.ID = room_number
        self.players = {}  # id: player
        self.size = size
        self.game = tp(gh, size)

    def join(self, player):
        if player.id in self.players:
            return
        self.players[player.id] = player
        self.game.join_game(player)
        if len(self.players) == self.size:
            self.gh.broadcast('Candidates enough, game start!')
            self.game.next_step([0, 0, 0])

    def leave(self, player):
        if player.id not in self.players:
            return
        del self.players[player]
        self.game.quit(player)