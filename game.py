import random
import numpy as np
from collections import defaultdict, Counter

# Base Card Classes
class Card:
    def __init__(self, name, cost):
        self.name = name
        self.cost = cost

class TreasureCard(Card):
    def __init__(self, name, cost, value):
        super().__init__(name, cost)
        self.value = value

class VictoryCard(Card):
    def __init__(self, name, cost, points):
        super().__init__(name, cost)
        self.points = points

class CurseCard(Card):
    def __init__(self, name, cost, points):
        super().__init__(name, cost)
        self.points = points

class KingdomCard(Card):
    def __init__(self, name, cost, action=None, reaction=None):
        super().__init__(name, cost)
        self.action = action
        self.reaction = reaction

    def perform_action(self, player, game):
        if self.action:
            self.action(player, game)

    def perform_reaction(self, player, game):
        if self.reaction:
            self.reaction(player, game)



# Game Class
class Game:
    def __init__(self, players, kingdom_cards = []):
        self.players = players
        self.supply = {}
        self.trash = []  # Trash pile for trashed cards
        self.current_player_index = 0
        self.game_over = False
        self.turn_number = 1
        self.kingdom_cards = kingdom_cards

    def setup(self):
        # Set up the supply piles
        self.supply = {
            "Copper": [TreasureCard("Copper", 0, 1) for _ in range(60)],
            "Silver": [TreasureCard("Silver", 3, 2) for _ in range(40)],
            "Gold": [TreasureCard("Gold", 6, 3) for _ in range(30)],
            "Estate": [VictoryCard("Estate", 2, 1) for _ in range(8+6)],
            "Duchy": [VictoryCard("Duchy", 5, 3) for _ in range(8)],
            "Province": [VictoryCard("Province", 8, 6) for _ in range(8)],
            "Curse": [CurseCard("Curse", 0, -1) for _ in range(10)]
        }

        possible_kingdom_cards = {
            "Cellar": KingdomCard("Cellar", 2, cellar_action),
            "Chapel": KingdomCard("Chapel", 2, chapel_action),
            "Moat": KingdomCard("Moat", 2, moat_action),
            "Village": KingdomCard("Village", 3, village_action),
            "Workshop": KingdomCard("Workshop", 3, workshop_action),
            "Militia": KingdomCard("Militia", 4, militia_action),
            "Remodel": KingdomCard("Remodel", 4, remodel_action),
            "Smithy": KingdomCard("Smithy", 4, smithy_action),
            "Market": KingdomCard("Market", 5, market_action),
            "Mine": KingdomCard("Mine", 5, mine_action),
            "Merchant": KingdomCard("Merchant", 3, merchant_action),
            "Gardens": VictoryCard("Gardens", 4, 0),  # Points calculated later
            "Bureaucrat": KingdomCard("Bureaucrat", 4, bureaucrat_action),
            "Feast": KingdomCard("Feast", 4, feast_action),
            "Council Room": KingdomCard("Council Room", 5, council_room_action),
            "Laboratory": KingdomCard("Laboratory", 5, laboratory_action),
            "Festival": KingdomCard("Festival", 5, festival_action),
            "Library": KingdomCard("Library", 5, library_action),
            "Sentry": KingdomCard("Sentry", 5, sentry_action),
            "Throne Room": KingdomCard("Throne Room", 4, throne_room_action),
            "Witch": KingdomCard("Witch", 5, witch_action),
            "Spy": KingdomCard("Spy", 4, spy_action),
            "Thief": KingdomCard("Thief", 4, thief_action),
            "Adventurer": KingdomCard("Adventurer", 6, adventurer_action)
        }
        #add fixed kingdom cards
        selected_kingdom_cards = []
        for card_name in self.kingdom_cards:
            selected_kingdom_cards.append((card_name, possible_kingdom_cards[card_name]))

        # Randomly pick 10 kingdom cards
        random_kingdom_cards = random.sample(sorted(possible_kingdom_cards.items()), 10-len(self.kingdom_cards))

        # Add all to the supply
        selected_kingdom_cards.extend(random_kingdom_cards)
        selected_kingdom_cards.sort(key=lambda x: x[1].cost)
        print(f'Kingdom cards:')
        print([card_name for card_name, card in selected_kingdom_cards])

        for card_name, card in selected_kingdom_cards:
            if isinstance(card, VictoryCard):
                self.supply[card_name] = [card for _ in range(8)]
            else:
                self.supply[card_name] = [card for _ in range(10)]

        # Initialize each player's deck
        for player in self.players:
            player.deck.extend([self.supply["Copper"].pop() for _ in range(7)])
            player.deck.extend([self.supply["Estate"].pop() for _ in range(3)])
            random.shuffle(player.deck)
            player.draw(5)

    def trash_card(self, card, player):
        """Move a card from a player's hand to the trash pile."""
        self.trash.append(card)
        print(f"{player.name} trashes {card.name}.")

    def check_for_moat(self, player):
        has_moat = any(card.name == "Moat" for card in player.hand)
        if has_moat:
            print(f"{player.name} has Moat and may reveal it.")
            return True
        return False

    def play_game(self):
        self.setup()
        while not self.game_over:
            player = self.players[self.current_player_index]
            player.actions = 1
            player.buys = 1
            player.coins = 0

            # Print current state
            print(f"Turn {self.turn_number}: {player.name}'s turn")


            # Action Phase
            action_cards = [card for card in player.hand if isinstance(card, KingdomCard) and card.action]
            # placeholder for action
            card_to_play = True
            while player.actions > 0 and action_cards and card_to_play:
                card_to_play = player.choose_action(action_cards, self)
                if not card_to_play:
                    print(f"{player.name} chooses not to play an action card.")
                else:
                    print(f"{player.name} plays {card_to_play.name}.")
                player.play_action(card_to_play, self)
                action_cards = [card for card in player.hand if isinstance(card, KingdomCard) and card.action]

            # Buy Phase
            treasures = [card for card in player.hand if isinstance(card, TreasureCard)]
            player.coins += sum(treasure.value for treasure in treasures)
            available_buys = [card_name for card_name, pile in self.supply.items() if pile and pile[0].cost <= player.coins]
            # placeholder for buy 
            card_to_buy = True
            while player.buys > 0 and available_buys and card_to_buy:
                print(f"{player.name}'s buys: {player.buys}, coins: {player.coins}")
                card_to_buy = player.choose_buy(available_buys, self)
                player.buy_card(card_to_buy, self)
                print(f"{player.name} buys {card_to_buy}.")
                available_buys = [card_name for card_name, pile in self.supply.items() if pile and pile[0].cost <= player.coins]

            # Clean-up Phase
            player.cleanup_phase()
            self.turn_number += 0.5

            if self.turn_number >= 1000:
                self.game_over = True
                print("Game over! The game lasted too long.")
                return self.determine_winner()

            # Check for end game conditions
            if len(self.supply["Province"]) == 0 or sum(1 for pile in self.supply.values() if not pile) >= 3:
                self.game_over = True
                print("Game over!")
                return self.determine_winner()

            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def determine_winner(self):
        scores = {player.name: 0 for player in self.players}
        for player in self.players:
            all_player_cards = player.deck + player.hand + player.discard_pile
            if "Gardens" in [card.name for card in all_player_cards]:
                garden_points = len(all_player_cards) // 10
            for card in player.deck + player.hand + player.discard_pile:
                if isinstance(card, VictoryCard) or isinstance(card, CurseCard):
                    scores[player.name] += card.points
                    if card.name == "Gardens":
                        scores[player.name] += garden_points
                elif card.name == "Gardens":
                    total_cards = len(player.deck + player.hand + player.discard_pile)
                    scores[player.name] += total_cards // 10
        print(f"Scores: {scores}")
        print(f'The game lasted {self.turn_number} turns.')
        # check for tie
        if len(set(scores.values())) == 1:
            print("It's a tie!")
            return 'Draw'

        else:
            winner = max(scores, key=scores.get)
            print(f"The winner is {winner}!")

            print(f'Final decks:')
            for player in self.players:
                print(f'-' * 50)
                print(f'{player.name}')
                all_cards = player.deck + player.hand + player.discard_pile
                counts = Counter([card.name for card in all_cards])
                print(counts)
                print(f'-' * 50)


            return winner


# Action Functions
def moat_action(player, game):
    player.draw(2)


def militia_action(player, game):
    player.coins += 2
    for opponent in game.players:
        if opponent != player:
            if game.check_for_moat(opponent):
                continue

            if len(opponent.hand) > 3:
                cards_to_discard = opponent.choose_discard(opponent.hand, game, min_number=len(opponent.hand)-3, max_number=len(opponent.hand)-3)
                opponent.discard_cards(cards_to_discard, game)
                print(f"{opponent.name} discards {len(cards_to_discard)} cards due to Militia.")

def cellar_action(player, game):
    player.actions += 1
    cards_to_discard = player.choose_discard(player.hand, game, min_number = 0, max_number=len(player.hand))
    player.discard_cards(cards_to_discard, game)
    player.draw(len(cards_to_discard))

def chapel_action(player, game):
    cards_to_trash = player.choose_trash(player.hand, game, min_number = 0, max_number=4)
    for card in cards_to_trash:
        player.trash_card(card, game)

def village_action(player, game):
    player.actions += 2
    player.draw(1)

def workshop_action(player, game):
    gainable_cards = [card for card in game.supply if game.supply[card] and game.supply[card][0].cost <= 4]
    card_to_gain = player.choose_gain(gainable_cards, game)
    if card_to_gain:
        player.gain_card(card_to_gain, game)

def remodel_action(player, game):
    if not player.hand:
        return
    cards_to_trash = player.choose_trash(player.hand, game, min_number = 1, max_number=1)
    if cards_to_trash:
        trashed_card = cards_to_trash[0]
        player.trash_card(trashed_card, game)
        gainable_cards = [card for card in game.supply if game.supply[card] and game.supply[card][0].cost <= trashed_card.cost + 2]
        if gainable_cards:
            card_to_gain = player.choose_gain(gainable_cards, game)
            player.gain_card(card_to_gain, game)

def smithy_action(player, game):
    player.draw(3)

def market_action(player, game):
    player.actions += 1
    player.buys += 1
    player.coins += 1
    player.draw(1)

def mine_action(player, game):
    treasures_in_hand = [card for card in player.hand if isinstance(card, TreasureCard)]
    if treasures_in_hand:
        cards_to_trash = player.choose_trash(treasures_in_hand, game, min_number = 0, max_number=1)
        if cards_to_trash:
            trashed_card = cards_to_trash[0]
            gainable_cards = [card for card in game.supply if game.supply[card] and isinstance(game.supply[card][0], TreasureCard) and game.supply[card][0].cost <= trashed_card.cost + 3]
            card_to_gain = player.choose_gain(gainable_cards, game)
            print(f"{player.name} trashes {trashed_card.name}.")
            player.trash_card(trashed_card, game)
            if card_to_gain:
                player.gain_card(card_to_gain, game)

def merchant_action(player, game):
    player.draw(1)
    player.actions += 1
    # Check if a Silver card was played and give +1 coin
    if "Silver" in [card.name for card in player.hand]:
        player.coins += 1

def bureaucrat_action(player, game):
    # Gain a silver card onto deck
    if "Silver" in game.supply and game.supply["Silver"]:
        player.deck.insert(0, game.supply["Silver"].pop(0))
        print(f"{player.name} gains a Silver card onto their deck.")
    # Each other player reveals a Victory card and places it on their deck
    for opponent in game.players:
        if opponent != player:
            victory_cards = [card for card in opponent.hand if isinstance(card, VictoryCard)]
            if victory_cards:
                card_to_reveal = opponent.general_choice(victory_cards, game)
                print(f"{opponent.name} reveals {card_to_reveal.name}.")
                opponent.hand.remove(card_to_reveal)
                opponent.deck.insert(0, card_to_reveal)

def feast_action(player, game):
    # Trash this card
    try:
        feast_card = [card for card in player.played_cards if card.name == "Feast"][0]
        game.trash_card(feast_card, player)
        player.played_cards.remove(feast_card)
    except:
        print("Feast card not found in played cards. CHECK THIS SHOULD ONLY HAPPEN AFTER THRONE ROOM")
    # Gain a card costing up to 5
    gainable_cards = [card for card in game.supply if game.supply[card] and game.supply[card][0].cost <= 5]
    card_to_gain = player.choose_gain(gainable_cards, game)
    if card_to_gain:
        player.gain_card(card_to_gain, game)

def council_room_action(player, game):
    player.draw(4)
    player.buys += 1
    for opponent in game.players:
        if opponent != player:
            opponent.draw(1)

def laboratory_action(player, game):
    player.draw(2)
    player.actions += 1

def festival_action(player, game):
    player.actions += 2
    player.buys += 1
    player.coins += 2

def library_action(player, game):
    temp_zone = []
    while len(player.hand) < 7 and (player.deck or player.discard_pile):
        player.draw(1)
        if isinstance(player.hand[-1], KingdomCard) and player.hand[-1].action:
            keep_action_card = player.general_choice(["keep", "set aside"], game)
            if keep_action_card == "set aside":
                temp_zone.append(player.hand.pop())
    player.discard_pile.extend(temp_zone)

def sentry_action(player, game):
    player.draw(1)
    player.actions += 1
    if len(player.deck) < 2:
        player.refresh_deck()
    top_cards = player.deck[:2]
    player.deck = player.deck[2:]
    first_name = top_cards[0].name if top_cards else "Nothing"
    second_name = top_cards[1].name if len(top_cards) > 1 else "Nothing"
    print(f"{player.name} reveals {first_name} and {second_name}.")
    for card in top_cards:
        decision = player.general_choice(["keep", "discard", "trash"], game)
        if decision == "trash":
            game.trash_card(card, player)
        elif decision == "discard":
            player.discard_pile.append(card)
        else:
            player.deck.insert(0, card)

def throne_room_action(player, game):
    action_cards = [card for card in player.hand if isinstance(card, KingdomCard) and card.action]
    if action_cards:
        card_to_play_twice = player.choose_action(action_cards, game)
        player.actions += 1
        player.play_action(card_to_play_twice, game)  
        card_to_play_twice.perform_action(player, game)      

def witch_action(player, game):
    player.draw(2)
    for opponent in game.players:
        if game.check_for_moat(opponent):
            continue

        if opponent != player and game.supply["Curse"]:
            opponent.discard_pile.append(game.supply["Curse"].pop(0))

def spy_action(player, game):
    player.draw(1)
    player.actions += 1
    for p in game.players:
        if p != player:
            if game.check_for_moat(p):
                continue

        if not p.deck:
            p.refresh_deck()

        try:
            top_card = p.deck.pop(0)
            print(f"{p.name} reveals {top_card.name}.")
            if player.general_choice(["discard", "keep"], game) == "discard":
                p.discard_pile.append(top_card)
            else:
                p.deck.insert(0, top_card)
        except:
            print(f"{p.name} has no cards left in their deck or discard")
            assert not p.deck and not p.discard_pile

def thief_action(player, game):
    for opponent in game.players:
        if opponent != player:
            if game.check_for_moat(opponent):
                continue

            #refresh deck if smaller than 2
            if len(opponent.deck) < 2:
                opponent.refresh_deck()

            
            try:
                top_two_cards = [opponent.deck.pop(0) for _ in range(2)]
                print(f"{opponent.name} reveals {top_two_cards[0].name} and {top_two_cards[1].name}.")
                treasures = [card for card in top_two_cards if isinstance(card, TreasureCard)]
                if treasures:
                    treasure_to_trash = player.general_choice([t for t in treasures], game)
                    game.trash_card(treasure_to_trash, opponent)
                    if player.general_choice(["pass", "gain"], game) == "gain":
                        player.gain_card(treasure_to_trash.name, game)
                else:
                    treasure_to_trash = None
                opponent.discard_pile.extend([card for card in top_two_cards if not treasure_to_trash or card.name != treasure_to_trash.name])
            except:
                print(f"{opponent.name} has no cards left in their deck or discard")
                assert not opponent.deck and not opponent.discard_pile

def adventurer_action(player, game):
    revealed_cards = []
    while len([card for card in revealed_cards if isinstance(card, TreasureCard)]) < 2:
        if not player.deck:
            player.refresh_deck()
        try:
            revealed_cards.append(player.deck.pop(0))
        except:
            print(f"{player.name} has no cards left in their deck or discard")
            assert not player.deck and not player.discard_pile
            break
    treasure_cards = [card for card in revealed_cards if isinstance(card, TreasureCard)]
    player.hand.extend(treasure_cards)
    player.discard_pile.extend([card for card in revealed_cards if card not in treasure_cards])
