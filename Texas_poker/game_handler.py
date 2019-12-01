from collections import deque

from flask import jsonify


class GameHandler:
    def __init__(self, g):
        self.globe = g
        self.content = deque([])
        self.start = False
        self.public = ''
        self.counter = 0
        self.ls = -1
        self.json = None
        self.game = None
        self.db = None
        self.vs = [0, 0, 0]  # change of broadcast, public cards, personal cards

    def set_db(self, db):
        self.db = db

    def broadcast(self, s):
        """
        :param s: content of the broadcast
        :return:
        """
        if len(self.content) >= 10:
            self.content.popleft()
        self.content.append(s)
        self.counter += 1
        self.vs[0] += 1
        print(s)

    def intable(self, v):
        try:
            int(v)
        except ValueError:
            return False
        return True

    def get_broadcast(self):
        if self.ls != self.counter:
            self.ls = self.counter
            dic = {-1: self.vs[0]}
            for j, i in enumerate(self.content):
                dic[j] = i
            self.json = jsonify(dic)
        return self.json

    def set_public(self, s):
        self.public = s
        self.vs[1] += 1

    def get_public(self):
        return self.public

    def set_game(self, game):
        self.game = game

    def send_request(self, request):
        if self.game:
            return self.game.next_step(request)
        return '0'

    def get_coins(self, ID):
        return self.db.get_coins(ID)

    def update(self, request):
        change = {i: 0 for i in range(3)}
        for i in range(3):
            if int(request[i]) != self.vs[i]:
                change[i] = 1
        return change

    def add_personal_cards(self):
        self.vs[2] += 1