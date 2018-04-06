"""
Models for battleships game.

Basic assumptions:
- Game has only two players
- Player has a name and a board
- Board and ships conforms to the standard Hasbro rules (no salvo support for now!).

Link:
    https://www.hasbro.com/common/instruct/Battleship.PDF
"""

from collections import namedtuple, Counter
from enum import Enum, auto
from typing import Optional, List, Set

Ship = namedtuple('Ship', ['name', 'symbol', 'size'])

symbol_to_ship = {
    'C': Ship('Carrier', 'C', 5),
    'B': Ship('Battleship', 'B', 4),
    'R': Ship('Cruiser', 'R', 3),
    'S': Ship('Submarine', 'S', 3),
    'D': Ship('Destroyer', 'D', 2)
}


class Board:
    """Board is the main component of the game.

    It is created from a string of length == 100 which should represent a valid starting grid.
    """

    N = 10
    HIT, MISS, SUNK = '+', '-', 'x'
    ACTIONS = {HIT, MISS, SUNK}
    NO_ACTION = '.'

    def __init__(self, starting_grid: str):
        self.validate_starting_grid(starting_grid)

        self.starting_grid = starting_grid
        self.grid = starting_grid

    def enemy_view(self) -> str:
        """How enemy views this board."""
        if self.no_ships(): return self.grid

        return ''.join([self.grid[xy] if self.grid[xy] in Board.ACTIONS else ' ' for xy in range(Board.N * Board.N)])

    def can_shoot_at(self, x: int, y: int) -> bool:
        """Is it legal to shoot at field."""
        xy = self._to_1d(x, y)

        return self.grid[xy] == self.starting_grid[xy]

    def shoot(self, x: int, y: int) -> str:
        """Shoot at a field and return string with a result.

        Returns:
            Result of an action as string
                - Miss
                - Hit {ship_name}
                - Sunk {ship_name}

        Raises:
            ValueError if action can't take place on this field (x,y was already shot at).
        """
        if not self.can_shoot_at(x, y): raise ValueError(f"Field ({x}, {y}) was already acted upon.")

        xy = self._to_1d(x, y)

        if self.grid[xy] == Board.NO_ACTION:
            self.grid = self.grid[:xy] + self.MISS + self.grid[xy + 1:]
            return 'Miss'
        else:
            symbol = self.grid[xy]
            self.grid = self.grid[:xy] + self.HIT + self.grid[xy + 1:]

            if symbol in self.grid:
                return f'Hit {symbol_to_ship[symbol].name}'
            else:
                self.grid = ''.join([self.grid[i] if self.starting_grid[i] != symbol else self.SUNK for i in range(Board.N * Board.N)])

                return f'Sunk {symbol_to_ship[symbol].name}'

    def no_ships(self) -> bool:
        """All ships sunk?"""
        return set(self.grid) <= Board.ACTIONS | set(Board.NO_ACTION)

    def remaining_ships(self) -> Set[str]:
        """Return set of symbols of remaining ships."""
        return set(self.grid) & set(symbol_to_ship.keys())

    def sunk_ships(self) -> Set[str]:
        """Return set of symbols of sunk ships."""
        return set(symbol_to_ship.keys()) - self.remaining_ships()

    @staticmethod
    def _to_1d(x: int, y: int) -> int: return y*Board.N + x

    @staticmethod
    def grid_as_matrix(grid) -> List[str]:
        """Transforms grid into 2d representation."""
        return [grid[i:i + Board.N] for i in range(0, len(grid), Board.N)]

    @staticmethod
    def validate_starting_grid(grid: str):
        """Raises ValueError if grid is not valid starting grid.

        Valid starting grid has:
            - len == 100
            - only ships and empty fields
            - ships are of valid sizes
            - ships are placed horizontally or vertically

        Raises:
            ValueError if one of the conditions is not True.
        """
        counter = Counter(grid)
        matrix_grid = '\n'.join(Board.grid_as_matrix(grid))

        if len(grid) != Board.N * Board.N:
            raise ValueError(f"Grid has to be of length 100.\n{matrix_grid}")

        for _, v in symbol_to_ship.items():
            if v.size != counter[v.symbol]:
                raise ValueError(f"Grid has ships of illegal sizes.\n{matrix_grid}")

        if set(grid) != (set(symbol_to_ship.keys()) | set(Board.NO_ACTION)):
            raise ValueError(f"Grid has more than ships and empty fields. {matrix_grid}")

        for symbol, s in symbol_to_ship.items():
            g = Board.grid_as_matrix(grid)
            row, col = divmod(grid.index(symbol), Board.N)

            symbols_in_row = g[row].count(symbol)

            if symbols_in_row == 1:  # must be vertically placed
                g = [''.join(r) for r in zip(*g)]  # transposing matrix to make horizontal placement out of vertical

                for r in range(Board.N):
                    if symbol in g[r]:
                        row, col = r, g[r].index(symbol)  # new row, col pair of a first symbol
                        break

            if col + s.size > Board.N or g[row][col:col+s.size] != symbol * s.size:
                raise ValueError(f"Ship {s.symbol} is not placed correctly.\n{matrix_grid}")


class Player:
    """Player ties name and board together."""

    def __init__(self, name: str, board: Board):
        self.name = name
        self.board = board


class Game:
    """Game is an object which couples players and their actions.

    When both players are in game, they shoot in turns until one of the players have no ships.
    Once the game is finished no player can shoot.

    At first game is in State.NEW. After another player joins in, it is in State.PLAYING. When one of the players have
    no ships left it switches to State.FINISHED.
    """

    class State(Enum):
        NEW = auto()
        PLAYING = auto()
        FINISHED = auto()

    def __init__(self):
        self.current = None
        self.other = None

        self.state = self.State.NEW

    def join(self, player: Player):
        """Join new player to the game."""
        if self.state != self.State.NEW:
            raise ValueError(f"Can't join players when game is not in state NEW. State={self.state}")

        if self.current is None:
            self.current = player
        else:
            if self.current is player:
                raise ValueError(f"Player can't join the same game twice.")
            self.other = player
            self.state = self.State.PLAYING

    def shoot(self, player_name: str, x: int, y: int) -> str:
        """Try to shoot as player.

        Returns:
            Action result as a string.

        Raises:
            ValueError if shot cannot be taken.
        """
        if self.current is None:
            raise ValueError(f"No players in game")

        if self.current.name != player_name:
            raise ValueError(f"It's '{self.current.name}' turn")

        if self.state != self.State.PLAYING:
            raise ValueError(f"Game is in state '{self.state}' - can't shoot.")

        result = self.other.board.shoot(x, y)

        if self.other.board.no_ships():
            self.state = self.State.FINISHED
        else:
            self.other, self.current = self.current, self.other

        return result

    def winner(self) -> Optional[Player]:
        return self.current if self.state == self.State.FINISHED else None
