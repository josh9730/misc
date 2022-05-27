import random
from collections import namedtuple


class Card(namedtuple("Deck", ["value", "suit"])):
    def __str__(self):
        """Overload string return, ex: '2 of Hearts'"""
        return f"{self.value} of {self.suit}"


class Deck:
    def __init__(self):
        """Create Deck from Card class as a list of namedtuples and shuffle the deck."""
        self.suits = ["Hearts", "Spades", "Diamonds", "Clubs"]
        self.faces = ["Ace", "King", "Queen", "Jack"]
        self.values = [str(i) for i in range(2, 11)] + self.faces

        self.deck = self._create_deck()
        self.shuffle(self.deck)

    def _create_deck(self):
        """Create new deck."""
        return [Card(val, suit) for suit in self.suits for val in self.values]

    def cards_in_deck(self):
        """Return length of current deck."""
        return len(self.deck)

    def display(self):
        """Play 52 card pickup."""
        for card in self.deck:
            print(card)

    def shuffle(self, deck):
        """Shuffle deck."""
        random.shuffle(deck)

    def draw_one(self):
        """Draw one random card and put back into the deck."""
        return random.choice(self.deck)

    def deal_cards(self, number, return_list=False):
        """Deal defined number of cards from the deck, removing the cards."""
        if number > 52 or number > len(self.deck):
            self.add_new_deck()
        else:
            dealt_cards = [self.deck.pop(0) for _ in range(number)]
            if return_list:
                return [str(i) for i in dealt_cards]
            else:
                return dealt_cards

    def add_new_deck(self):
        """Create and shuffle a new deck, and add to existing deck."""
        new_deck = self._create_deck()
        self.shuffle(new_deck)
        self.deck.extend(new_deck)


if __name__ == "__main__":
    deck = Deck()

    print(deck.draw_one())
    print(deck.deal_cards(3, return_list=True))
    print(deck.cards_in_deck())
    deck.add_new_deck()
    # print(deck.display())
    print(deck.cards_in_deck())
