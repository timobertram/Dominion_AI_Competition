from game import Game
from players import BigMoney_Player, BigMoneySmithy_Player, Random_Player, Human_Player
import numpy as np
from collections import defaultdict

def simulate_game(player_1, player_2, num_games=100, kingdom_cards=[]):
    scores = defaultdict(int)
    # Run the Game
    for _ in range(num_games):
        players = [player_1, player_2]
        np.random.shuffle(players)
        game = Game(players, kingdom_cards=kingdom_cards)
        winner = game.play_game()
        scores[winner] += 1
        player_1.reset()
        player_2.reset()

    print('-'*50)
    print("Final Scores:")
    print(scores)

if __name__ == "__main__":
    kingdom_cards = []
    # Human_Player for command line interface
    simulate_game(Random_Player("P_1"), Random_Player("P_2"), num_games=10_000, kingdom_cards=kingdom_cards)