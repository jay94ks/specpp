import unittest

from doom_map import LineDef, Sector, SideDef, Vertex
from doom_specials import (
    Ceiling, Door, FloorMover, LightFlash, Platform, advance_specials,
    trigger_line_special,
)


class DoorRequiredTest(unittest.TestCase):
    """specials.md의 test_required Doom.Door 블록을 그대로 옮긴 테스트."""

    def test_open_door_reaches_target_and_reports_finished(self):
        sector = Sector(0, 0, "F", "C", 160, 0, 0)
        door = Door(sector, "Open", targetCeilingHeight=128, speed=8)
        still_going = True
        for _ in range(1000):
            still_going = door.tick()
            if not still_going:
                break
        self.assertEqual(sector.ceilingHeight, 128)
        self.assertFalse(still_going)

    def test_open_then_close_reopens_if_blocked(self):
        sector = Sector(0, 0, "F", "C", 160, 0, 0)
        door = Door(sector, "OpenThenClose", targetCeilingHeight=128, speed=64)
        door.waitTicsRemaining = 2
        for _ in range(3):
            door.tick()
        self.assertEqual(sector.ceilingHeight, 128)


class FloorMoverTest(unittest.TestCase):
    def test_floor_rises_to_target(self):
        sector = Sector(0, 64, "F", "C", 160, 0, 0)
        mover = FloorMover(sector, targetFloorHeight=32, speed=8)
        while mover.tick():
            pass
        self.assertEqual(sector.floorHeight, 32)


class CeilingCrusherTest(unittest.TestCase):
    def test_repeating_crusher_bounces_between_top_and_bottom(self):
        sector = Sector(0, 128, "F", "C", 160, 0, 0)
        crusher = Ceiling(sector, topHeight=128, bottomHeight=32, speed=32,
                           direction="Down", repeats=True)
        heights = []
        for _ in range(20):
            crusher.tick()
            heights.append(sector.ceilingHeight)
        self.assertIn(32, heights)
        self.assertTrue(crusher.tick())  # 크러셔는 절대 끝나지 않는다(항상 True).


class PlatformTest(unittest.TestCase):
    def test_lift_descends_then_stops(self):
        sector = Sector(64, 128, "F", "C", 160, 0, 0)
        lift = Platform(sector, lowHeight=0, highHeight=64, speed=16, direction="Down")
        while lift.tick():
            pass
        self.assertEqual(sector.floorHeight, 0)


class LightFlashTest(unittest.TestCase):
    def test_low_roll_picks_max_light(self):
        sector = Sector(0, 0, "F", "C", 160, 0, 0)
        flash = LightFlash(sector, maxLight=200, minLight=80, rng=lambda: 0.0, ticsUntilNextChange=1)
        flash.tick()
        self.assertEqual(sector.lightLevel, 200)

    def test_high_roll_picks_min_light(self):
        sector = Sector(0, 0, "F", "C", 160, 0, 0)
        flash = LightFlash(sector, maxLight=200, minLight=80, rng=lambda: 0.9, ticsUntilNextChange=1)
        flash.tick()
        self.assertEqual(sector.lightLevel, 80)


def _make_door_linedef(requiredKey=None):
    v1, v2 = Vertex(0, 0), Vertex(0, 64)
    frontSector = Sector(0, 0, "F", "C", 160, 0, 1)
    backSector = Sector(0, 0, "F", "C", 160, 0, 0)
    front = SideDef(0, 0, "-", "-", "-", frontSector)
    back = SideDef(0, 0, "-", "-", "-", backSector)
    line = LineDef(v1, v2, flags=0, special=1, tag=1, frontSide=front, backSide=back)
    return line, backSector


class LockedDoorTest(unittest.TestCase):
    """specials.md에 새로 추가한 requiredKey/잠긴 문 판정을 검증한다."""

    def test_locked_door_does_not_open_without_matching_key(self):
        line, sector = _make_door_linedef()
        active = []

        class Player:
            keys = []

        def make_mover(l):
            return Door(sector, "Open", targetCeilingHeight=128, requiredKey="blue")

        def is_locked_check(l):
            return Door(sector, "Open", targetCeilingHeight=128, requiredKey="blue")

        mover = trigger_line_special(line, "Use", Player(), active, make_mover, is_locked_check)
        self.assertIsNone(mover)
        self.assertEqual(active, [])
        self.assertNotEqual(line.special, 0)  # 다시 시도할 수 있게 special이 남아 있다.

    def test_locked_door_opens_with_matching_key(self):
        line, sector = _make_door_linedef()
        active = []

        class Player:
            keys = ["blue"]

        def make_mover(l):
            return Door(sector, "Open", targetCeilingHeight=128, requiredKey="blue")

        def is_locked_check(l):
            return Door(sector, "Open", targetCeilingHeight=128, requiredKey="blue")

        mover = trigger_line_special(line, "Use", Player(), active, make_mover, is_locked_check)
        self.assertIsNotNone(mover)
        self.assertEqual(active, [mover])


class SpecialsProgressTest(unittest.TestCase):
    """specials.md의 '## Feature: 특수 효과 진행' 검증."""

    def test_finished_movers_are_removed_still_active_kept(self):
        sectorA = Sector(0, 0, "F", "C", 160, 0, 0)
        sectorB = Sector(0, 0, "F", "C", 160, 0, 0)
        finished_soon = FloorMover(sectorA, targetFloorHeight=1, speed=1)
        long_running = FloorMover(sectorB, targetFloorHeight=100, speed=1)
        active = [finished_soon, long_running]
        active = advance_specials(active)
        self.assertIn(long_running, active)
        # finished_soon은 1 tic만에 목표(1)에 도달해 제거된다.
        self.assertNotIn(finished_soon, active)


if __name__ == "__main__":
    unittest.main()
