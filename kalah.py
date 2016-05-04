#!/usr/bin/env python3

"""The board game Kalah.

Author: Skorpio
License: MIT
"""

import random
from operator import itemgetter


__version__ = '0.1.3'

# Opposite houses. {0: 12, 1: 11, 2: 10, etc.}
OPPOSITES = dict(zip(range(0, 6), range(12, 6, -1)))
OPPOSITES.update({v: k for k, v in OPPOSITES.items()})
# Player: Houses, store.
PLAYER_DATA = {
    0: (range(0, 6), 6),
    1: (range(7, 13), 13)
    }


def move(board, house, player):
    """Move the seeds from selected house counter-clockwise.

    Args:
        board (list): The game board.
        house (int): Index of the selected house.
        player (int): 0 is Player 1; 1 is Player 2.
    """
    seeds = board[house]
    board[house] = 0
    store = PLAYER_DATA[player][1]
    opp_store = 13 if player == 0 else 6

    # Move again if last seed ends up in store.
    move_again = find_target_house(house, seeds) == store

    while seeds > 0:
        house = (house + 1) % len(board)
        if house == opp_store:
            continue
        board[house] += 1
        seeds -= 1

    if board[house] == 1:  # Last house was empty.
        if can_capture_house(board, player, last_seed_pos=house):
            board = capture_house(board, player, last_seed_pos=house)

    return board, move_again


def can_capture_house(board, player, last_seed_pos):
    """Determine if capturing a house is possible.

    May not capture in opponents house or store.
    Can capture if seeds are in opponents house.

    Args:
        board (list): The game board.
        player (int): 0 or 1
        last_seed_pos (int): Index of the last placed seed.
            Works only if the house was empty.
    """
    opp_houses = range(7, 13) if player == 0 else range(0, 6)
    if last_seed_pos in opp_houses or last_seed_pos in (6, 13):
        return False
    return board[OPPOSITES[last_seed_pos]] != 0


def capture_house(board, player, last_seed_pos):
    """Move last seed and opposite seeds to own store."""
    board = board.copy()
    board[last_seed_pos] = 0
    store = 6 if player == 0 else 13
    board[store] += 1 + board[OPPOSITES[last_seed_pos]]
    board[OPPOSITES[last_seed_pos]] = 0
    return board


def find_target_house(house, seeds):
    """Find the target house of a choosen house."""
    player = 0 if house in range(0, 6) else 1
    opp_store = 6 if player == 1 else 13
    for _ in range(0, seeds):
        if house + 1 == opp_store:
            house = (house+2) % 14
        else:
            house = (house+1) % 14
    return house


def weigh_moves(board, own_houses, store, possible_moves):
    """Give weights to possible moves.

    Capturing opponents house has highest priority (4),
    then scoring with bonus turn (3),
    just scoring has lowest priority (2) (except for
    random moves).

    Args:
        board (list): Game board.
        own_houses (range): Houses of the player.
        store (int): The store of the player.
        possible_moves (list): Houses with seeds.

    Return:
        weighted_moves (list[tuple]): Houses with their weight.
    """
    weighted_moves = []
    for house in possible_moves:
        seeds = board[house]
        can_score = seeds + house > store
        can_score_with_bonus = seeds + house == store
        target_house = find_target_house(house, seeds)
        target_house_empty = board[target_house] == 0
        if target_house in own_houses:
            seeds_in_opp = board[OPPOSITES[target_house]] != 0
        else:
            seeds_in_opp = False

        can_capture = (target_house_empty and target_house in own_houses
                       and seeds_in_opp)
        if can_capture:
            weighted_moves.append([house, 4])
        elif can_score_with_bonus:
            weighted_moves.append([house, 3])
        elif can_score:
            weighted_moves.append([house, 2])
    return weighted_moves


def ai_move(board, player):
    """Find the best move for the ai player.

    Args:
        board (list): The game board.
        player (int): 0 if player 1; 1 if player2.
    """
    own_houses, store = PLAYER_DATA[player]

    # Houses with seeds.
    possible_moves = [house for house in own_houses if board[house]]
    weighted_moves = weigh_moves(board, own_houses, store, possible_moves)

    if weighted_moves:
        print(sorted(weighted_moves, key=itemgetter(1), reverse=True))
        return sorted(weighted_moves, key=itemgetter(1), reverse=True)[0][0]
    else:
        return random.choice(possible_moves)


def print_board(board):
    """Print the board."""
    print('_' * 40)
    print("  '12''11''10''9' '8' '7'  House numbers")
    print("{:>4}{:>4}{:>4}{:>4}{:>4}{:>4}".format(*reversed(board[7:13])))
    print()
    print("{}{}{}   Stores".format(board[13], ' '*26, board[6]))
    print()
    print("{:>4}{:>4}{:>4}{:>4}{:>4}{:>4}".format(*board[0:6]))
    print("  '0' '1' '2' '3' '4' '5'  House numbers")
    print('_' * 40)


def get_human_players():
    """Player can enter if 0, 1 or 2 human players take part."""
    while True:
        print('Enter number of human players (0, 1, 2)')
        human_players = input('>>> ')
        if human_players in ('0', '1', '2'):
            return int(human_players)
        else:
            print('Invalid input.')


def get_seeds():
    """Player needs to enter seeds per house."""
    print('Enter number of seeds per house (3-6)')
    while True:
        try:
            seed_number = int(input('>>> '))
        except ValueError:
            print('Invalid input. Enter a number between 3 and 6.')
            continue
        if seed_number in range(3, 7):
            return seed_number
        else:
            print('Invalid input. Enter a number between 3 and 6.')


def setup():
    """Get players, seeds and create board."""
    print('Welcome to Kalah.\n'.rjust(30))
    print('Enter the number of the house to move the seeds counter-clockwise.')
    print('Enter quit or q to stop the game.\n')
    human_players = get_human_players()
    if human_players == 1:
        player1 = random.choice(('human', 'ai'))
        if player1 == 'human':
            player2 = 'ai'
        else:
            player2 = 'human'
    elif human_players == 0:
        player1 = 'ai'
        player2 = 'ai'
    else:
        player1 = 'human'
        player2 = 'human'

    seed_number = get_seeds()

    board = [seed_number] * 14
    board[6] = 0
    board[13] = 0
    print_board(board)
    return player1, player2, board


def determine_winner(board):
    """Return the winner announcement."""
    pl1, pl2 = board[6], board[13]
    if pl1 > pl2:
        return 'Player 1 is the winner.'
    elif pl2 > pl1:
        return 'Player 2 is the winner.'
    else:
        return 'The game ended in a tie.'


def game_over(board):
    """Return True if all houses on one side are empty."""
    return not any(board[0:6]) or not any(board[7:13])


def main():
    """Setup, run main loop and determine winner."""
    player1, player2, board = setup()
    current_player = 0
    while True:
        print('Player {}'.format(current_player + 1))

        active_player = player1 if current_player == 0 else player2
        if active_player == 'human':
            inp = input('>>> ')
        else:
            inp = ai_move(board, current_player)
            print('AI move:', inp)

        if inp in ('quit', 'q'):
            return
        try:
            inp = int(inp)
        except ValueError:
            print('Invalid input.')
            continue
        own_houses = PLAYER_DATA[current_player][0]
        if inp not in own_houses or board[inp] == 0:
            print('Invalid move.')
            continue

        board, move_again = move(board, inp, current_player)
        print_board(board)

        if game_over(board):
            # Add remaining seeds to store.
            if not any(board[0:6]):
                board[13] += sum(board[7:13])
                board[7:13] = [0] * 6
            else:
                board[6] += sum(board[0:6])
                board[0:6] = [0] * 6

            print_board(board)
            break

        if not move_again:
            current_player = (current_player + 1) % 2

    input('{:^40}'.format(determine_winner(board)))


if __name__ == "__main__":
    main()
