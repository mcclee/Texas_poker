from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, Response, make_response
from flask_cors import CORS
import random
from Texas_poker import TexasPoke as tp
from player import Player
from flask import jsonify
import game_public
import User
import game_handler

app = Flask(__name__)
CORS(app)
realtime = {}  # code: [user, password]
user_handler = User.DB(game_public.Db_name)


class ServerHandler:
    def __init__(self):
        self.ghs = {}  # gh id: gh
        self.index = 0
        self.ingames = {}  # player: room_id
        self.coins = {}
        self.players = {}

    def join(self, player, size, room_id):
        if room_id == '-1':
            for i in self.ghs:
                if self.ghs[i].game.player_limitation == size and len(self.ghs[i].game.players) < self.ghs[i].game.player_limitation:
                    if self.ghs[i].game.join_game(player):
                        self.ingames[player.id] = i
                        return True
        else:
            if self.ghs.get(room_id, None):
                if self.ghs[room_id].game.join_game(player):
                    self.ingames[player.id] = room_id
                return True
        return False

    def create(self, player, size):
        dic = {'status': '-1', 'content': ''}
        if self.ingames.get(player.id, None):
            dic['content'] = 'You have been in a game.'
            return dic
        gh = game_handler.GameHandler(g)
        gh.set_db(user_handler)
        self.ghs[self.index] = gh
        tpgame = tp(gh, size, server)
        gh.game = tpgame
        gh.game.join_game(player)
        self.ingames[player.id] = self.index
        self.index += 1
        dic['room'] = self.ingames[player.id]
        dic['status'] = '1'
        dic['content'] = self.ingames[player.id]
        return dic

    def check_player(self, ID):
        if ID in self.ingames:
            if self.ingames[ID] in self.ghs:
                return True
        return False

    def quit(self, ID):
        if self.ingames.get(ID, None):
            self.ghs[self.ingames[ID]].game.quit(self.players[ID])
            del self.ingames[ID]

    def update(self, ID, status_codes):
        if ID not in self.ingames:
            return {i: status_codes[i] for i in range(3)}
        if self.ingames[ID] not in self.ghs:
            return {i: status_codes[i] for i in range(3)}
        return self.ghs[self.ingames[ID]].update(status_codes)

    def get_broadcast(self, ID):
        if ID in self.ingames:
            if self.ingames[ID] in self.ghs:
                return self.ghs[self.ingames[ID]].get_broadcast()
        return jsonify({})

    def get_public(self, ID):
        if ID in self.ingames:
            if self.ingames[ID] in self.ghs:
                return {'pub': self.ghs[self.ingames[ID]].get_public(), 'vs': self.ghs[self.ingames[ID]].vs[1]}
        return {'pub': '', 'vs': 0}

    def get_cards(self, ID):
        if self.check_player(ID):
            return {'card': self.ghs[self.ingames[ID]].game.players[ID].get_cards(), 'vs': self.ghs[self.ingames[ID]].vs[2]}
        return {'card': '', 'vs': 0}

    def options(self, ID, option):
        if self.check_player(ID):
            self.players[ID].request[1] = int(option)
            return self.ghs[self.ingames[ID]].send_request(self.players[ID].request)
        return '0'

    def add_value(self, ID, value):
        if self.check_player(ID):
            self.players[ID].request[1] = 1
            self.players[ID].request[2] = int(value)
            res = self.ghs[self.ingames[ID]].send_request(self.players[ID].request)
            self.players[ID].reset_request()
            return res
        return '0'

    def say(self, ID, s):
        if self.check_player(ID):
            self.ghs[self.ingames[ID]].broadcast(f'憨批 {ID} 说:' + str(s))

    def set_coins(self, ID, coins):
        if ID in self.coins:
            self.coins[ID] = coins

    def login(self, username, dic, res):
        self.players[username] = Player(username, user_handler.get_coins(username), None)
        self.coins[username] = res
        code = str(hash(str(random.randint(1, 1000)) + username))[10: 26]
        dic['coins'] = str(self.coins[username])
        dic['ID'] = username
        dic['content'] = code
        dic['status'] = '1'
        realtime[code] = dic


server = ServerHandler()


@app.route('/test', methods=['GET'])
def show_entries():
    return str(hash(str(random.randint(1, 1000))))[10: 18]


@app.route('/ingame/update/<ID>/<i1>/<i2>/<i3>', methods=['GET'])
def upd(i1, i2, i3, ID):
    dic = server.update(ID, [i1, i2, i3])
    dic[3] = server.coins.get(ID, 0)
    return jsonify(dic)


@app.route('/join_game/<ID>/<size>/<room>', methods=['GET'])
def join(ID, size, room):
    dic = {
        'status': '0',
        'content': '',
        'ID': ''}
    if ID in server.ingames:
        dic['status'] = '1'
        dic['ID'] = ID
        dic['content'] = f'{ID}. Room number is {server.ingames[ID]}. You have been in a game. When the next game ' \
                         f'start, you will be notified. '
        return jsonify(dic)
    else:
        if not server.join(server.players[ID], int(size), room):
            dic['ID'] = ID
            dic['content'] = f'No such a room, {ID}, try later.'
            return jsonify(dic)
    dic['status'] = '1'
    dic['ID'] = ID
    dic['content'] = f'Join the game successfulllllly, {ID}. Room number is {server.ingames[ID]}. When the next game ' \
                     f'start, you will be notified. '
    return jsonify(dic)


@app.route('/create_game/<ID>/<size>/', methods=['GET'])
def create(ID, size):
    if ID in server.players:
        return jsonify(server.create(server.players[ID], int(size)))
    return jsonify({'status': '-1', 'content': 'You have not logged in.'})


@app.route('/ingame/broadcast/<ID>', methods=['GET'])
def broadcast(ID):
    return server.get_broadcast(ID)


@app.route('/ingame/public/<ID>', methods=['GET'])
def get_public(ID):
    return jsonify(server.get_public(ID))


@app.route('/ingame/get_card/<ID>', methods=['GET'])
def get_card(ID):
    return jsonify(server.get_cards(ID))


@app.route('/ingame/<ID>/option/<option>', methods=['GET'])
def select_option(ID, option):
    return server.options(ID, option)


@app.route('/ingame/<ID>/value/<value>', methods=['GET'])
def select_value(ID, value):
    return server.add_value(ID, value)


@app.route('/ingame/<ID>/say/<said>', methods=['GET'])
def say(ID, said):
    server.say(ID, said)
    return '1'


@app.route('/ingame/<ID>/quit', methods=['GET'])
def quit(ID):
    server.quit(ID)
    return '1'


@app.route('/login/<username>/<psw>', methods=['GET'])
def login(username, psw):
    dic = {
        'status': '0',
        'content': '',
        'coins': '0',
        'ID': ''}
    if username in server.players:
        return jsonify(dic)
    res = user_handler.login(username, psw)
    if len(res) == 0:
        return jsonify(dic)
    server.login(username, dic, res[0][1])
    return jsonify(dic)


@app.route('/register/<username>/<psw>', methods=['GET'])
def register(username, psw):
    dic = {
        'status': '0',
        'content': '',
        'coins': '0',
        'ID': ''}
    if username in server.players:
        return jsonify(dic)
    if not user_handler.register(username, psw):
        return jsonify(dic)
    server.login(username, dic, 1000)
    return jsonify(dic)


@app.route('/read_session/<session>', methods=['GET'])
def read_session(session):
    dic = {
        'status': '0',
        'content': '',
        'coins': '0',
        'ID': ''}
    if session is None or session not in realtime:
        return jsonify(dic)
    return jsonify(realtime[session])


if __name__ == "__main__":
    app.run(host=game_public.host, port=5000, debug=True)
