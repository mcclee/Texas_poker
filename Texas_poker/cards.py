import random
mp = ['♠', '❤', '♣', '♦']
mn = {i: str(i) for i in range(2, 14)}
mn[14] = 'A'


class NoCardsException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class Card:
    def __init__(self, color, number):
        self.color = color
        self.number = number

    def __repr__(self):
        return f'{mp[self.color]} {mn[self.number]}'

    def __lt__(self, other):
        if type(other) is Card:
            return self.number < other.number
        return self.number < other

    def __ne__(self, other):
        if type(other) is Card:
            return self.number != other.number
        return self.number != other

    def __gt__(self, other):
        if type(other) is Card:
            return self.number > other.number
        return self.number > other

    def __le__(self, other):
        if type(other) is Card:
            return self.number <= other.number
        return self.number <= other

    def __ge__(self, other):
        if type(other) is Card:
            return self.number >= other.number
        return self.number >= other

    def __eq__(self, other):
        if type(other) is Card:
            return self.number == other.number
        return self.number == other

    def __sub__(self, other):
        if type(other) is Card:
            return self.number - other.number
        return self.number - other

    def __add__(self, other):
        if type(other) is Card:
            return self.number + other.number
        return self.number + other

    def __hash__(self):
        return hash(self.number)


class Deck:
    def __init__(self, i=1):
        """
        :param i: the number of sets
        """
        self.packs = i
        self.cards = self.new_cards(i)
        self.shuffle()

    def shuffle(self):
        """
        shuffle the current deck
        :return:
        """
        for i in range(len(self.cards) - 1, -1, -1):
            random_index = random.randint(0, i)
            self.cards[i], self.cards[random_index] = self.cards[random_index], self.cards[i]

    def new_deck(self):
        """
        refill the deck
        :return:
        """
        self.cards = self.new_cards(self.packs)
        self.shuffle()

    def new_cards(self, sets):
        """
        generate some sets of cards
        :param sets:
        :return:
        """
        cards = []
        for _ in range(sets):
            for color in (0, 1, 2, 3):
                for number in range(2, 15):
                    cards.append(Card(color, number))
        return cards

    def get_card(self):
        """
        get one card
        :return:
        """
        if self.cards:
            return self.cards.pop()
        raise NoCardsException('No card in the case!')


if __name__ == '__main__':
    d = Deck()
    '''
    while True:
        try:
            print(d.get_card())
        except NoCardsException as no:
            print(no.message)
            break'''
    a1 = Card(1, 3)
    a2 = Card(2, 14)
    print([a1, a2].count(a1))
    print([a1, a2])
