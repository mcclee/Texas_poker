from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, Response, make_response
import time
from flask_cors import CORS
import random
from repos import TexasPoke as tp
from player import Player
from flask import jsonify
from collections import deque
import game_public
import sqlite3
import User

app = Flask(__name__)
CORS(app)
players = {}  # id: gamer_ID
realtime = {} # code: [user, password]

class GameHandler:
    def __init__(self, g):
        self.globe = g
        self.content = deque([])
        self.request = [-1, -1]  # id: content
        self.response = ''
        self.option = -1
        self.start = False
        self.public = ''
        self.counter = 0
        self.ls = -1
        self.json = None
        self.players = players
        self.game = None

    def broadcast(self, s):
        """
        :param s: content of the broadcast
        :return:
        """
        if len(self.content) >= 10:
            self.content.popleft()
        self.content.append(s)
        self.counter += 1
        print(s)

    def intable(self, v):
        try:
            int(v)
        except ValueError:
            return False
        return True

    def clearall(self):
        self.request = [-1, -1]
        self.response = ''
        self.option = -1

    def get_broadcast(self):
        if self.ls != self.counter:
            self.ls = self.counter
            dic = {}
            for j, i in enumerate(self.content):
                dic[j] = i
            self.json = jsonify(dic)
        return self.json

    def set_public(self, s):
        self.public = s

    def get_public(self):
        return self.public

    def set_game(self, game):
        self.game = game

    def send_request(self, request):
        if self.game:
            return self.game.next_step(request)
        return '0'


gh = GameHandler(g)
tpgame = tp(gh, game_public.player_limitation)
gh.game = tpgame
user_handler = User.DB('test.db')


@app.route('/test', methods=['GET'])
def show_entries():
    a = request.cookies.get('username')
    return str(hash(str(random.randint(1, 1000))))[10: 18]


@app.route('/join_game', methods=['GET'])
def join():
    dic = {
        'content': '',
        'ID': ''}
    if len(players) >= game_public.player_limitation:
        return jsonify(dic)
    v = str(hash(str(random.randint(1, 1000))))[10: 18]
    p = Player(v, 1000, gh)
    players[v] = p
    tpgame.join_game(p)
    if len(players) == game_public.player_limitation:
        tpgame.next_step([0, 0, 0])
    print(players)
    dic['ID'] = v
    dic['content'] = f'Join the game successfulllllly, your id is {v}. When the next game start, you will be notified.'
    return jsonify(dic)


@app.route('/ingame/<ID>', methods=['GET'])
def check_status(ID):
    if gh.start is True:
        if ID == gh.request[0]:
            return str(gh.request[1])
    return gh.get_broadcast()


@app.route('/ingame/public', methods=['GET'])
def get_public():
    return gh.get_public()


@app.route('/ingame/get_card/<ID>', methods=['GET'])
def get_card(ID):
    if gh.game.start and ID in tpgame.players:
        return tpgame.players[ID].get_cards()
    else:
        return ''


@app.route('/ingame/<ID>/option/<option>', methods=['GET'])
def select_option(ID, option):
    if ID in players:
        players[ID].request[1] = int(option)
        return gh.send_request(players[ID].request)
    return '0'


@app.route('/ingame/<ID>/value/<value>', methods=['GET'])
def select_value(ID, value):
    if ID in players:
        players[ID].request[1] = 1
        players[ID].request[2] = int(value)
        gh.send_request(players[ID].request)
        return '1'
    return '0'


@app.route('/ingame/<ID>/say/<said>', methods=['GET'])
def say(ID, said):
    gh.broadcast(f'憨批 {ID} 说:' + str(said))
    return '1'


@app.route('/ingame/<ID>/quit', methods=['GET'])
def quit(ID):
    gh.broadcast(f'Player {ID} quit the playing game.')
    if ID in players:
        if gh.game:
            gh.game.quit(players[ID])
        del players[ID]
    return '1'


def new_dic(username, dic):
    code = str(hash(str(random.randint(1, 1000)) + username))[10: 26]
    dic['ID'] = username
    dic['content'] = code
    dic['status'] = '1'
    realtime[code] = dic


@app.route('/login/<username>/<psw>', methods=['GET'])
def login(username, psw):
    dic = {
        'status': '0',
        'content': '',
        'ID': ''}
    res = user_handler.login(username, psw)
    if len(res) == 0:
        return jsonify(dic)
    new_dic(username, dic)
    return jsonify(dic)


@app.route('/register/<username>/<psw>', methods=['GET'])
def register(username, psw):
    dic = {
        'status': '0',
        'content': '',
        'ID': ''}
    if not user_handler.register(username, psw):
        return jsonify(dic)
    new_dic(username, dic)
    return jsonify(dic)


@app.route('/read_session/<session>', methods=['GET'])
def read_session(session):
    dic = {
        'status': '0',
        'content': '',
        'ID': ''}
    if session is None or session not in realtime:
        return jsonify(dic)
    return jsonify(realtime[session])


if __name__ == "__main__":
    app.run(host=game_public.host, port=5000, debug=True)
