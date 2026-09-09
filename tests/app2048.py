"""examples/2048.md 의 # Interface > ## GUI 참조 구현 (tkinter Canvas 기반).

Windows/DirectX 대상일 때는 std/windows/direct2d.md로 렌더링하는 것이
Constraints에서 우선이지만, 여기서는 std/ui/canvas.md 계약을 만족하는
다른 2D 렌더러(Constraints가 명시적으로 허용)로 Python에서 검증한다.
게임 로직(game2048.Game)은 렌더러와 무관하게 그대로 재사용한다.
"""
from game2048 import Game, SIZE
from spp_std.canvas_ import CanvasWindow

TILE_COLORS = {
    0: "#CDC1B4",
    2: "#EEE4DA",
    4: "#EDE0C8",
    8: "#F2B179",
    16: "#F59563",
    32: "#F67C5F",
    64: "#F65E3B",
    128: "#EDCF72",
    256: "#EDCC61",
    512: "#EDC850",
    1024: "#EDC53F",
    2048: "#EDC22E",
}
DEFAULT_TILE_COLOR = "#3C3A32"
LIGHT_TEXT = "#F9F6F2"
DARK_TEXT = "#776E65"
BOARD_BG = "#BBADA0"

CELL = 90
PAD = 10
BOARD_TOP = 60


class Game2048App:
    # spp-source: examples/2048.md#Interface.GUI
    def __init__(self, game=None):
        self.game = game or Game()
        self._won_announced = False
        size = PAD + SIZE * (CELL + PAD) + BOARD_TOP
        self.window = CanvasWindow("2048", size, size)
        self.window.onKeyDown = self._onKeyDown
        self.window.onRender = self._onRender
        self.window.requestRedraw()

    # spp-source: examples/2048.md#Behavior.방향키로 한 번 이동
    def _onKeyDown(self, direction):
        moved = self.game.move(direction)
        if moved:
            self.game.spawnRandomTile()
        self.window.requestRedraw()
        if self.game.hasWon() and not self._won_announced:
            self._won_announced = True

    def _onRender(self, canvas):
        canvas.clear(BOARD_BG)
        canvas.drawText(PAD, 15, f"점수: {self.game.score}", DARK_TEXT, 18)
        if self.game.isGameOver():
            canvas.drawText(PAD, 35, "게임 오버", "#FF0000", 14)
        elif self._won_announced:
            canvas.drawText(PAD, 35, "2048 달성!", "#008000", 14)

        for r in range(SIZE):
            for c in range(SIZE):
                value = self.game.grid[r][c]
                x = PAD + c * (CELL + PAD)
                y = BOARD_TOP + PAD + r * (CELL + PAD)
                color = TILE_COLORS.get(value, DEFAULT_TILE_COLOR)
                canvas.fillRect(x, y, CELL, CELL, color)
                if value:
                    text_color = DARK_TEXT if value <= 4 else LIGHT_TEXT
                    canvas.drawText(x + CELL / 2 - 12, y + CELL / 2 - 12, str(value), text_color, 20)
