import random
import enum

from django.db import models
from picklefield.fields import PickledObjectField


@enum.unique
class CellDisplay(enum.IntEnum):
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
        self.x = x
        self.y = y
        self.hidden = True
        self.has_mine = False
        self.has_flag = False
        self.neighbor_mines = 0
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
        elif self.neighbor_mines == 0:
            return 'Z{}'.format(self.safe_area_id)
        else:
            return 'N{}'.format(self.neighbor_mines)


class Game(models.Model):
    configuration = {
        Difficulty.super_easy: (3, 2),
        Difficulty.easy: (9, 10),
        Difficulty.normal: (16, 40),
        Difficulty.hard: (22, 99),
    }

    creation_datetime = models.DateTimeField(auto_now=True)
    board = PickledObjectField()
    difficulty = models.IntegerField(
        choices=(
            (x.value, x.name.title().replace('_', ' ')) for x in Difficulty
        ), default=Difficulty.easy.value, null=True
    )
    game_over = models.BooleanField(default=False)
    win = models.BooleanField(default=False)

    @property
    def board_size(self):
        return len(self.board)

    @classmethod
    def create(cls, *, difficulty=None, board_size=None, mine_placement=None):
        if difficulty is not None:
            board_size, mine_count = cls.configuration[difficulty]

        game = cls(difficulty=difficulty.value)
        game.board = [
            [Cell(x, y) for x in range(board_size)]
            for y in range(board_size)
        ]
        if mine_placement is None:
            for _ in range(mine_count):
                x, y = random.randint(0, board_size - 1), random.randint(0, board_size - 1)
                game._place_mine(x, y)
        else:
            for x, y in mine_placement:
                game._place_mine(x, y)

        game._precalculate_empty_areas()
        game.save()
        return game

    def flag(self, x, y):
        if self.game_over:
            return self.game_over, self.win, []

        cell = self.board[y][x]
        if cell.display == CellDisplay.cleared:
            return self.game_over, self.win, []
        cell.has_flag = not cell.has_flag
        self._check_for_game_over()
        self.save()
        return self.game_over, self.win, [cell]

    def sweep(self, x, y):
        '''
        Reveals safe area. It updates the display board and returns the cells that changed.
        '''
        if self.game_over:
            return self.game_over, self.win, []

        cell = self.board[y][x]
        cell.hidden = False
        cells_revealed = {cell}
        is_game_over = cell.has_mine
        is_safe_area = cell.safe_area_id is not None and cell.neighbor_mines == 0

        if is_game_over or is_safe_area:
            safe_area_id = cell.safe_area_id
            for x in range(self.board_size):
                for y in range(self.board_size):
                    cell = self.board[y][x]
                    clicked_on_safe_area = is_safe_area and cell.safe_area_id == safe_area_id
                    if is_game_over or clicked_on_safe_area:
                        cell.hidden = False
                        cells_revealed.add(cell)

        self.game_over = is_game_over
        self._check_for_game_over()
        self.save()
        return self.game_over, self.win, cells_revealed

    def _place_mine(self, x, y):
        if x < 0 or y < 0:
            raise IndexError('Negative indices not allowed in the board. x={}, y={}'.format(x, y))

        if self.board[y][x].has_mine:  # ignoring collitions
            return

        self.board[y][x].has_mine = True
        for i in range(max(0, x - 1), min(x + 2, self.board_size)):
            for j in range(max(0, y - 1), min(y + 2, self.board_size)):
                if self.board[j][i].has_mine:
                    continue
                self.board[j][i].neighbor_mines += 1
        self.board[y][x].neighbor_mines = 0

    def _precalculate_empty_areas(self):
        direction_vectors = [(1, 0), (-1, 0), (0, -1), (0, 1)]  # up down left right

        # this is a dfs algorithm, not great. Improve this.
        # See https://en.wikipedia.org/wiki/Connected-component_labeling
        def mark_area(x, y, area_id):
            if not (0 <= x < self.board_size and 0 <= y < self.board_size):
                return
            cell = self.board[y][x]

            if cell.has_mine or cell.safe_area_id is not None:
                return

            cell.safe_area_id = area_id
            if cell.neighbor_mines == 0:
                for dx, dy in direction_vectors:
                    mark_area(x + dx, y + dy, area_id)

        area_id = 0
        for y in range(self.board_size):
            for x in range(self.board_size):
                cell = self.board[y][x]
                if not cell.has_mine and cell.safe_area_id is None and cell.neighbor_mines == 0:
                    area_id += 1
                    mark_area(x, y, area_id)

    def _check_for_game_over(self):
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
        return '\n'.join(
            '|' + ''.join('{:2}'.format(cell.neighbor_mines) for cell in row) + '|'
            for row in self.board
        )
