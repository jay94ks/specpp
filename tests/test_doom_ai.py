import unittest

from doom_actors import MF_SOLID, Actor, MONSTER_TYPES, Player
from doom_ai import (
    check_melee_range, check_missile_range, chase, face_target,
    has_line_of_sight, hitscan_attack, look_for_players, melee_attack,
    pain_and_death,
)
from doom_map import LineDef, Sector, SideDef, Vertex


def _solid_wall(x1, y1, x2, y2):
    sector = Sector(0, 0, "F", "C", 160, 0, 0)
    side = SideDef(0, 0, "-", "-", "WALL", sector)
    return LineDef(Vertex(x1, y1), Vertex(x2, y2), flags=0, special=0, tag=0,
                    frontSide=side, backSide=None)


class LineOfSightTest(unittest.TestCase):
    def test_open_space_has_sight(self):
        self.assertTrue(has_line_of_sight(0, 0, 100, 0, []))

    def test_wall_between_blocks_sight(self):
        wall = _solid_wall(50, -50, 50, 50)
        self.assertFalse(has_line_of_sight(0, 0, 100, 0, [wall]))

    def test_wall_off_to_the_side_does_not_block(self):
        wall = _solid_wall(50, 100, 50, 150)
        self.assertTrue(has_line_of_sight(0, 0, 100, 0, [wall]))


class LookForPlayersTest(unittest.TestCase):
    """ai.md의 '## Feature: 대기 중 플레이어 탐지 (A_Look)' 검증."""

    def test_visible_player_becomes_target_and_triggers_see_state(self):
        zombie = Actor.Spawn(MONSTER_TYPES["Zombieman"], 0, 0)
        playerActor = Actor.Spawn(MONSTER_TYPES["Zombieman"], 100, 0)
        player = Player(playerActor)
        found = look_for_players(zombie, [player], lineDefs=[])
        self.assertTrue(found)
        self.assertIs(zombie.target, playerActor)
        self.assertIs(zombie.state, zombie.type.seeState)

    def test_player_behind_wall_is_not_found(self):
        zombie = Actor.Spawn(MONSTER_TYPES["Zombieman"], 0, 0)
        playerActor = Actor.Spawn(MONSTER_TYPES["Zombieman"], 100, 0)
        player = Player(playerActor)
        wall = _solid_wall(50, -50, 50, 50)
        found = look_for_players(zombie, [player], lineDefs=[wall])
        self.assertFalse(found)
        self.assertIsNone(zombie.target)


class MeleeRangeTest(unittest.TestCase):
    def test_close_target_is_in_melee_range(self):
        demon = Actor.Spawn(MONSTER_TYPES["Demon"], 0, 0)
        demon.target = Actor.Spawn(MONSTER_TYPES["Zombieman"], 10, 0)
        self.assertTrue(check_melee_range(demon))

    def test_far_target_is_not_in_melee_range(self):
        demon = Actor.Spawn(MONSTER_TYPES["Demon"], 0, 0)
        demon.target = Actor.Spawn(MONSTER_TYPES["Zombieman"], 500, 0)
        self.assertFalse(check_melee_range(demon))

    def test_monster_without_melee_state_never_melees(self):
        zombie = Actor.Spawn(MONSTER_TYPES["Zombieman"], 0, 0)  # meleeState=None.
        zombie.target = Actor.Spawn(MONSTER_TYPES["Zombieman"], 5, 0)
        self.assertFalse(check_melee_range(zombie))


class FaceTargetTest(unittest.TestCase):
    def test_faces_directly_at_target(self):
        a = Actor.Spawn(MONSTER_TYPES["Imp"], 0, 0)
        a.target = Actor.Spawn(MONSTER_TYPES["Zombieman"], 0, 100)
        face_target(a)
        self.assertAlmostEqual(a.angle, 90.0)


class MeleeAttackTest(unittest.TestCase):
    """ai.md의 '## Feature: 근접 공격 판정' 검증."""

    def test_deals_damage_when_still_in_range(self):
        demon = Actor.Spawn(MONSTER_TYPES["Demon"], 0, 0)
        victim = Actor.Spawn(MONSTER_TYPES["Zombieman"], 10, 0)
        demon.target = victim
        dealt = []

        def deal_damage(target, damage, inflictor):
            dealt.append((target, damage, inflictor))
            target.health -= damage

        melee_attack(demon, lambda rng: 24, rng=lambda: 0, deal_damage=deal_damage)
        self.assertEqual(len(dealt), 1)
        self.assertIs(dealt[0][0], victim)
        self.assertEqual(dealt[0][1], 24)

    def test_no_damage_if_target_moved_away(self):
        demon = Actor.Spawn(MONSTER_TYPES["Demon"], 0, 0)
        victim = Actor.Spawn(MONSTER_TYPES["Zombieman"], 500, 0)
        demon.target = victim
        dealt = []
        melee_attack(demon, lambda rng: 24, rng=lambda: 0,
                      deal_damage=lambda t, d, i: dealt.append(t))
        self.assertEqual(dealt, [])


class PainAndDeathTest(unittest.TestCase):
    """ai.md의 '## Feature: 고통과 죽음 (A_Pain / A_Fall 계열)' 검증."""

    def test_health_above_zero_may_enter_pain_state(self):
        zombie = Actor.Spawn(MONSTER_TYPES["Zombieman"], 0, 0)
        zombie.health = 10
        result = pain_and_death(zombie, rng=lambda: 0.0)  # 항상 고통 확률을 넘긴다.
        self.assertEqual(result, "pain")
        self.assertIs(zombie.state, zombie.type.painState)

    def test_health_zero_enters_death_state_and_loses_solid(self):
        zombie = Actor.Spawn(MONSTER_TYPES["Zombieman"], 0, 0)
        zombie.health = 0
        result = pain_and_death(zombie, rng=lambda: 0.0)
        self.assertEqual(result, "death")
        self.assertIs(zombie.state, zombie.type.deathState)
        self.assertFalse(zombie.flags & MF_SOLID)


if __name__ == "__main__":
    unittest.main()
