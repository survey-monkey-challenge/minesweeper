import random
from enum import IntEnum

from django.db import models
from picklefield.fields import PickledObjectField


class CellState(IntEnum):
    flagged = -3
    bomb = -2
    hidden = -1
    cleared = 0


class Game(models.Model):
    creation_datetime = models.DateTimeField(auto_now=True)
    display_board = PickledObjectField()
    board = PickledObjectField()

    @classmethod
    def create(cls, board_size, *, mine_count=9, mine_placement=None):
        game = cls()
        game.display_board = [
            [CellState.hidden.value] * board_size
            for _ in range(board_size)
        ]
        game.board = [
            [None] * board_size
            for _ in range(board_size)
        ]
        if mine_placement is None:
            for _ in range(mine_count):
                x, y = random.randint(0, board_size - 1), random.randint(0, board_size - 1)
                game._place_mine(x, y, board_size)
        else:
            for x, y in mine_placement:
                game._place_mine(x, y, board_size)

        game._precalculate_empty_areas(board_size)
        return game

    def _place_mine(self, x, y, board_size):
        if x < 0 or y < 0:
            raise IndexError('Negative indices not allowed in the board. x={}, y={}'.format(x, y))

        if self.board[y][x] == 0:
            print('collition!')
            return

        self.board[y][x] = 0
        for i in range(max(0, x - 1), min(x + 2, board_size)):
            for j in range(max(0, y - 1), min(y + 2, board_size)):
                if self.board[j][i] == 0:
                    continue
                if self.board[j][i] is None:
                    self.board[j][i] = 0
                self.board[j][i] += 1

    def _precalculate_empty_areas(self, board_size):
        direction_vectors = [(1, 0), (-1, 0), (0, -1), (0, 1)]  # up down left right

        # this is a dfs algorithm, not great. Improve this.
        # See https://en.wikipedia.org/wiki/Connected-component_labeling
        def mark_area(x, y, area):
            if not (0 <= x < board_size and 0 <= y < board_size):
                return
            if self.board[y][x] is not None:
                return

            self.board[y][x] = area
            for dx, dy in direction_vectors:
                mark_area(x + dx, y + dy, area)

        area = 0
        for x in range(board_size):
            for y in range(board_size):
                if self.board[y][x] is None:
                    area -= 1
                    mark_area(x, y, area)

    def __str__(self):
        return '\n'.join(
            '|' + ''.join('{:2}'.format('' if cell is None else cell) for cell in row) + '|'
            for row in self.board
        )
