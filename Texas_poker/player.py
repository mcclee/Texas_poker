class Player:
    """
    A player has his/her own coins which default value is 1000. ID is dispatched when he join the game.
    """
    def __init__(self, Id, coins, gh):
        self.id = Id
        self.coins = coins
        self.cards = []
        self.giveup = False
        self.gh = gh
        self.request = [self.id, 0, 0]

    def reset_request(self):
        self.request = [self.id, 0, 0]

    def reset(self):
        self.cards.clear()
        self.giveup = False

    def add_value(self, current_value):
        self.gh.broadcast(f'Now is Player {self.id}')
        option = self.gh.getopt(f'current value is: {current_value}. Will you "(1: Add, 2: follow, 3: quit)": ', self.id)
        if option == 1:
            self.gh.broadcast(f'Player {self.id} wanted to add!')
            value = int(self.gh.getvalue(f'Please input your value: ', self.id))
            while current_value > value or value > self.coins:
                value = int(self.gh.getvalue('Not a valid money. Please input your value: ', self.id))
            self.gh.broadcast(f'Player {self.id} rised the value to {value}.')
        elif option == 2:
            value = current_value
            self.gh.broadcast(f'Player {self.id} followed the value {current_value}.')
        else:
            self.giveup = True
            self.gh.broadcast(f'Player {self.id} select to quit this game.')
            return 0
        return value

    def add_card(self, card):
        self.cards.append(card)

    def __repr__(self):
        return ', '.join(i.__repr__() for i in self.cards)

    def display(self):
        return f"Public cards are: {self.__repr__()}."

    def __getitem__(self, item):
        return self.cards[item]

    def get_cards(self):
        return f' your cards are: {self.__repr__()}'
