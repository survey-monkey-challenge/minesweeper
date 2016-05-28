from django.test import TestCase

from .models import Game


class BoardTests(TestCase):
    def test_mine_edge_placement(self):
        # upper left corner
        game = Game.create(3, mine_placement=[(0, 0)])
        self.assertEqual(game.board, [
            [0, 1, -1],
            [1, 1, -1],
            [-1, -1, -1],
        ])

        # bottom left corner
        game = Game.create(3, mine_placement=[(0, 2)])
        self.assertEqual(game.board, [
            [-1, -1, -1],
            [1, 1, -1],
            [0, 1, -1]
        ])

        # bottom right corner
        game = Game.create(3, mine_placement=[(2, 2)])
        self.assertEqual(game.board, [
            [-1, -1, -1],
            [-1, 1, 1],
            [-1, 1, 0]
        ])

        # upper right corner
        game = Game.create(3, mine_placement=[(2, 0)])
        self.assertEqual(game.board, [
            [-1, 1, 0],
            [-1, 1, 1],
            [-1, -1, -1]
        ])

    def test_mine_out_of_range_placement(self):
        with self.assertRaises(IndexError):
            Game.create(3, mine_placement=[(3, 0)])

        with self.assertRaises(IndexError):
            Game.create(3, mine_placement=[(0, 3)])

        with self.assertRaises(IndexError):
            Game.create(3, mine_placement=[(-1, 0)])

        with self.assertRaises(IndexError):
            Game.create(3, mine_placement=[(0, -1)])

    def test_mine_near_placement(self):
        game = Game.create(3, mine_placement=[(0, 0), (1, 0)])
        self.assertEqual(game.board, [
            [0, 0, 1],
            [2, 2, 1],
            [-1, -1, -1]
        ])

        game = Game.create(3, mine_placement=[(0, 0), (1, 0), (2, 0)])
        self.assertEqual(game.board, [
            [0, 0, 0],
            [2, 3, 2],
            [-1, -1, -1]
        ])

        game = Game.create(3, mine_placement=[(0, 0), (0, 2)])
        self.assertEqual(game.board, [
            [0, 1, -1],
            [2, 2, -1],
            [0, 1, -1]
        ])
