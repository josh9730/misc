from cards import Deck


class Blackjack:
    game_over = False

    def __init__(self):
        self.deck = Deck()

    def deal(self):
        if self.deck.cards_in_deck() < 4:
            self.deck.add_new_deck()

        self.dealer_hand = self.deck.deal_cards(2)
        self.player_hand = self.deck.deal_cards(2)

        self.player_points = self.calc_points(self.player_hand)
        self.dealer_points = self.calc_points(self.dealer_hand)

    def calc_points(self, hand: list):
        ace = False
        points = 0
        for i in hand:
            if i.value in ("Jack", "Queen", "King"):
                points += 10
            elif i.value == "Ace":
                ace = True
                points += 11
            else:
                points += int(i.value)

        if ace and points > 21:
            points -= 10
        return points

    def player_hit(self):
        new_card = self.deck.deal_cards(1)
        self.player_hand.extend(new_card)
        self.player_points = self.calc_points(self.player_hand)

        if self.player_points >= 21:
            self.game_over = True

    def dealer_hit(self):
        while self.player_points >= self.dealer_points:
            new_card = self.deck.deal_cards(1)
            self.dealer_hand.extend(new_card)
            self.dealer_points = self.calc_points(self.dealer_hand)
        self.game_over = True

    def print_dealer(self, show_all=False):
        if not show_all:
            print(f"\tDealer Hand: {self.dealer_hand[0]}, UNKNOWN")
        else:
            cards_str = ", ".join(str(i) for i in self.dealer_hand)
            print(f"\tDealer Hand: {cards_str}")
            print(f"\t\tPoints: {self.dealer_points}")

    def print_player(self):
        cards_str = ", ".join(str(i) for i in self.player_hand)
        print(f"\tYour Hand: {cards_str}")
        print(f"\t\tPoints: {self.player_points}")

    def return_scores(self):
        if self.player_points > 21 or 21 >= self.dealer_points > self.player_points:
            print("\n\nGame Over -- YOU LOSE\n\n")
        else:
            print("\n\nGame Over -- YOU WIN\n\n")
        self.print_dealer(show_all=True)
        self.print_player()


if __name__ == "__main__":
    game = Blackjack()
    game.deal()
    game.print_dealer()
    print("")
    game.print_player()

    while not game.game_over:
        print("=" * 50)
        response = ""
        while response not in ("hit", "stay"):
            response = input("Hit or stay? ").lower()

        if response == "hit":
            game.player_hit()
            game.print_dealer()
            game.print_player()

        elif response == "stay":
            game.dealer_hit()

    print("=" * 50)
    game.return_scores()
