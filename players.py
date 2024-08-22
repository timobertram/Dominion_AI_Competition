from game import TreasureCard, VictoryCard, CurseCard
import numpy as np
import random


# Player Class
class Player:
    def __init__(self, name):
        self.name = name
        self.deck = []
        self.hand = []
        self.discard_pile = []
        self.played_cards = []
        self.actions = 0
        self.buys = 0
        self.coins = 0

    def reset(self):
        self.__init__(self.name)

    def refresh_deck(self):
        self.deck = np.random.permutation(self.discard_pile).tolist()
        self.discard_pile = []

    def print_hand(self):
        print(f"{self.name}'s hand: {[card.name for card in self.hand]}")

    def draw(self, num):
        for _ in range(num):
            if not self.deck:
                self.refresh_deck()
            if self.deck:
                self.hand.append(self.deck.pop(0))
        print(f"{self.name} draws {num} cards.")

    def play_action(self, card, game):
        if self.actions > 0 and card in self.hand:
            self.actions -= 1
            self.hand.remove(card)
            self.played_cards.append(card)
            card.perform_action(self, game)

    def trash_card(self, card, game):
        assert card in self.hand
        self.hand.remove(card)
        game.trash_card(card, self)

    def discard_cards(self, cards, game):
        for card in cards:
            assert card in self.hand
            self.hand.remove(card)
            self.discard_pile.append(card)

    def buy_card(self, card, game):
        if self.buys > 0 and card in game.supply and game.supply[card]:
            card = game.supply[card].pop(0)
            self.coins -= card.cost
            self.buys -= 1
            self.discard_pile.append(card)

    def cleanup_phase(self):
        self.discard_pile.extend(self.hand)
        self.discard_pile.extend(self.played_cards)
        self.played_cards = []
        self.hand = []
        self.draw(5)

    def gain_card(self, card_name, game):
        """
        Gain a card from the supply and add it to the discard pile.
        """
        if card_name in game.supply and game.supply[card_name]:
            gained_card = game.supply[card_name].pop(0)  # Remove the card from the supply
            self.discard_pile.append(gained_card)  # Add the card to the discard pile
            print(f"{self.name} gains a {gained_card.name} and adds it to their discard pile.")
        else:
            print(f"{self.name} cannot gain {card_name} as it is not available in the supply.")

    def choose_action(self, action_cards, game):
        raise NotImplementedError

    def choose_buy(self, buyable_cards, game):
        raise NotImplementedError

    def choose_discard(self, cards, game, min_number, max_number):
        raise NotImplementedError
    
    def choose_trash(self, cards, game, min_number, max_number):
        raise NotImplementedError

    def choose_gain(self, gainable_cards, game):
        raise NotImplementedError

    def general_choice(self, options, game):
        return NotImplementedError

class Random_Player(Player):
    def choose_action(self, action_cards, game):
        self.print_hand()
        return random.choice(action_cards)

    def choose_buy(self, buyable_cards, game):
        return random.choice(buyable_cards)

    def choose_discard(self, cards, game, min_number, max_number):
        number_to_discard = random.randint(min_number, min(max_number, len(cards)))
        return random.sample(cards, number_to_discard)
    
    def choose_trash(self, cards, game, min_number, max_number):
        number_to_trash = random.randint(min_number, min(max_number, len(cards)))
        return random.sample(cards, number_to_trash)

    def choose_gain(self, gainable_cards, game):
        return random.choice(gainable_cards)

    def general_choice(self, options, game):
        return random.choice(options)

class Human_Player(Player):
    def choose_action(self, action_cards, game):
        self.print_hand()
        print("Action Cards in Hand:")
        for i, card in enumerate(action_cards):
            print(f"{i}: {card.name}")
        try:
            choice = int(input("Choose an action card to play (-1 for nothing): "))
            if choice == -1:
                return None
            if choice >= len(action_cards):
                raise ValueError('Invalid choice. Try again.')
        except ValueError as e:
            print(e)
            return self.choose_action(action_cards, game)
        return action_cards[choice]

    def choose_buy(self, buyable_cards, game):
        self.print_hand()
        print("Buyable Cards:")
        for i, card in enumerate(buyable_cards):
            print(f"{i}: {card}")
        try:
            choice = int(input("Choose a card to buy (-1 for nothing): "))
            if choice == -1:
                return None
            if choice >= len(buyable_cards):
                raise ValueError('Invalid choice. Try again.')
        except ValueError as e:
            print(e)
            return self.choose_buy(buyable_cards, game)
        return buyable_cards[choice]

    def choose_trash(self, cards, game, min_number, max_number):
        print("Trashable Cards:")
        for i, card in enumerate(cards):
            print(f"{i}: {card.name}")
        choices = []
        num_trashed = 0
        for j in range(max_number):
            try:
                choice = int(input("Choose a card to trash (-1 for stop): "))
                if choice == -1:
                    if num_trashed < min_number:
                        raise ValueError(f"Must trash at least {min_number} cards. Try again.")
                        self.choose_trash(cards, game, min_number, max_number)
                    break
                if choice >= len(cards):
                    raise ValueError('Invalid choice. Try again.')
            except ValueError as e:
                print(e)
                return self.choose_trash(cards, game, max_number)
            choices.append(cards[choice])
            num_trashed += 1
        return choices

    def choose_discard(self, cards, game, min_number, max_number):
        print("Discardable Cards:")
        for i, card in enumerate(cards):
            print(f"{i}: {card.name}")
        choices = []
        num_discarded = 0
        for _ in range(max_number):
            try:
                choice = int(input("Choose a card to discard (-1 for stop): "))
                if choice == -1:
                    if num_discarded < min_number:
                        raise ValueError(f"Must discard at least {min_number} cards. Try again.")
                        self.choose_discard(cards, game, min_number, max_number)
                    break
                if choice >= len(cards):
                    raise ValueError('Invalid choice. Try again.')
            except ValueError as e:
                print(e)
                return self.choose_discard(cards, game, max_number)
            choices.append(cards[choice])
            num_discarded += 1
        return choices

    def choose_gain(self, gainable_card_names, game):
        print("Gainable Cards:")
        for i, card in enumerate(gainable_card_names):
            print(f"{i}: {card}")
        try:
            choice = int(input("Choose a card to gain (-1 for nothing): "))
            if choice == -1:
                return None
            if choice >= len(gainable_card_names):
                raise ValueError('Invalid choice. Try again.')
        except ValueError as e:
            print(e)
            return self.choose_gain(gainable_card_names, game)
        return gainable_card_names[choice]

    def general_choice(self, options, game):
        print("Options:")
        for i, option in enumerate(options):
            if isinstance(option, str):
                print(f"{i}: {option}")
            else:
                print(f"{i}: {option.name}")
        try:
            choice = int(input("Choose an option: "))
            if choice >= len(options):
                raise ValueError('Invalid choice. Try again.')
        except ValueError as e:
            print(e)
            return self.general_choice(options, game)
        return options[choice]


class BigMoney_Player(Player):
    def choose_action(self, action_cards, game):
        return None

    def choose_buy(self, buyable_cards, game):
        if 'Silver' not in buyable_cards:
            return  None
        if 'Province' in buyable_cards:
            return 'Province'
        treasure_cards = [card for card in buyable_cards if isinstance(game.supply[card][0], TreasureCard)]
        return max(treasure_cards, key=lambda card: game.supply[card][0].value)

    def choose_discard(self, cards, game, max_number):
        # Curses > Victory cards > Treasure cards of ascending order > Smithy  
        to_discard = []
        
        # Discard Curses first.
        curses = [card for card in cards if isinstance(card, CurseCard)]
        to_discard.extend(curses)

        # Discard Victory cards next.
        victory_cards = [card for card in cards if isinstance(card, VictoryCard)]
        to_discard.extend(victory_cards)
        
        # Discard Treasures in ascending order.
        coppers = [card for card in cards if isinstance(card, TreasureCard) and card.value == 1]
        to_discard.extend(coppers)

        silvers = [card for card in cards if isinstance(card, TreasureCard) and card.value == 2]
        to_discard.extend(silvers)

        golds = [card for card in cards if isinstance(card, TreasureCard) and card.value == 3]
        to_discard.extend(golds)

        # Everything else.
        remaining_cards = [card for card in cards if card not in to_discard]
        to_discard.extend(remaining_cards)

        # Ensure we don't discard more than max_number of cards.
        return to_discard[:max_number]


class BigMoneySmithy_Player(BigMoney_Player):
    def __init__(self, name):
        super().__init__(name)
        self.bought_smithy = False


    def choose_action(self, action_cards, game):
        for card in action_cards:
            if card.name == 'Smithy':
                return card
        return None

    def choose_buy(self, buyable_cards, game):
        if 'Smithy' in buyable_cards and not self.bought_smithy:
            self.bought_smithy = True
            return 'Smithy'
        else:
            return super().choose_buy(buyable_cards, game)

class BigMoneyWitch_Player(BigMoney_Player):
    def __init__(self, name):
        super().__init__(name)
        self.bought_witch = False


    def choose_action(self, action_cards, game):
        for card in action_cards:
            if card.name == 'Witch':
                return card
        return None

    def choose_buy(self, buyable_cards, game):
        if 'Witch' in buyable_cards and not self.bought_witch:
            self.bought_witch = True
            return 'Witch'
        else:
            return super().choose_buy(buyable_cards, game)