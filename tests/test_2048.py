import unittest
from game2048 import Game
from app2048 import Game2048App


class Game2048ExamplesTest(unittest.TestCase):
    """examples/2048.md 의 # Examples 섹션을 그대로 옮긴 테스트."""

    def test_adjacent_tiles_merge(self):
        game = Game()
        game.grid = [[2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        game.score = 0
        game.move("Left")
        self.assertEqual(game.grid[0], [4, 0, 0, 0])
        self.assertEqual(game.score, 4)

    def test_no_chain_merge_in_one_move(self):
        game = Game()
        game.grid = [[2, 2, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        game.move("Left")
        self.assertEqual(game.grid[0], [4, 4, 0, 0])

    def test_no_op_move_returns_false_and_leaves_grid_unchanged(self):
        game = Game()
        game.grid = [[4, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        before = [row[:] for row in game.grid]
        changed = game.move("Left")
        self.assertFalse(changed)
        self.assertEqual(game.grid, before)

    def test_game_over_when_full_and_no_adjacent_equal(self):
        game = Game()
        game.grid = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2],
        ]
        self.assertTrue(game.isGameOver())


class Game2048RequiredTest(unittest.TestCase):
    """Domain의 test_required Game2048.Game 블록을 그대로 옮긴 테스트."""

    def test_merge_increases_score_by_merged_value(self):
        game = Game()
        game.grid = [[8, 8, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        game.score = 0
        game.move("Left")
        self.assertEqual(game.score, 16)

    def test_four_equal_tiles_pair_up_not_chain(self):
        for direction, expected in [
            ("Left", [4, 4, 0, 0]),
            ("Right", [0, 0, 4, 4]),
        ]:
            game = Game()
            game.grid = [[2, 2, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
            game.move(direction)
            self.assertEqual(game.grid[0], expected)

    def test_full_board_no_merges_is_game_over(self):
        game = Game()
        game.grid = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2],
        ]
        self.assertTrue(game.isGameOver())

    def test_move_with_nothing_to_do_returns_false(self):
        game = Game()
        game.grid = [[0, 0, 0, 2], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.assertFalse(game.move("Right"))


class Game2048SpawnTest(unittest.TestCase):
    def test_spawn_uses_90_10_split(self):
        # rng()가 항상 0을 반환하면(< 0.9) 항상 2가 나와야 한다.
        game = Game(rng=lambda: 0.0)
        self.assertTrue(all(v in (0, 2) for row in game.grid for v in row))

    def test_spawn_can_produce_four(self):
        # rng()가 항상 0.95를 반환하면(>= 0.9) 4가 나와야 한다.
        game = Game(rng=lambda: 0.95)
        self.assertTrue(any(v == 4 for row in game.grid for v in row))

    def test_win_detection(self):
        game = Game()
        game.grid[0][0] = 2048
        self.assertTrue(game.hasWon())
        game.grid[0][0] = 1024
        self.assertFalse(game.hasWon())


class Game2048GuiWiringTest(unittest.TestCase):
    """# Interface > ## GUI: onKeyDown이 실제로 Behavior.방향키로 한 번 이동을 실행하는지 확인.

    실제 창은 띄우지 않는다(CanvasWindow가 생성 즉시 withdraw한다).
    """

    def test_arrow_key_moves_and_redraws(self):
        game = Game(rng=lambda: 0.0)
        game.grid = [[2, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        game.score = 0
        app = Game2048App(game=game)

        app._onKeyDown("Left")

        self.assertEqual(app.game.grid[0][0], 4)
        self.assertEqual(app.game.score, 4)
        app.window.close()

    def test_no_op_move_does_not_spawn_a_tile(self):
        game = Game(rng=lambda: 0.0)
        game.grid = [[4, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        app = Game2048App(game=game)
        empties_before = sum(1 for row in app.game.grid for v in row if v == 0)

        app._onKeyDown("Left")  # 이미 왼쪽 끝까지 밀려 있어 변화가 없어야 한다.

        empties_after = sum(1 for row in app.game.grid for v in row if v == 0)
        self.assertEqual(empties_before, empties_after)
        app.window.close()


if __name__ == "__main__":
    unittest.main()
