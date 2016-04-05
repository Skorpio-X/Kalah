#!/usr/bin/env python3

"""The board game Kalah.

Author: Skorpio
License: MIT
"""

import random
from operator import itemgetter


__version__ = '0.1.0'

# Opposite houses. {0: 12, 1: 11, 2: 10, etc.}
opposites = {i: j for i, j in zip(range(0, 6), range(12, 6, -1))}
opposites.update({v: k for k, v in opposites.items()})


def move(board, house, player):
    seeds = board[house]
    board[house] = 0

    # Move again if last seed ends up in store.
    if house + seeds in (6, 13):
        move_again = True
    else:
        move_again = False

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
    board = board.copy()
    # May not capture in opponents house.
    if (player_num == 0 and last_seed_pos in range(7, 13) or
        player_num == 1 and last_seed_pos in range(0, 6)):
        return board
    # May not capture if 0 seeds in opponents house.
    if last_seed_pos not in (6, 13):
        seeds_in_opp = board[opposites[last_seed_pos]] != 0
    else:
        seeds_in_opp = False

    last_house_not_store = last_seed_pos not in (6, 13)
    if last_house_not_store and seeds_in_opp:
        board[last_seed_pos] = 0
        store = 6 if player_num == 0 else 13
        board[store] += 1 + board[opposites[last_seed_pos]]
        board[opposites[last_seed_pos]] = 0
    return board


def ai_move(board, position=1):
    """AI move.

    Args:
        position (int): 0 if player 1; 1 if player2.
    """
    # Houses with seeds.
    possible_moves = [house for house in range(7, 13) if board[house]]
    # Rate moves.
    ratings = []
    for house in possible_moves:
        seeds = board[house]
        can_score = seeds + house > 12
        can_score_with_bonus = seeds + house == 13
        target_house = (seeds + house) % len(board)
        target_house_empty = board[target_house] == 0
        target_not_store = target_house in range(7, 13)
        if target_not_store:
            seeds_in_opp = opposites[target_house] != 0
        else:
            seeds_in_opp = False
        can_capture = target_house_empty and target_not_store and seeds_in_opp
        if can_capture:
            ratings.append([house, 4])
        elif can_score_with_bonus:
            ratings.append([house, 3])
        elif can_score:
            ratings.append([house, 2])

#     if position == 1:  # player2
#         filled_houses = [house for house in range(7, 13) if board[house]]
#         # Find empty houses and check if AI can end their turn in one.
#         empty_houses = [house for house in range(7, 13) if board[house] == 0]
#         capture_moves = []
#         for house in empty_houses:
#             for idx, seeds in enumerate(board[7:13], 7):
#                 if idx + seeds == house and seeds > 0:
#                     capture_moves.append(idx)
#     else:  # player1
#         filled_houses = [house for house in range(0, 6) if board[house]]
#         empty_houses = [house for house in range(0, 6) if board[house] == 0]
    if ratings:
        print(sorted(ratings, key=itemgetter(1), reverse=True))
        return sorted(ratings, key=itemgetter(1), reverse=True)[0][0]
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


def main():
    player = 0
#     board = [6, 6, 6, 6, 6, 6, 0, 6, 6, 6, 6, 6, 6, 0]
    board = [3, 3, 3, 3, 3, 3, 0, 3, 3, 3, 3, 3, 3, 0]
    print('Welcome to Kalah.\n'.rjust(30))
    print('Enter the number of the house to')
    print('move the seeds counter-clockwise.')
    print('Enter quit or q to stop the game.\n')
    print_board(board)
    while True:
        print('Player {}'.format(player + 1).rjust(20, ' '))
        if player == 0:
            inp = input('>>> ')
        else:
            inp = ai_move(board)
            print('AI:', inp)
        if inp in ('quit', 'q'):
            break
        try:
            inp = int(inp)
        except ValueError:
            print('Invalid input.')
            continue
        if (player == 0 and inp not in range(0, 6) or
            player == 1 and inp not in range(7, 13) or board[inp] == 0):
            print('Invalid input.')
            continue

        board, move_again = move(board, inp, player)
        print_board(board)

        # Game over.
        if not any(board[0:6]) or not any(board[7:13]):
            # Add remaining seeds to store.
            if not any(board[0:6]):
                board[13] += sum(board[7:13])
                board[7:13] = [0] * 6
            else:
                board[6] += sum(board[0:6])
                board[0:6] = [0] * 6

            print_board(board)
            # Determine winner.
            pl1, pl2 = board[6], board[13]
            print(' ' * 8, end='')
            if pl1 > pl2:
                input('Player 1 is the winner.')
            elif pl2 > pl1:
                input('Player 2 is the winner.')
            else:
                input('The game ended in a tie.')
            break

        player = (player + 1) % 2 if not move_again else player


if __name__ == "__main__":
    main()
