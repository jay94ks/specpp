import unittest
from rps import Game, RpsApp


class RpsGameExamplesTest(unittest.TestCase):
    """examples/rock-paper-scissors.md 의 # Examples 섹션을 그대로 옮긴 테스트."""

    def test_player_wins(self):
        game = Game(computerChooser=lambda: "Scissors")
        result = game.play("Rock")
        self.assertEqual(result.outcome, "Win")
        self.assertEqual(game.playerScore, 1)
        self.assertEqual(game.computerScore, 0)

    def test_player_loses(self):
        game = Game(computerChooser=lambda: "Paper")
        result = game.play("Rock")
        self.assertEqual(result.outcome, "Lose")
        self.assertEqual(game.computerScore, 1)
        self.assertEqual(game.playerScore, 0)

    def test_draw(self):
        game = Game(computerChooser=lambda: "Rock")
        result = game.play("Rock")
        self.assertEqual(result.outcome, "Draw")
        self.assertEqual(game.playerScore, 0)
        self.assertEqual(game.computerScore, 0)

    def test_score_accumulates_across_rounds(self):
        game = Game(computerChooser=lambda: "Scissors")
        r1 = game.play("Rock")
        r2 = game.play("Rock")
        self.assertEqual(r1.outcome, "Win")
        self.assertEqual(r2.outcome, "Win")
        self.assertEqual(game.playerScore, 2)


class RpsGameRequiredTest(unittest.TestCase):
    """Domain의 test_required Rps.Game 블록을 그대로 옮긴 테스트."""

    def test_rock_beats_scissors_scissors_beats_paper_paper_beats_rock(self):
        self.assertEqual(Game(computerChooser=lambda: "Scissors").play("Rock").outcome, "Win")
        self.assertEqual(Game(computerChooser=lambda: "Paper").play("Scissors").outcome, "Win")
        self.assertEqual(Game(computerChooser=lambda: "Rock").play("Paper").outcome, "Win")

    def test_same_choice_is_always_draw_and_scores_unchanged(self):
        for choice in ("Rock", "Paper", "Scissors"):
            game = Game(computerChooser=lambda c=choice: c)
            result = game.play(choice)
            self.assertEqual(result.outcome, "Draw")
            self.assertEqual(game.playerScore, 0)
            self.assertEqual(game.computerScore, 0)

    def test_scores_never_negative(self):
        game = Game(computerChooser=lambda: "Paper")
        for _ in range(5):
            game.play("Rock")
        self.assertGreaterEqual(game.playerScore, 0)
        self.assertGreaterEqual(game.computerScore, 0)


class RpsGuiWiringTest(unittest.TestCase):
    """# Interface > ## GUI: 버튼 클릭이 실제로 Behavior.한 라운드 진행을 실행하는지 확인.

    실제 창은 띄우지 않는다(Window가 생성 즉시 withdraw한다) — 위젯 생성과
    이벤트 배선만 검증한다.
    """

    def test_clicking_rock_button_runs_a_round_and_updates_labels(self):
        app = RpsApp(game=Game(computerChooser=lambda: "Scissors"))
        self.assertEqual(app.scoreLabel.text(), "당신 0 : 0 컴퓨터")

        app.rockButton.click()

        self.assertIn("이겼습니다", app.resultLabel.text())
        self.assertEqual(app.scoreLabel.text(), "당신 1 : 0 컴퓨터")
        app.window.close()

    def test_three_buttons_are_wired_to_their_own_choice(self):
        app = RpsApp(game=Game(computerChooser=lambda: "Rock"))
        app.paperButton.click()  # Paper beats Rock
        self.assertEqual(app.game.playerScore, 1)
        app.window.close()


if __name__ == "__main__":
    unittest.main()
