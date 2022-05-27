import random
from collections import namedtuple
from typing import Union


class Card(namedtuple("Card", ["value", "suit"])):
    def __str__(self):
        """Overload string return, ex: '2 of Hearts'"""
        return f"{self.value} of {self.suit}"


class Deck:
    def __init__(self):
        """Create Deck from Card class as a list of namedtuples and shuffle the deck."""
        self.deck = self._create_deck()
        self.shuffle(self.deck)

    def _create_deck(self) -> list:
        """Create new deck."""
        self.suits = ["Hearts", "Spades", "Diamonds", "Clubs"]
        self.values = [str(i) for i in range(2, 11)] + ["Ace", "King", "Queen", "Jack"]
        return [Card(val, suit) for suit in self.suits for val in self.values]

    def cards_in_deck(self) -> int:
        """Return length of current deck."""
        return len(self.deck)

    def display(self):
        """Play 52 card pickup."""
        for card in self.deck:
            print(card)

    def shuffle(self, deck: list):
        """Shuffle deck.

        Args:
            deck [list]: list of Card objects
        """
        random.shuffle(deck)

    def draw_one(self) -> Card:
        """Draw one random card and put back into the deck."""
        return random.choice(self.deck)

    def deal_cards(self, number, return_list=False) -> Union[list, Card]:
        """Deal defined number of cards from the deck, removing the cards.

        Args:
            number [int]: number of cards to deal
            return_list [bool]: return output as list if True
        """
        if number > 52 or number > len(self.deck):
            self.add_new_deck()
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
