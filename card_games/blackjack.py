import cards


class Blackjack:
    game_over = False

    def __init__(self):
        self.deck = cards.Deck()
        self.money = 100
        self.money_lost = 0
        self.bet = 0

    def _calc_points(self, hand: list) -> int:
        """Calculate points for the hand supplied."""
        num_aces = 0
        points = 0
        for card in hand:
            if card.value in ("Jack", "Queen", "King"):
                points += 10
            elif card.value == "Ace":
                num_aces += 1
                points += 11
            else:
                points += int(card.value)

        while points > 21 and num_aces:
            points -= 10
            num_aces -= 1

        return points

    def _test_game_over(self):
        """Check if game_over (i.e. break conditions):
        - player has 21
            dealer will hit until equal to 21 or bust
        - player has over 21
            player busts
        """
        if self.dealer_points < self.player_points == 21:
            self.dealer_hit()

        elif self.player_points > 21:
            self.game_over = True

    def _hit(self, hand: list) -> int:
        """Hit and return calculated points.

        Args:
            hand [list]: list of Card objects. Expect either self.player_hand or
            self.dealer_hand
        """
        new_card = self.deck.deal_cards(1)
        hand.extend(new_card)
        return self._calc_points(hand)

    def _show_last_card(self):
        """Draw last card on lose or draw."""
        return self.deck.deal_cards(1)

    def _print_cards_per(self, player: str, hand: list):
        """Print cards and points per-player.

        - if player or game_over == True, then all cards will be shown and the point
        total displayed.
        - if dealer and not game_over, then only the dealer's first card will be shown.
        The point total for the dealer will be only an empty string.

        Args:
            player [str]: 'dealer' or 'player'. Used to determine which hand to display.
            hand [list]: list of Card objects. Expect either self.player_hand or
            self.dealer_hand
        """
        points = ""
        if player == "player" or self.game_over:
            cards_str = ", ".join(str(i) for i in hand)
            points = self.player_points if player == "player" else self.dealer_points

        else:
            cards_str = f"{hand[0]}, UNKNOWN"

        print(
            f"{player.capitalize()} Hand:\n\t{cards_str}",
            f"\n\tPoints: {points}",
        )

    def _laugh_at_player(self):
        """Show last card to the player to see if they would have won."""
        last_card = self._show_last_card()
        print(f"\tThe next card was the {str(last_card[0])}\n")

        self.player_hand.extend(last_card)
        points = self._calc_points(self.player_hand)

        if 21 >= points > self.dealer_points:
            print("\tHaha, you would have won, sucker!")

    def calc_bet(self, win=False):
        """Calculate winnings/losings."""
        if win:
            self.money += self.bet

        else:
            self.money -= self.bet
            self.money_lost += self.bet

    def show_me_the_money(self):
        """Function to print current money pot."""
        print(f"\nYou have: ${self.money}")
        print(f"You have lost: ${self.money_lost}\n")

    def deal(self):
        """Deal new hand to players.

        - deal 2 to player and dealer
        - Calculate points for each player
        - Test if player has 21, no need to prompt for stay/hit
        """
        self.dealer_hand = self.deck.deal_cards(2)
        self.player_hand = self.deck.deal_cards(2)

        self.dealer_points = self._calc_points(self.dealer_hand)
        self.player_points = self._calc_points(self.player_hand)

        self._test_game_over()

    def player_hit(self):
        """Hit player and test game_over."""
        self.player_points = self._hit(self.player_hand)
        self._test_game_over()

    def dealer_hit(self):
        """Hit dealer, looping until dealer_points are equal to or greater
        than the player_points, then changing game_over to True."""
        while self.player_points > self.dealer_points:
            self.dealer_points = self._hit(self.dealer_hand)

        self.game_over = True

    def show_cards(self):
        """Show the cards & points for both the dealer and player."""
        self._print_cards_per("dealer", self.dealer_hand)
        self._print_cards_per("player", self.player_hand)
        print("")

    def show_winner(self):
        """Determine winner, print GAME OVER string."""
        msg = "\n***** Game Over -- {} *****\n"

        if self.player_points == self.dealer_points:
            print(msg.format("DRAW"))
            print("At least you didn't lose any money.")
            self._laugh_at_player()

        elif self.player_points > 21 or 21 > self.dealer_points > self.player_points:
            self.calc_bet()
            print(msg.format("YOU LOSE"))
            print(f"You lost ${self.bet}")
            self._laugh_at_player()

        else:
            self.calc_bet(win=True)
            print(msg.format("YOU WIN"))
            print(f"You won ${self.bet}!")


#
# Pytests
#


def create_hand(hand: list) -> list:
    """Initialize card namedtuple."""
    return [cards.Card(i, "Hearts") for i in hand]


def test_hands():
    """Test various hand conditions."""
    hands = [
        (12, ["Ace", "Ace", "10"]),
        (13, ["Ace", "Ace", "Ace", "10"]),
        (14, ["Ace", "Ace", "Ace", "Ace", "10"]),
        (17, ["Ace", "Ace", "King", "5"]),
        (18, ["Ace", "Ace", "Ace", "King", "5"]),
        (26, ["Ace", "King", "Queen", "5"]),
    ]

    game = Blackjack()
    for hand_points in hands:
        hand = create_hand(hand_points[1])
        points = game._calc_points(hand)
        assert points == hand_points[0]


def test_21():
    """Test if player score == 21 ends the game."""
    game = Blackjack()
    game.deal()
    game.player_points = 21
    game._test_game_over()
    assert game.game_over


def test_lose_bet():
    """Test bet if lose."""
    game = Blackjack()
    game.bet = 10
    game.calc_bet(win=False)
    assert game.money == 90
    assert game.money_lost == 10


def test_win_bet():
    """Test bet if win."""
    game = Blackjack()
    game.bet = 10
    game.calc_bet(win=True)
    assert game.money == 110
    assert game.money_lost == 0


#
# End Pytests
#


def main():
    game = Blackjack()

    play = True
    while play:
        game.deal()
        game.show_me_the_money()

        bet = 0
        while not bet:

            bet_str = input("Place your bet: ")
            try:
                bet = int(bet_str)

            except ValueError:
                print("Must be valid bet.")
                bet = False

            else:
                if bet > game.money:
                    print("You are too poor for that bet.")
                    bet = False
                elif bet <= 0:
                    print("Stop betting nonsense.")
                    bet = False
                elif bet == game.money:
                    print("Feeling cocky!")

        print(f"You bet ${bet}\n")
        game.bet = bet
        game.show_cards()

        while not game.game_over:

            response = ""
            while response not in ("hit", "stay"):
                response = input("Hit or stay? ").lower()

            if response == "hit":
                print("")
                game.player_hit()
                game.show_cards()

            elif response == "stay":
                game.dealer_hit()
                game.show_cards()

        game.show_winner()

        # play new game & reset
        print("=" * 50)
        if game.money == 0:
            print("You're broke, get out of the casino!")
            exit()
        new_game = ""
        while new_game not in ("yes", "no"):
            new_game = input("New Game? ").lower()
            print("")

        if new_game == "no":
            play = False
        else:
            game.game_over = False

    winnings = game.money - game.money_lost
    if winnings > 0:
        print(f"Good Game! You won a total of ${winnings}.")
    elif winnings < 0:
        print(f"You're not very good. You lost a total of ${winnings}.")
    else:
        print("Yay... You broke even...")


if __name__ == "__main__":
    main()
