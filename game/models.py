import random
import enum

from django.db import models
from picklefield.fields import PickledObjectField


@enum.unique
class CellDisplay(enum.IntEnum):
    '''
    Represents the different ways a cell can be displayed.
    There are css classes with a 'cell-' prefix to mach each.
    '''
    hidden = 0
    cleared = 1
    flagged = 2
    mine = 3


@enum.unique
class Difficulty(enum.IntEnum):
    super_easy = 0
    easy = 1
    normal = 2
    hard = 3


class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.hidden = True
        self.has_mine = False
        self.has_flag = False
        self.nearby_mine_counter = 0
        self.safe_area_id = None

    @property
    def display(self):
        if self.has_flag:
            return CellDisplay.flagged
        if self.hidden:
            return CellDisplay.hidden
        if self.has_mine:
            return CellDisplay.mine
        return CellDisplay.cleared

    def __repr__(self):
        if self.has_mine:
            return 'B'
        elif self.nearby_mine_counter == 0:
            return 'Z{}'.format(self.safe_area_id)
        else:
            return 'N{}'.format(self.nearby_mine_counter)


class Game(models.Model):
    creation_datetime = models.DateTimeField(auto_now=True)
    difficulty = models.IntegerField(
        choices=(
            (x.value, x.name.title().replace('_', ' '))
            for x in Difficulty
        ), default=Difficulty.easy.value, null=True
    )
    game_over = models.BooleanField(default=False)
    win = models.BooleanField(default=False)
    board = PickledObjectField()  # matrix of cells

    @property
    def board_size(self):
        return len(self.board)

    @classmethod
    def create(cls, *, difficulty=Difficulty.normal):
        configuration = {
            Difficulty.super_easy: (3, 2),
            Difficulty.easy: (9, 10),
            Difficulty.normal: (16, 40),
            Difficulty.hard: (22, 99),
        }
        board_size, mine_count = configuration[difficulty]
        return cls._non_random_create(board_size, [
            (random.randint(0, board_size - 1), random.randint(0, board_size - 1))
            for _ in range(mine_count)
        ], difficulty)

    @classmethod
    def _non_random_create(cls, board_size, mine_placement, difficulty=Difficulty.normal):
        '''
        This method is useful for testing specific scenarios on the unit tests.
        '''
        game = cls(difficulty=difficulty.value)
        game.board = [
            [Cell(x, y) for x in range(board_size)]
            for y in range(board_size)
        ]
        for x, y in mine_placement:
            game._place_mine(x, y)

        game._identify_safe_areas()
        game.save()
        return game

    def flag_cell(self, x, y):
        '''
        Flags a cell unless the game is over or the cell has already being cleared.
        Checks if the end of game has been reached (See _check_for_game_over)
        Returns the game over state and the cells to update (one or zero in this case)
        '''
        cell = self.board[y][x]
        if self.game_over or cell.display == CellDisplay.cleared:
            return self.game_over, self.win, []

        cell.has_flag = not cell.has_flag
        self._check_for_game_over()
        self.save()
        return self.game_over, self.win, [cell]

    def sweep_cell(self, x, y):
        '''
        Sweeps a cell unless the game is over or the cell has a flag.
        This operation results in one of four scenarios:
            * The cell has a mine:
                Game over. Reveal all cells
            * The cell has nearby mine/s:
                Reveal only that cell and show the number of nearby mines
            * The cell is in a "safe area":
                Reveal that area including the edges showing the number of
                nearby mines (this has been precalculated at the creation of the board)
            * The cell is the last cell to reveal and all mines have been flagged:
                You win!

        Checks if the end of game has been reached (See _check_for_game_over)
        Returns the game over state and the cells to update (zero or more cells)
        '''
        cell = self.board[y][x]
        if self.game_over or cell.has_flag:
            return self.game_over, self.win, []

        cell.hidden = False
        cells_revealed = {cell}
        is_game_over = cell.has_mine
        inside_safe_area = cell.safe_area_id is not None and cell.nearby_mine_counter == 0

        if is_game_over or inside_safe_area:
            safe_area_id = cell.safe_area_id
            for x in range(self.board_size):
                for y in range(self.board_size):
                    cell = self.board[y][x]
                    clicked_on_safe_area = inside_safe_area and cell.safe_area_id == safe_area_id
                    if is_game_over or clicked_on_safe_area:
                        cell.hidden = False
                        cells_revealed.add(cell)

        self.game_over = is_game_over
        self._check_for_game_over()
        self.save()
        return self.game_over, self.win, cells_revealed

    def _place_mine(self, x, y):
        '''
        Places a mine at x, y. All surrounding cells have their nearby_mine_counter attribute
        increased. If the cell already has a mine, ignore it.
        negative indices while valid on Python should raise an exception here.
        '''
        if x < 0 or y < 0:
            raise IndexError('Negative indices not allowed in the board. x={}, y={}'.format(x, y))

        # ignoring collitions, otherwise the nearby_mine_counter will count duplicates
        if self.board[y][x].has_mine:
            return

        self.board[y][x].has_mine = True
        for i in range(max(0, x - 1), min(x + 2, self.board_size)):
            for j in range(max(0, y - 1), min(y + 2, self.board_size)):
                if self.board[j][i].has_mine:
                    continue
                self.board[j][i].nearby_mine_counter += 1
        self.board[y][x].nearby_mine_counter = 0

    def _identify_safe_areas(self):
        '''
        Identifies safe areas and gives them an unique id.
        Safe areas are defined as contiguous cells which have no mines or nearby mines.
        These are the big areas which are revealed on the game when sweeping one of those cells.

        The point of this method is avoid the expensive DFS calculation to reveal the area while
        the game is being played. Instead, the total cost is N^2 (it could be brought to
        O(number of cells in the area) by using more memory and a more complicated structure).
        '''
        direction_vectors = [(1, 0), (-1, 0), (0, -1), (0, 1)]  # up down left right

        # this is a DFS algorithm, not great. Improve this.
        # See https://en.wikipedia.org/wiki/Connected-component_labeling
        def mark_area(x, y, area_id):
            if not (0 <= x < self.board_size and 0 <= y < self.board_size):
                return
            cell = self.board[y][x]

            if cell.has_mine or cell.safe_area_id is not None:
                return

            cell.safe_area_id = area_id
            if cell.nearby_mine_counter == 0:
                for dx, dy in direction_vectors:
                    mark_area(x + dx, y + dy, area_id)

        area_id = 0
        for y in range(self.board_size):
            for x in range(self.board_size):
                cell = self.board[y][x]
                if not cell.has_mine and cell.safe_area_id is None and cell.nearby_mine_counter == 0:
                    area_id += 1
                    mark_area(x, y, area_id)

    def _check_for_game_over(self):
        '''
        Checks if the end of game has been reached (all mines have been flagged and
        the rest of the cells have been cleared)
        '''
        if self.game_over:
            return

        for y in range(self.board_size):
            for x in range(self.board_size):
                cell = self.board[y][x]
                if cell.has_mine and not cell.has_flag:
                    return
                if not cell.has_mine and cell.hidden:
                    return
        self.game_over = self.win = True

    def __str__(self):
        '''String representation of the matrix of nearby_mine_counter. Useful for debugging'''
        return '\n'.join(
            '|' + ''.join('{:2}'.format(cell.nearby_mine_counter) for cell in row) + '|'
            for row in self.board
        )
