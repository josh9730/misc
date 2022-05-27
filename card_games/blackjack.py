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

    def calc_bet(self, win=False):
        if win:
            self.money += self.bet
        else:
            self.money -= self.bet
            self.money_lost += self.bet

    def show_me_the_money(self):
        """Function to print current money pot."""
        print(f"You have: ${self.money}")
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
        print("=" * 50)

    def show_winner(self):
        """Determine winner, print GAME OVER string."""
        msg = "\n** Game Over -- {} **\n"
        if self.player_points == self.dealer_points:
            print(msg.format("DRAW"))
            print("At least you didn' lose any money.")
            print(f"\tThe next card was the {str(self._show_last_card()[0])}\n")
        elif self.player_points > 21 or 21 > self.dealer_points > self.player_points:
            self.calc_bet()
            print(msg.format("YOU LOSE"))
            print(f"You lost ${self.bet}")
            print(f"\tThe next card was the {str(self._show_last_card()[0])}\n")
        else:
            self.calc_bet(win=True)
            print(msg.format("YOU WIN"))
            print(f"You won ${self.bet}!")


#
# Pytests
#


def create_hand(hand: list) -> list:
    return [cards.Card(i, "Hearts") for i in hand]


def test_hands():
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


#
# End Pytests
#


if __name__ == "__main__":
    game = Blackjack()

    play = True
    while play:
        game.deal()
        game.show_me_the_money()

        bet = 0
        # while isinstance(bet, int) and 0 < bet < game.money:
        while bet == False:
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
                    print("You got balls, son.")

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
        new_game = ""
        while new_game not in ("yes", "no"):
            new_game = input("New Game? ").lower()
            print("")

        if new_game == "no":
            play = False
        else:
            game.game_over = False

    print("Good Game!")