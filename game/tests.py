from django.test import TestCase

from .models import Game


class BoardTests(TestCase):
    def test_mine_edge_placement(self):
        # upper left corner
        game = Game.create(board_size=3, mine_placement=[(0, 0)])
        self.assertEqual(self.get_cells(game), [
            [(0, None), (1, 1), (0, 1)],
            [(1, 1), (1, 1), (0, 1)],
            [(0, 1), (0, 1), (0, 1)]
        ])

        # bottom left corner
        game = Game.create(board_size=3, mine_placement=[(0, 2)])
        self.assertEqual(self.get_cells(game), [
            [(0, 1), (0, 1), (0, 1)],
            [(1, 1), (1, 1), (0, 1)],
            [(0, None), (1, 1), (0, 1)]
        ])

        # bottom right corner
        game = Game.create(board_size=3, mine_placement=[(2, 2)])
        self.assertEqual(self.get_cells(game), [
            [(0, 1), (0, 1), (0, 1)],
            [(0, 1), (1, 1), (1, 1)],
            [(0, 1), (1, 1), (0, None)]
        ])

        # upper right corner
        game = Game.create(board_size=3, mine_placement=[(2, 0)])
        self.assertEqual(self.get_cells(game), [
            [(0, 1), (1, 1), (0, None)],
            [(0, 1), (1, 1), (1, 1)],
            [(0, 1), (0, 1), (0, 1)]
        ])

    def test_mine_out_of_range_placement(self):
        with self.assertRaises(IndexError):
            Game.create(board_size=3, mine_placement=[(3, 0)])

        with self.assertRaises(IndexError):
            Game.create(board_size=3, mine_placement=[(0, 3)])

        with self.assertRaises(IndexError):
            Game.create(board_size=3, mine_placement=[(-1, 0)])

        with self.assertRaises(IndexError):
            Game.create(board_size=3, mine_placement=[(0, -1)])

    def test_mine_near_placement(self):
        game = Game.create(board_size=3, mine_placement=[(0, 0), (1, 0)])
        self.assertEqual(self.get_cells(game), [
            [(0, None), (0, None), (1, None)],
            [(2, 1), (2, 1), (1, 1)],
            [(0, 1), (0, 1), (0, 1)]
        ])

        game = Game.create(board_size=3, mine_placement=[(0, 0), (1, 0), (2, 0)])
        self.assertEqual(self.get_cells(game), [
            [(0, None), (0, None), (0, None)],
            [(2, 1), (3, 1), (2, 1)],
            [(0, 1), (0, 1), (0, 1)]
        ])

        game = Game.create(board_size=3, mine_placement=[(0, 0), (0, 2)])
        self.assertEqual(self.get_cells(game), [
            [(0, None), (1, 1), (0, 1)],
            [(2, None), (2, 1), (0, 1)],
            [(0, None), (1, 1), (0, 1)]
        ])

    def test_mine_belonging_to_multiple_safe_areas(self):
        game = Game.create(board_size=5, mine_placement=[(x, 2) for x in range(5)])
        self.assertEqual(self.get_cells(game), [
            [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1)],
            [(2, 1), (3, 1), (3, 1), (3, 1), (2, 1)],
            [(0, None), (0, None), (0, None), (0, None), (0, None)],
            [(2, 2), (3, 2), (3, 2), (3, 2), (2, 2)],
            [(0, 2), (0, 2), (0, 2), (0, 2), (0, 2)]
        ])

    def get_cells(self, game):
        return [
            [(c.neighbor_mines, c.safe_area_id) for c in row]
            for row in game.board
        ]
