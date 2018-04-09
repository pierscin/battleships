from random import choice
from typing import Tuple

import pytest

from app.api.models import Board, Player, Game


@pytest.fixture
def player1(board_factory):
    return Player(name='p1', board=board_factory())


@pytest.fixture
def player2(board_factory):
    return Player(name='p2', board=board_factory())


def ships_locations(board: Board) -> Tuple[Tuple[int, ...], ...]:
    return tuple(tuple(reversed(divmod(xy, board.N))) for xy, s in enumerate(board.starting_grid) if s != '.')


def test_starting_grid_validation():
    valid_grids = {
          'CCCCC.....'
        + 'BBBB......'
        + 'RRR.......'
        + 'SSS.......'
        + 'DD........'
        + '..........'
        + '..........'
        + '..........'
        + '..........'
        + '..........',

          '.....CCCCC'
        + '..........'
        + '..........'
        + '..........'
        + '..........'
        + '..........'
        + '..........'
        + '..........'
        + '....DD....'
        + 'SSSRRRBBBB',

          'C.........'
        + 'CBBBB.....'
        + 'CRRR......'
        + 'CSSS......'
        + 'CDD.......'
        + '..........'
        + '..........'
        + '..........'
        + '..........'
        + '..........',

          'C.........'
        + 'C.BBBB....'
        + 'C.........'
        + 'C.........'
        + 'C.........'
        + '.........R'
        + '.........R'
        + '.........R'
        + '......SSSD'
        + '.........D',
    }

    for grid in valid_grids:
        Board.validate_starting_grid(grid)

    invalid_grids = {
        # break in Carrier
          'CCCC.C....'
        + 'BBBB......'
        + 'RRR.......'
        + 'SSS.......'
        + 'DD........'
        + '..........'
        + '..........'
        + '..........'
        + '..........'
        + '..........',

        # Cruiser of size 2
          '.....CCCCC'
        + '..........'
        + '..........'
        + '..........'
        + '..........'
        + '..........'
        + '..........'
        + '..........'
        + '....DD....'
        + 'SSSRR.BBBB',

        # length == 99
          'C.........'
        + 'CBBBB.....'
        + 'CRRR......'
        + 'CSSS......'
        + 'CDD.......'
        + '..........'
        + '..........'
        + '..........'
        + '..........'
        + '.........',

        # misplaced Carrier
          'C.........'
        + '.CBBBB....'
        + 'CRRR......'
        + 'CSSS......'
        + 'CDD.......'
        + '..........'
        + '..........'
        + '..........'
        + '..........'
        + '..........'
    }

    for grid in invalid_grids:
        with pytest.raises(ValueError, message="This starting grid is invalid"):
            Board(grid)


def test_sinking_carrier(board_factory):
    grid =   'CCCCC.....' \
           + 'BBBB......' \
           + 'RRR.......' \
           + 'SSS.......' \
           + 'DD........' \
           + '..........' \
           + '..........' \
           + '..........' \
           + '..........' \
           + '..........'

    b = board_factory(grid)

    carrier_hits = ((0, 0), (1, 0), (2, 0), (3, 0))
    for hit in carrier_hits:
        assert b.shoot(*hit) == 'Hit Carrier'

    assert b.shoot(4, 0) == 'Sunk Carrier'
    assert b.sunk_ships() == {'C'}


def test_miss(board_factory):
    assert board_factory().shoot(9, 9) == 'Miss'


def test_illegal_double_action(board_factory):
    board = board_factory()
    x, y = choice(ships_locations(board))

    assert 'Hit' in board.shoot(x, y)

    with pytest.raises(ValueError):
        board.shoot(x, y)


def test_sinking_everything(board_factory):
    board = board_factory()

    for x, y in ships_locations(board):
        board.shoot(x, y)

    assert board.no_ships()


def test_join_more_than_two_players_is_illegal(player1, player2, board_factory, session):
    g = Game()

    g.join(player1)
    g.save_to_db()

    with pytest.raises(ValueError, message="First player can't join the same game twice"):
        g.join(player1)

    g.join(player2)

    with pytest.raises(ValueError, message="Game can only have 2 players"):
        g.join(Player(name="Third player", board=board_factory()))


def test_second_join_raises_exception_when_no_id_for_first_player(player1, player2, session):
    g = Game()

    g.join(player1)

    with pytest.raises(ValueError, message="First player should have no id from database (no commit before)"):
        g.join(player2)

    g.save_to_db()

    g.join(player2)


def test_illegal_move_raises_exception(player1, player2, session):
    g = Game()

    with pytest.raises(ValueError, message="Illegal move - no players in game"):
        g.shoot("", 0, 0)

    g.join(player1)

    g.save_to_db()

    with pytest.raises(ValueError, message="Illegal move - second player has not joined this game"):
        g.shoot(player1.name, 0, 0)

    g.join(player2)

    g.save_to_db()

    g.shoot(player1.name, 0, 0)

    with pytest.raises(ValueError, message="Illegal move - first player moved out of his turn"):
        g.shoot(player1.name, 0, 1)

    g.shoot(player2.name, 0, 0)

    with pytest.raises(ValueError, message="Illegal move - action was already taken on that field"):
        g.shoot(player1.name, 0, 0)


def test_game_flow(player1, player2, session):
    g = Game()

    g.save_to_db()

    assert g.state == g.State.NEW
    assert g.current is None
    assert g.other is None

    g.join(player1)

    g.save_to_db()

    assert g.state == g.State.NEW
    assert g.current is player1
    assert g.other is None

    g.join(player2)

    g.save_to_db()

    assert g.state == g.State.PLAYING
    assert g.current is player1
    assert g.other is player2

    assert g.winner() is None

    g.save_to_db()

    ships = ships_locations(player1.board)

    assert ships == ships_locations(player2.board)

    for x, y in ships[:-1]:
        g.shoot(player1.name, x, y)
        assert g.state == g.State.PLAYING

        g.shoot(player2.name, x, y)
        assert g.state == g.State.PLAYING

    g.shoot(player1.name, *ships[-1])

    assert g.state == g.State.FINISHED
    assert g.winner() is player1
