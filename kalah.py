#!/usr/bin/env python3

"""The board game Kalah.

Author: Skorpio
License: MIT
"""

import random
from operator import itemgetter


__version__ = '0.1.1'

# Opposite houses. {0: 12, 1: 11, 2: 10, etc.}
OPPOSITES = dict(zip(range(0, 6), range(12, 6, -1)))
OPPOSITES.update({v: k for k, v in OPPOSITES.items()})


def move(board, house, player):
    """Move the seeds from selected house counter-clockwise.

    Args:
        board (list): The game board.
        house (int): Index of the selected house.
        player (int): 0 is Player 1; 1 is Player 2.
    """
    seeds = board[house]
    board[house] = 0

    # Move again if last seed ends up in store.
    move_again = house + seeds in (6, 13)

    i = house
    seeds_left = seeds
    while seeds_left > 0:
        i += 1
        idx = i % len(board)
        if player == 0 and idx == 13 or player == 1 and idx == 6:
            continue
        board[idx] += 1
        seeds_left -= 1

    if board[idx] == 1: # Last house was empty.
        board = capture_house(board, player, last_seed_pos=idx)

    return board, move_again


def capture_house(board, player_num, last_seed_pos):
    """If last seed ends in a empty house, take last + opponent seeds."""
    # May not capture in opponents house.
    if (player_num == 0 and last_seed_pos in range(7, 13)
            or player_num == 1 and last_seed_pos in range(0, 6)):
        return board

    board = board.copy()
    # May not capture if 0 seeds in opponents house.
    last_house_is_not_store = last_seed_pos not in (6, 13)
    if last_house_is_not_store:
        seeds_in_opp = board[OPPOSITES[last_seed_pos]] != 0
    else:
        seeds_in_opp = False

    if last_house_is_not_store and seeds_in_opp:
        board[last_seed_pos] = 0
        store = 6 if player_num == 0 else 13
        board[store] += 1 + board[OPPOSITES[last_seed_pos]]
        board[OPPOSITES[last_seed_pos]] = 0
    return board


def ai_move(board, position):
    """Find the best move for the ai player.

    Give weights to possible moves.
    Capturing opponents house has highest priority,
    then scoring with bonus turn,
    just scoring has lowest priority (except for
    random moves).

    Args:
        board (list): The game board.
        position (int): 0 if player 1; 1 if player2.
    """
    if position == 0:
        own_houses = range(0, 6)
        store = 6
        highest_house = 5
    else:
        own_houses = range(7, 13)
        store = 13
        highest_house = 12

    # Houses with seeds.
    possible_moves = [house for house in own_houses if board[house]]
    # Rate moves.
    weighted_moves = []
    for house in possible_moves:
        seeds = board[house]
        can_score = seeds + house > highest_house
        can_score_with_bonus = seeds + house == store
        target_house = (seeds + house) % len(board)
        target_house_empty = board[target_house] == 0
        target_not_store = target_house in own_houses
        if target_not_store:
            seeds_in_opp = OPPOSITES[target_house] != 0
        else:
            seeds_in_opp = False
        can_capture = target_house_empty and target_not_store and seeds_in_opp
        if can_capture:
            weighted_moves.append([house, 4])
        elif can_score_with_bonus:
            weighted_moves.append([house, 3])
        elif can_score:
            weighted_moves.append([house, 2])

    if weighted_moves:
        return sorted(weighted_moves, key=itemgetter(1), reverse=True)[0][0]
    else:
        return random.choice(possible_moves)


def print_board(board):
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
    while True:
        print('Enter number of human players (0, 1, 2)')
        human_players = input('>>> ')
        if human_players in ('0', '1', '2'):
            return int(human_players)
        else:
            print('Invalid input.')


def get_seeds():
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
            inp = ai_move(board, position=current_player)
            print('AI move:', inp)

        if inp in ('quit', 'q'):
            break
        try:
            inp = int(inp)
        except ValueError:
            print('Invalid input.')
            continue
        if (current_player == 0 and inp not in range(0, 6)
                or current_player == 1 and inp not in range(7, 13)
                or board[inp] == 0):
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
