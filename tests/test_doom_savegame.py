import tempfile
import unittest

from doom_game import Game
from doom_savegame import SaveGame
from doom_specials import Door
from doom_test_fixtures import MAP_NAME, build_two_room_map_wad
from doom_wad import WadFile


class SaveGameRoundTripTest(unittest.TestCase):
    """savegame.md의 test_required Doom.SaveGame 블록을 그대로 옮긴 테스트."""

    def setUp(self):
        f = tempfile.NamedTemporaryFile(suffix=".wad", delete=False)
        f.write(build_two_room_map_wad())
        f.close()
        self.wad = WadFile(f.name)
        self.game = Game.Start(self.wad, MAP_NAME, rng=lambda: 0.0)

    def test_restore_immediately_after_save_matches_original_state(self):
        self.game.player.health = 63
        self.game.player.armor = 40
        self.game.player.ammo["bullets"] = 17
        self.game.killCount = 2
        door = Door(self.game.map.sectors[1], "Open", targetCeilingHeight=96, speed=4)
        door.sector.ceilingHeight = 50
        self.game.specials.append(door)

        snapshot = SaveGame.Save(self.game, "E1M1 테스트 저장")
        restored = snapshot.restore(self.wad)

        self.assertEqual(restored.player.health, 63)
        self.assertEqual(restored.player.armor, 40)
        self.assertEqual(restored.player.ammo["bullets"], 17)
        self.assertEqual(restored.killCount, 2)
        self.assertEqual((restored.player.actor.x, restored.player.actor.y),
                          (self.game.player.actor.x, self.game.player.actor.y))
        self.assertEqual(len(restored.specials), 1)
        self.assertEqual(restored.specials[0].sector.ceilingHeight, 50)
        # 복제된 SectorMover가 복사본이 아니라 restore()로 새로 불러온 맵의 실제
        # 섹터를 가리키는지 확인한다 — 그래야 이후 tick()이 실제 맵에 반영된다.
        self.assertIs(restored.specials[0].sector, restored.map.sectors[1])
        self.assertEqual(restored.map.sectors[1].ceilingHeight, 50)
        self.assertEqual(len(restored.actors), len(self.game.actors))

    def test_restoring_does_not_mutate_the_original_snapshot(self):
        snapshot = SaveGame.Save(self.game, "slot 1")
        restored = snapshot.restore(self.wad)
        restored.player.health = 1
        self.assertNotEqual(snapshot.player.health, 1)


if __name__ == "__main__":
    unittest.main()
