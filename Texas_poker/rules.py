import time
from functools import cmp_to_key
import cards
import Texas_poker


class Rules:
    def __init__(self):
        self.rules = [self.same_color_flush, self.four_of_a_kind, self.threeandtwo, self.flush, self.straight, self.justthree, self.two_pair, self.one_pair, self.high_card]
        self.cmps = [self.cmp_flush, self.cmp_flush, self.cmp_3_2, self.cmp_same_color, self.cmp_flush, self.cmp_3, self.cmp_2_2, self.cmp_2, self.cmp_same_color]

    def winner(self, players):
        """
        :param players: iterable value
        :return:
        """
        first_group = []
        for index, i in enumerate(self.rules):
            for j in players:
                cards = i(j.cards)
                if len(cards) < min(5, len(j.cards)):
                    continue
                else:
                    j.cards = cards
                    first_group.append(j)
            if first_group:
                winners = [max(first_group, key=cmp_to_key(self.cmps[index]))]
                for p in first_group:
                    if p != winners[0] and self.cmps[index](p, winners[0]) == 0:
                        winners.append(p)
                return winners

    def one_color(self, cards):
        dic = {}
        for i in cards:
            dic[i.color] = dic.get(i.color, 0) + 1
        c = max(dic, key=lambda x: dic[x])
        if dic[c] >= 5:
            return [cards[i] for i in range(len(cards)) if cards[i].color == c]
        return [-1]

    def flush(self, cards):
        c = self.one_color(cards)
        if len(c) > 4:
            return c[len(c) - 5: len(c)]
        return [-1]

    def cmp_same_color(self, x, y):
        for i in range(4, -1, -1):
            if x[i] > y[i]:
                return 1
            if x[i] < y[i]:
                return -1
        return 0

    def same_color_flush(self, cards):
        c = self.one_color(cards)
        c = self.straight(c)
        if len(c) > 4:
            return c
        return [-1]

    def cmp_flush(self, x, y):
        if x[4] > y[4]:
            return 1
        if x[4] < y[4]:
            return -1
        return 0

    def straight(self, cards):
        cards = sorted(set(cards))
        for i in range(len(cards) - 5, -1, -1):
            f = True
            for step in range(4):
                if cards[i + step].number != cards[i + step + 1].number - 1:
                    f = False
                    break
            if f is True:
                return cards[i: i + 5]
        return [-1]

    def four_of_a_kind(self, cards):
        for i in range(len(cards) - 1, -1, -1):
            r = cards.count(cards[i])
            if r >= 4:
                for j in range(len(cards) - 1, -1, -1):
                    if cards[j] != cards[i]:
                        return [k for k in cards if k == cards[i]][:4] + [cards[j]]
        return [-1]

    def threeandtwo(self, cards):
        for i in range(len(cards) - 1, -1, -1):
            r = cards.count(cards[i])
            if r >= 3:
                for j in range(len(cards) - 1, -1, -1):
                    if cards[j] != cards[i] and cards.count(cards[j]) > 1:
                        return [k for k in cards if k == cards[i]][:3] + [k for k in cards if k == cards[j]][:4]
        return [-1]

    def cmp_3_2(self, x, y):
        for i in (0, -1):
            if x[i] > y[i]:
                return 1
            elif x[i] < y[i]:
                return -1
        return 0

    def justthree(self, cards):
        for i in range(len(cards) - 1, -1, -1):
            r = cards.count(cards[i])
            if r >= 3:
                ans = [k for k in cards if k == cards[i]][:3]
                for j in range(len(cards) - 1, -1, -1):
                    if cards[j] != cards[i]:
                        ans.append(cards[j])
                    if len(ans) == 5:
                        return ans
        return [-1]

    def cmp_3(self, x, y):
        for i in (0, 3, 4):
            if x[i] > y[i]:
                return 1
            elif x[i] < y[i]:
                return -1
        return 0

    def two_pair(self, cards):
        for i in range(len(cards) - 2, -1, -1):
            if cards[i] == cards[i + 1]:
                for j in range(i - 1, -1, -1):
                    if cards[j] != cards[i] and cards.count(cards[j]) > 1:
                        ans = [k for k in cards if k == cards[i]][:2] + [k for k in cards if k == cards[j]][:2]
                        for k in range(len(cards) - 1, -1, -1):
                            if cards[k] not in ans:
                                ans.append(cards[k])
                                return ans
        return [-1]

    def cmp_2_2(self, x, y):
        for i in (0, 2, 4):
            if x[i] > y[i]:
                return 1
            elif x[i] < y[i]:
                return -1
        return 0

    def cmp_2(self, x, y):
        for i in (0, 2, 3, 4):
            if x[i] > y[i]:
                return 1
            elif x[i] < y[i]:
                return -1
        return 0

    def one_pair(self, cards):
        for i in range(len(cards) - 2, -1, -1):
            if cards[i] == cards[i + 1]:
                ans = [k for k in cards if k == cards[i]][:2]
                for k in range(len(cards) - 1, -1, -1):
                    if cards[k] != cards[i]:
                        ans.append(cards[k])
                    if len(ans) == 5:
                        return ans
        return [-1]

    def high_card(self, cards):
        """
        increasing
        :param cards:
        :return:
        """
        return cards[len(cards) - 5: len(cards)]


if __name__ == '__main__':

    t1 = time.time()
    r = Rules()
    '''
    for i in range(10):
        d = cards.Deck()
        dealer = texas_poker.Player(-1, 1000)
        a1 = texas_poker.Player(0, 1000)
        a2 = texas_poker.Player(1, 1000)
        a3 = texas_poker.Player(2, 1000)
        a4 = texas_poker.Player(3, 1000)
        for i in range(5):
            dealer.add_card(d.get_card())
        for i in range(2):
            a1.add_card(d.get_card())
            a2.add_card(d.get_card())
            a3.add_card(d.get_card())
            a4.add_card(d.get_card())
        a1.cards.extend(dealer.cards)
        a2.cards.extend(dealer.cards)
        a3.cards.extend(dealer.cards)
        a4.cards.extend(dealer.cards)
        ans = [a1, a2]
        print(sorted(a1))
        print(sorted(a2))
        w = r.winner(ans)
        print(w)
        print('\n')
    '''
    a1 = Texas_poker.Player(0, 1000, None)
    a2 = Texas_poker.Player(1, 1000, None)
    a1.cards = [cards.Card(1, 2), cards.Card(2, 6), cards.Card(1, 14), cards.Card(0, 3), cards.Card(3, 4), cards.Card(3, 2), cards.Card(1, 13)]
    a2.cards = [cards.Card(1, 14), cards.Card(1, 11), cards.Card(2, 9), cards.Card(3, 13), cards.Card(1, 10), cards.Card(2, 10), cards.Card(2, 12)]
    ans = [a1, a2]
    print(sorted(a1))
    print(sorted(a2))
    w = r.winner(ans)
    print(w)

