"""examples/2048.md 의 # Domain(Game2048.Game) 참조 구현. GUI와 무관하다."""
import random

SIZE = 4


def _merge_line(line):
    """line은 이동 방향 쪽(인덱스 0)이 기준이 되도록 이미 정렬되어 있다고 가정한다."""
    filtered = [v for v in line if v != 0]
    merged = []
    gained = 0
    i = 0
    while i < len(filtered):
        if i + 1 < len(filtered) and filtered[i] == filtered[i + 1]:
            value = filtered[i] * 2
            merged.append(value)
            gained += value
            i += 2
        else:
            merged.append(filtered[i])
            i += 1
    merged += [0] * (len(line) - len(merged))
    return merged, gained


class Game:
    def __init__(self, rng=None):
        self._rng = rng or random.random
        self.grid = [[0] * SIZE for _ in range(SIZE)]
        self.score = 0
        self.spawnRandomTile()
        self.spawnRandomTile()

    # spp-source: examples/2048.md#Domain.Class:Game2048.Game
    def move(self, direction):
        before = [row[:] for row in self.grid]

        if direction in ("Left", "Right"):
            for r in range(SIZE):
                line = self.grid[r][:]
                reversed_ = direction == "Right"
                if reversed_:
                    line = line[::-1]
                merged, gained = _merge_line(line)
                if reversed_:
                    merged = merged[::-1]
                self.grid[r] = merged
                self.score += gained
        elif direction in ("Up", "Down"):
            for c in range(SIZE):
                col = [self.grid[r][c] for r in range(SIZE)]
                reversed_ = direction == "Down"
                if reversed_:
                    col = col[::-1]
                merged, gained = _merge_line(col)
                if reversed_:
                    merged = merged[::-1]
                for r in range(SIZE):
                    self.grid[r][c] = merged[r]
                self.score += gained
        else:
            raise ValueError(f"unknown direction: {direction}")

        return self.grid != before

    def spawnRandomTile(self):
        empties = [(r, c) for r in range(SIZE) for c in range(SIZE) if self.grid[r][c] == 0]
        if not empties:
            return
        idx = min(int(self._rng() * len(empties)), len(empties) - 1)
        r, c = empties[idx]
        self.grid[r][c] = 2 if self._rng() < 0.9 else 4

    def isGameOver(self):
        for r in range(SIZE):
            for c in range(SIZE):
                if self.grid[r][c] == 0:
                    return False
        for r in range(SIZE):
            for c in range(SIZE):
                v = self.grid[r][c]
                if c + 1 < SIZE and self.grid[r][c + 1] == v:
                    return False
                if r + 1 < SIZE and self.grid[r + 1][c] == v:
                    return False
        return True

    def hasWon(self):
        return any(v >= 2048 for row in self.grid for v in row)
