import unittest
import numpy as np
from game2048 import *

class TestGame2048(unittest.TestCase):

    def setUp(self):
        self.game = Game2048()

    def test_create_grid(self):
        grid = self.game.create_grid()
        self.assertEqual(grid.shape, (4, 4))
        self.assertTrue(np.all(grid == 0))


    def test_add_random_tile(self):
        grid_before = self.game.grid.copy()
        self.game.add_random_tile()
        grid_after = self.game.grid
        diff = np.count_nonzero(grid_before - grid_after)
        self.assertEqual(diff, 1)

    def test_move_tiles_helper_up(self):
        test_grid = np.array([[2, 0, 2, 0], [0, 4, 4, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
        expected_grid = np.array([[4, 0, 0, 0], [4, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
        result = self.game.move_tiles_helper(test_grid, "up")
        np.testing.assert_array_equal(result, expected_grid)


    def test_check_win(self):
        self.game.grid = np.array([[2, 4, 8, 16], [4, 2, 16, 8], [16, 2, 8, 4], [16, 4, 8, 2]])
        self.assertTrue(self.game.check_win())
        self.game.grid[0, 0] = 0
        self.assertFalse(self.game.check_win())


if __name__ == "__main__":
    unittest.main()