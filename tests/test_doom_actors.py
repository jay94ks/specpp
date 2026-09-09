import unittest

from doom_actors import (
    Actor, ITEM_PICKUPS, MF_COUNTKILL, MF_SHADOW, MF_SOLID, MONSTER_TYPES,
    PROJECTILE_TYPES, Player, State, find_resurrectable, resurrect,
)


class ZombiemanExampleTest(unittest.TestCase):
    """actors.md의 '## 예제: Zombieman의 상태 기계'를 그대로 옮긴 테스트."""

    def test_actor_settles_into_final_death_frame(self):
        z = Actor.Spawn(MONSTER_TYPES["Zombieman"], 100, 200, 0, sector=None)
        z.setState(z.type.deathState)
        for _ in range(5):
            z.tick()
        self.assertEqual(z.state.duration, -1)
        stateBefore = z.state
        for _ in range(10):
            z.tick()
        self.assertIs(z.state, stateBefore)


class ActorRequiredTest(unittest.TestCase):
    """actors.md의 test_required Doom.Actor 블록을 그대로 옮긴 테스트."""

    def test_set_state_none_removes_actor(self):
        z = Actor.Spawn(MONSTER_TYPES["Zombieman"], 0, 0)
        z.setState(None)
        self.assertTrue(z.isRemoved)

    def test_tick_exactly_duration_times_advances_state(self):
        z = Actor.Spawn(MONSTER_TYPES["Zombieman"], 0, 0)
        original = z.state
        for _ in range(original.duration):
            z.tick()
        self.assertIs(z.state, original.nextState)

    def test_infinite_duration_never_advances(self):
        forever = State("XXXX", 0, -1, nextState=None)
        a = Actor()
        a.state = forever
        a.ticsRemaining = -1
        a.x = a.y = a.z = a.momX = a.momY = a.momZ = 0.0
        for _ in range(1000):
            a.tick()
        self.assertIs(a.state, forever)


class MonsterRosterTest(unittest.TestCase):
    """actors.md의 '## 전체 몬스터 로스터' 표가 실제로 다 채워졌는지 검증한다."""

    EXPECTED = {
        "Zombieman": 3004, "Shotgun Guy": 9, "Chaingunner": 65,
        "Wolfenstein SS": 84, "Imp": 3001, "Demon": 3002, "Spectre": 58,
        "Lost Soul": 3006, "Cacodemon": 3005, "Hell Knight": 69,
        "Baron of Hell": 3003, "Arachnotron": 68, "Pain Elemental": 71,
        "Revenant": 66, "Mancubus": 67, "Arch-vile": 64,
        "Spider Mastermind": 7, "Cyberdemon": 16,
    }

    def test_all_18_monsters_present_with_correct_doomednum(self):
        self.assertEqual(len(MONSTER_TYPES), 18)
        for name, doomednum in self.EXPECTED.items():
            self.assertIn(name, MONSTER_TYPES)
            self.assertEqual(MONSTER_TYPES[name].doomednum, doomednum)

    def test_all_monsters_are_shootable_and_countkill(self):
        for name, mtype in MONSTER_TYPES.items():
            self.assertTrue(mtype.flags & MF_SOLID, name)
            self.assertTrue(mtype.flags & MF_COUNTKILL, name)

    def test_spectre_matches_demon_stats_plus_shadow(self):
        demon = MONSTER_TYPES["Demon"]
        spectre = MONSTER_TYPES["Spectre"]
        self.assertEqual(demon.spawnHealth, spectre.spawnHealth)
        self.assertEqual(demon.radius, spectre.radius)
        self.assertEqual(demon.speed, spectre.speed)
        self.assertFalse(demon.flags & MF_SHADOW)
        self.assertTrue(spectre.flags & MF_SHADOW)

    def test_cyberdemon_is_the_toughest(self):
        cyber = MONSTER_TYPES["Cyberdemon"]
        self.assertEqual(cyber.spawnHealth, 4000)
        self.assertTrue(all(cyber.spawnHealth >= m.spawnHealth for m in MONSTER_TYPES.values()))


class ItemRosterTest(unittest.TestCase):
    """actors.md의 '## 아이템 로스터 (픽업)' 표 검증."""

    def test_expected_item_count(self):
        self.assertEqual(len(ITEM_PICKUPS), 34)

    def test_stimpack_heals_ten_capped_at_100(self):
        player = Player(actor=None)
        player.health = 95
        ITEM_PICKUPS["Stimpack"]["apply"](player)
        self.assertEqual(player.health, 100)

    def test_soulsphere_can_exceed_100_up_to_200(self):
        player = Player(actor=None)
        player.health = 150
        ITEM_PICKUPS["Soulsphere"]["apply"](player)
        self.assertEqual(player.health, 200)

    def test_blue_armor_sets_class_2(self):
        player = Player(actor=None)
        ITEM_PICKUPS["Blue Armor"]["apply"](player)
        self.assertEqual(player.armor, 200)
        self.assertEqual(player.armorClass, 2)

    def test_card_and_skull_key_are_interchangeable_by_color(self):
        player = Player(actor=None)
        ITEM_PICKUPS["Blue Keycard"]["apply"](player)
        ITEM_PICKUPS["Blue Skull Key"]["apply"](player)
        self.assertEqual(player.keys.count("blue"), 1)

    def test_backpack_adds_ammo_of_every_kind(self):
        player = Player(actor=None)
        before = dict(player.ammo)
        ITEM_PICKUPS["Backpack"]["apply"](player)
        for kind in ("bullets", "shells", "rockets", "cells"):
            self.assertGreater(player.ammo[kind], before[kind])

    def test_weapon_pickup_switches_current_weapon(self):
        player = Player(actor=None)
        ITEM_PICKUPS["Rocket Launcher"]["apply"](player)
        self.assertEqual(player.currentWeapon, "rocketLauncher")

    def test_berserk_heals_and_never_expires(self):
        player = Player(actor=None)
        player.health = 40
        ITEM_PICKUPS["Berserk"]["apply"](player)
        self.assertEqual(player.health, 100)
        self.assertEqual(player.powerups["berserk"], -1)

    def test_invulnerability_sets_a_30_second_timer(self):
        player = Player(actor=None)
        ITEM_PICKUPS["Invulnerability"]["apply"](player)
        self.assertEqual(player.powerups["invulnerability"], 30 * 35)

    def test_no_doomednum_collides_with_a_monster(self):
        monster_ids = {m.doomednum for m in MONSTER_TYPES.values()}
        item_ids = {v["doomednum"] for v in ITEM_PICKUPS.values()}
        self.assertEqual(monster_ids & item_ids, set())


class ProjectileRosterTest(unittest.TestCase):
    """actors.md의 '## 발사체 로스터' 표: 피해 공식이 문서화된 범위 안에 있는지 확인."""

    def test_imp_fireball_damage_range(self):
        dmg = PROJECTILE_TYPES["Imp Fireball"]["damage"]
        for rngVal in range(8):
            self.assertTrue(3 <= dmg(lambda v=rngVal: v) <= 24)

    def test_baron_fireball_hits_harder_than_imp(self):
        impMax = PROJECTILE_TYPES["Imp Fireball"]["damage"](lambda: 7)
        baronMax = PROJECTILE_TYPES["Baron Fireball"]["damage"](lambda: 7)
        self.assertGreater(baronMax, impMax)

    def test_arachnotron_plasma_is_fixed_damage(self):
        dmg = PROJECTILE_TYPES["Arachnotron Plasma"]["damage"]
        self.assertEqual(dmg(lambda: 0), 5)
        self.assertEqual(dmg(lambda: 7), 5)


class ArchvileResurrectionTest(unittest.TestCase):
    """actors.md의 '## Feature: 되살리기 (Arch-vile 전용)' 검증."""

    def test_finds_and_resurrects_dead_monster(self):
        archvile = Actor.Spawn(MONSTER_TYPES["Arch-vile"], 0, 0)
        zombie = Actor.Spawn(MONSTER_TYPES["Zombieman"], 50, 0)
        zombie.health = 0
        zombie.setState(zombie.type.deathState)
        zombie.tick()  # 마지막(무한) 죽음 프레임까지 보낸다.
        for _ in range(zombie.type.deathState.duration):
            zombie.tick()
        self.assertIs(zombie.state, zombie.type.deathState.nextState)

        found = find_resurrectable(archvile, [archvile, zombie])
        self.assertIs(found, zombie)

        resurrect(found)
        self.assertEqual(zombie.health, zombie.type.spawnHealth)
        self.assertTrue(zombie.flags & MF_SOLID)

    def test_does_not_resurrect_still_alive_monster(self):
        archvile = Actor.Spawn(MONSTER_TYPES["Arch-vile"], 0, 0)
        zombie = Actor.Spawn(MONSTER_TYPES["Zombieman"], 50, 0)
        found = find_resurrectable(archvile, [archvile, zombie])
        self.assertIsNone(found)


if __name__ == "__main__":
    unittest.main()
