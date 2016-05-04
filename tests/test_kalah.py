import pytest

from ..kalah import determine_winner, find_target_house


board1 = [0] * 14
board1[6] = 5
board1[13] = 9
board2 = [0] * 14
board2[13] = 5
board2[6] = 9
board3 = [0] * 14
board3[13] = 5
board3[6] = 5

@pytest.mark.parametrize('results', ((board1, 'Player 2 is the winner.'),
                                     (board2, 'Player 1 is the winner.'),
                                     (board3, 'The game ended in a tie.')))
def test_determine_winner(results):
    assert determine_winner(results[0]) == results[1]


def test_find_target_house():
    """house, seeds, player."""
    data = [
        ((7, 6), 13),
        ((7, 13), 7),
        ((7, 12), 5),
        ((7, 26), 7),
        ((7, 39), 7),
        ((0, 13), 0),
        ((0, 26), 0),
        ((0, 0), 0),
        ((0, 1), 1),
        ((5, 9), 1),
        ((0, 13), 0),
        ((4, 9), 0),
        ]
    for args, result in data:
        assert find_target_house(*args) == result
