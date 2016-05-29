import random

from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Game
from .forms import CreateGameForm


class BoardTests(TestCase):
    def test_mine_edge_placement(self):
        # upper left corner
        game = Game._non_random_create(3, [(0, 0)])
        self.assertEqual(self.get_cells(game), [
            [(0, None), (1, 1), (0, 1)],
            [(1, 1), (1, 1), (0, 1)],
            [(0, 1), (0, 1), (0, 1)]
        ])

        # bottom left corner
        game = Game._non_random_create(3, [(0, 2)])
        self.assertEqual(self.get_cells(game), [
            [(0, 1), (0, 1), (0, 1)],
            [(1, 1), (1, 1), (0, 1)],
            [(0, None), (1, 1), (0, 1)]
        ])

        # bottom right corner
        game = Game._non_random_create(3, [(2, 2)])
        self.assertEqual(self.get_cells(game), [
            [(0, 1), (0, 1), (0, 1)],
            [(0, 1), (1, 1), (1, 1)],
            [(0, 1), (1, 1), (0, None)]
        ])

        # upper right corner
        game = Game._non_random_create(3, [(2, 0)])
        self.assertEqual(self.get_cells(game), [
            [(0, 1), (1, 1), (0, None)],
            [(0, 1), (1, 1), (1, 1)],
            [(0, 1), (0, 1), (0, 1)]
        ])

    def test_mine_out_of_range_placement(self):
        with self.assertRaises(IndexError):
            Game._non_random_create(3, [(3, 0)])

        with self.assertRaises(IndexError):
            Game._non_random_create(3, [(0, 3)])

        with self.assertRaises(IndexError):
            Game._non_random_create(3, [(-1, 0)])

        with self.assertRaises(IndexError):
            Game._non_random_create(3, [(0, -1)])

    def test_mine_near_placement(self):
        game = Game._non_random_create(3, [(0, 0), (1, 0)])
        self.assertEqual(self.get_cells(game), [
            [(0, None), (0, None), (1, None)],
            [(2, 1), (2, 1), (1, 1)],
            [(0, 1), (0, 1), (0, 1)]
        ])

        game = Game._non_random_create(3, [(0, 0), (1, 0), (2, 0)])
        self.assertEqual(self.get_cells(game), [
            [(0, None), (0, None), (0, None)],
            [(2, 1), (3, 1), (2, 1)],
            [(0, 1), (0, 1), (0, 1)]
        ])

        game = Game._non_random_create(3, [(0, 0), (0, 2)])
        self.assertEqual(self.get_cells(game), [
            [(0, None), (1, 1), (0, 1)],
            [(2, None), (2, 1), (0, 1)],
            [(0, None), (1, 1), (0, 1)]
        ])

    def test_mine_belonging_to_multiple_safe_areas(self):
        game = Game._non_random_create(5, [(x, 2) for x in range(5)])
        self.assertEqual(self.get_cells(game), [
            [(0, 1), (0, 1), (0, 1), (0, 1), (0, 1)],
            [(2, 1), (3, 1), (3, 1), (3, 1), (2, 1)],
            [(0, None), (0, None), (0, None), (0, None), (0, None)],
            [(2, 2), (3, 2), (3, 2), (3, 2), (2, 2)],
            [(0, 2), (0, 2), (0, 2), (0, 2), (0, 2)]
        ])

    def get_cells(self, game):
        return [
            [(c.nearby_mine_counter, c.safe_area_id) for c in row]
            for row in game.board
        ]


class GameLogicTests(TestCase):
    def test_game_over(self):
        game = Game._non_random_create(3, [(0, 0)])

        game_over, win, _ = game.sweep_cell(2, 2)  # sweep bottom right corner (no mine)
        self.assertFalse(game_over)
        self.assertFalse(win)

        game_over, win, _ = game.sweep_cell(0, 0)  # sweep upper left corner (mine)
        self.assertTrue(game_over)
        self.assertFalse(win)

    def test_flag(self):
        game = Game._non_random_create(3, [(0, 0)])

        self.assertFalse(game.board[0][0].has_flag)
        game_over, win, updated_cells = game.flag_cell(0, 0)  # flag upper left corner
        self.assertTrue(game.board[0][0].has_flag)
        self.assertFalse(game_over)
        self.assertFalse(win)
        self.assertEqual(len(updated_cells), 1)  # only the flag cell should change

        # Flag again. It should toggle it
        game_over, win, updated_cells = game.flag_cell(0, 0)  # flag upper left corner
        self.assertFalse(game.board[0][0].has_flag)
        self.assertFalse(game_over)
        self.assertFalse(win)
        self.assertEqual(len(updated_cells), 1)  # only the flag cell should change

    def test_cant_flag_cleared_cell(self):
        game = Game._non_random_create(3, [(0, 0)])

        game_over, win, _ = game.sweep_cell(2, 2)  # sweep bottom right corner (no mine)
        self.assertFalse(game_over)
        self.assertFalse(win)

        # try to flag the cleared cell
        self.assertFalse(game.board[2][2].has_flag)
        game_over, win, updated_cells = game.flag_cell(2, 2)  # flag bottom right corner
        self.assertFalse(game.board[2][2].has_flag)  # still false, didn't change
        self.assertFalse(game_over)
        self.assertFalse(win)
        self.assertEqual(len(updated_cells), 0)  # no updates from the server

    def test_cant_clear_flagged_cell(self):
        game = Game._non_random_create(3, [(0, 0)])

        self.assertFalse(game.board[0][0].has_flag)
        game_over, win, _ = game.flag_cell(0, 0)  # flag upper left corner (mine)
        self.assertTrue(game.board[0][0].has_flag)
        self.assertFalse(game_over)
        self.assertFalse(win)

        # try to clear the flagged cell
        self.assertTrue(game.board[0][0].hidden)
        game_over, win, updated_cells = game.sweep_cell(0, 0)  # clear upper left corner
        self.assertTrue(game.board[0][0].hidden)  # still true, didn't change
        self.assertFalse(game_over)
        self.assertFalse(win)
        self.assertEqual(len(updated_cells), 0)  # no updates from the server

    def test_no_updates_after_game_over(self):
        game = Game._non_random_create(3, [(0, 0)])

        game_over, win, _ = game.sweep_cell(2, 2)  # sweep bottom right corner (no mine)
        self.assertFalse(game_over)
        self.assertFalse(win)

        game_over, win, _ = game.sweep_cell(0, 0)  # sweep upper left corner (mine)
        self.assertTrue(game_over)
        self.assertFalse(win)

        # try to clear random cell
        x, y = random.randint(0, 2), random.randint(0, 2)
        hidden_before = game.board[x][y].hidden
        game_over, win, updated_cells = game.sweep_cell(x, y)
        self.assertEqual(hidden_before, game.board[x][y].hidden)  # didn't change
        self.assertTrue(game_over)
        self.assertFalse(win)
        self.assertEqual(len(updated_cells), 0)  # no updates from the server

        # try to flag random cell
        flag_before = game.board[x][y].has_flag
        game_over, win, updated_cells = game.flag_cell(x, y)  # flag bottom right corner
        self.assertEqual(flag_before, game.board[x][y].has_flag)  # didn't change
        self.assertTrue(game_over)
        self.assertFalse(win)
        self.assertEqual(len(updated_cells), 0)  # no updates from the server


class GameViewTests(TestCase):
    def test_create_game_get_view(self):
        response = self.client.get(reverse('game:create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Start new game")
        self.assertIsInstance(response.context['form'], CreateGameForm)

    def test_create_game_post_view(self):
        response = self.client.post(reverse('game:create'), {'difficulty': 1})
        self.assertEqual(response.status_code, 302)

    def test_game_view(self):
        response = self.client.post(reverse('game:create'), {'difficulty': 1})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)  # new game url
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Start new game")
        self.assertIsInstance(response.context['form'], CreateGameForm)
