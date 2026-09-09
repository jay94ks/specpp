"""examples/doom/hud.md 의 # Domain/# Behavior 참조 구현."""


class Hud:
    def __init__(self):
        self.faceFrame = "STFST01"  # 기본(평온) 표정.

    # spp-source: examples/doom/hud.md#Feature:_얼굴_표정_갱신
    def updateFace(self, player, justDamagedFromDirection=None, justKilled=False):
        ratio = player.health / max(player.maxHealth, 1)

        if player.health <= 0:
            self.faceFrame = "STFDEAD0"
            return self.faceFrame

        if ratio <= 0.20:
            base = "STFEVL"  # 많이 다친(고통스러운) 등급.
        elif ratio <= 0.40:
            base = "STFOUCH"
        elif ratio <= 0.70:
            base = "STFKILL"
        else:
            base = "STFST"

        if justDamagedFromDirection is not None:
            self.faceFrame = f"{base}_HIT_{justDamagedFromDirection}"
        elif justKilled and ratio > 0.20:
            self.faceFrame = f"{base}_GRIN"
        else:
            self.faceFrame = base

        return self.faceFrame
