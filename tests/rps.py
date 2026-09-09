"""examples/rock-paper-scissors.md reference implementation."""
import random

from spp_std.ui_ import Window, Button, Label

BEATS = {
    "Rock": "Scissors",
    "Scissors": "Paper",
    "Paper": "Rock",
}


class RoundResult:
    def __init__(self, playerChoice, computerChoice, outcome):
        self.playerChoice = playerChoice
        self.computerChoice = computerChoice
        self.outcome = outcome


class Game:
    def __init__(self, computerChooser=None):
        self._computerChooser = computerChooser or (lambda: random.choice(list(BEATS.keys())))
        self.playerScore = 0
        self.computerScore = 0

    # spp-source: examples/rock-paper-scissors.md#Domain.Class:Rps.Game
    def play(self, playerChoice):
        computerChoice = self._computerChooser()

        if playerChoice == computerChoice:
            outcome = "Draw"
        elif BEATS[playerChoice] == computerChoice:
            outcome = "Win"
            self.playerScore += 1
        else:
            outcome = "Lose"
            self.computerScore += 1

        return RoundResult(playerChoice, computerChoice, outcome)


_LABELS = {"Rock": "바위", "Paper": "보", "Scissors": "가위"}
_OUTCOME_TEXT = {"Win": "이겼습니다!", "Lose": "졌습니다.", "Draw": "비겼습니다."}


class RpsApp:
    """examples/rock-paper-scissors.md 의 # Interface > ## GUI 를 그대로 옮긴 것."""

    # spp-source: examples/rock-paper-scissors.md#Interface.GUI
    def __init__(self, game=None):
        self.game = game or Game()
        self.window = Window("가위바위보", 320, 200)
        self.resultLabel = Label("눌러서 시작하세요")
        self.scoreLabel = Label(self._score_text())

        self.rockButton = Button("✊ 바위")
        self.paperButton = Button("✋ 보")
        self.scissorsButton = Button("✌️ 가위")

        self.rockButton.onClick = lambda: self._play("Rock")
        self.paperButton.onClick = lambda: self._play("Paper")
        self.scissorsButton.onClick = lambda: self._play("Scissors")

        for widget in (self.rockButton, self.paperButton, self.scissorsButton,
                       self.resultLabel, self.scoreLabel):
            self.window.addChild(widget)

    # spp-source: examples/rock-paper-scissors.md#Behavior.한 라운드 진행
    def _play(self, choice):
        result = self.game.play(choice)
        self.resultLabel.setText(
            f"당신: {_LABELS[result.playerChoice]} / "
            f"컴퓨터: {_LABELS[result.computerChoice]} — {_OUTCOME_TEXT[result.outcome]}"
        )
        self.scoreLabel.setText(self._score_text())
        return result

    def _score_text(self):
        return f"당신 {self.game.playerScore} : {self.game.computerScore} 컴퓨터"
