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
    pass


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
