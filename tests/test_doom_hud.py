import unittest

from doom_actors import Actor, MONSTER_TYPES, Player
from doom_hud import Hud


class HudFaceExampleTest(unittest.TestCase):
    """hud.md의 '## 예제: 체력이 0에 가까우면 고통스러운 얼굴'을 그대로 옮긴 테스트."""

    def test_low_health_shows_hurt_face(self):
        actor = Actor.Spawn(MONSTER_TYPES["Zombieman"], 0, 0)
        player = Player(actor)
        player.health = 10
        hud = Hud()
        hud.updateFace(player)
        self.assertIn("STFEVL", hud.faceFrame)


class HudFaceGradientTest(unittest.TestCase):
    def test_full_health_shows_calm_face(self):
        actor = Actor.Spawn(MONSTER_TYPES["Zombieman"], 0, 0)
        player = Player(actor)
        player.health = 100
        hud = Hud()
        hud.updateFace(player)
        self.assertIn("STFST", hud.faceFrame)

    def test_zero_health_shows_dead_face(self):
        actor = Actor.Spawn(MONSTER_TYPES["Zombieman"], 0, 0)
        player = Player(actor)
        player.health = 0
        hud = Hud()
        hud.updateFace(player)
        self.assertEqual(hud.faceFrame, "STFDEAD0")

    def test_recent_hit_shows_directional_face(self):
        actor = Actor.Spawn(MONSTER_TYPES["Zombieman"], 0, 0)
        player = Player(actor)
        player.health = 80
        hud = Hud()
        hud.updateFace(player, justDamagedFromDirection="left")
        self.assertIn("HIT_left", hud.faceFrame)


if __name__ == "__main__":
    unittest.main()
