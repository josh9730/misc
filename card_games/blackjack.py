import cards


class Blackjack:
    game_over = False

    def __init__(self):
        self.deck = cards.Deck()

    def _calc_points(self, hand: list) -> int:
        """Calculate points for the hand supplied."""
        ace = False
        points = 0
        for card in hand:
            if card.value in ("Jack", "Queen", "King"):
                points += 10
            elif card.value == "Ace":
                ace = True
                points += 11
            else:
                points += int(card.value)

        if ace and points > 21:
            points -= 10
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
        elif self.player_points > 21 or 21 > self.dealer_points > self.player_points:
            print(msg.format("YOU LOSE"))
        else:
            print(msg.format("YOU WIN"))


if __name__ == "__main__":
    game = Blackjack()

    play = True
    while play:
        game.deal()
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
