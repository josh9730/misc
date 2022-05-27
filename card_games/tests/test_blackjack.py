import pytest
from card_games.blackjack import Blackjack
from card_games.cards import Card


@pytest.fixture
def double_ace():
    return [Card(i, "Hearts") for i in ["Ace", "Ace", "2"]]


def test_two_aces(double_ace):
    game = Blackjack()
    points = game._calc_points(double_ace)
    assert points == 14
