import tempfile
import unittest

from doom_actors import MF_COUNTKILL, ITEM_TYPES, Actor
from doom_game import Game, check_map_exit, deal_damage, fire_weapon_input, move_and_collide, use_key
from doom_specials import Door
from doom_test_fixtures import MAP_NAME, build_two_room_map_wad
from doom_wad import WadFile


class DoomGameTestBase(unittest.TestCase):
    def setUp(self):
        f = tempfile.NamedTemporaryFile(suffix=".wad", delete=False)
        f.write(build_two_room_map_wad())
        f.close()
        self.wad = WadFile(f.name)
        self.game = Game.Start(self.wad, MAP_NAME, rng=lambda: 0.0)


class GameStartTest(DoomGameTestBase):
    def test_player_and_monster_spawned_from_things(self):
        self.assertIsNotNone(self.game.player)
        self.assertEqual((self.game.player.actor.x, self.game.player.actor.y), (16.0, 32.0))
        monsters = self.game.monsters()
        self.assertEqual(len(monsters), 1)
        self.assertEqual(monsters[0].type.name, "Zombieman")
        self.assertEqual(self.game.totalKills, 1)


class MovementAndCollisionExampleTest(DoomGameTestBase):
    """game.md의 '## 예제: 벽에 막힌 이동'을 옮긴 테스트."""

    def test_does_not_pass_through_impassable_wall(self):
        actor = self.game.player.actor
        actor.x, actor.y = 5.0, 5.0  # 서쪽 방 남쪽 벽(L0: V0(0,0)-V1(32,0)) 바로 앞.
        for _ in range(50):
            move_and_collide(self.game, actor, 0.0, -1.0)  # 남쪽 벽을 향해 계속 이동 시도.
        self.assertGreater(actor.y, 0.0)  # 벽(y=0)을 뚫고 나가지 않는다.

    def test_fully_blocked_move_does_not_raise_and_stays_put(self):
        actor = self.game.player.actor
        actor.x, actor.y = 1.0, 1.0
        try:
            for _ in range(20):
                move_and_collide(self.game, actor, -5.0, -5.0)
        except Exception as e:  # noqa: BLE001
            self.fail(f"이동이 막혔을 때 예외를 던지면 안 된다: {e}")
        self.assertGreaterEqual(actor.x, 0.0)
        self.assertGreaterEqual(actor.y, 0.0)

    def test_crossing_open_doorway_updates_sector(self):
        actor = self.game.player.actor
        self.game.actors = [actor]  # 이 테스트는 벽만 본다 — 몬스터와의 충돌은 별개 관심사.
        west = self.game.map.sectors[0]
        east = self.game.map.sectors[1]
        self.assertIs(actor.sector, west)
        for _ in range(10):
            move_and_collide(self.game, actor, 2.0, 0.0)  # 문(x=32)을 통과해 동쪽 방으로.
        self.assertIs(actor.sector, east)

    def test_blocked_by_another_solid_actor(self):
        actor = self.game.player.actor
        blocker = self.game.monsters()[0]
        blocker.x, blocker.y = actor.x + 20.0, actor.y  # 플레이어 바로 앞을 막는다.
        startX = actor.x
        for _ in range(10):
            move_and_collide(self.game, actor, 2.0, 0.0)
        self.assertLess(actor.x - startX, 20.0)  # blocker의 반경 안까지는 들어가지 못한다.


class CombatExampleTest(DoomGameTestBase):
    """game.md의 '## 예제: 체력이 다하면 처치 수가 오른다'를 그대로 옮긴 테스트."""

    def test_health_reaching_zero_increments_kill_count(self):
        target = self.game.monsters()[0]
        target.health = 5
        before = self.game.killCount
        deal_damage(self.game, target, damage=10)
        self.assertEqual(target.health, 0)
        self.assertIs(target.state, target.type.deathState)
        self.assertEqual(self.game.killCount, before + 1)

    def test_non_countkill_actor_does_not_increment_kills(self):
        import copy
        target = self.game.monsters()[0]
        # target.type은 MONSTER_TYPES 레지스트리가 공유하는 청사진이므로 직접 고치지
        # 않는다 — 이 Actor만을 위한 얕은 복사본을 만들어 flags만 바꾼다.
        target.type = copy.copy(target.type)
        target.type.flags &= ~MF_COUNTKILL
        deal_damage(self.game, target, damage=1000)
        self.assertEqual(self.game.killCount, 0)

    def test_armored_player_absorbs_partial_damage(self):
        player = self.game.player
        player.armor = 100
        player.armorClass = 1  # 초록 갑옷: 1/3을 갑옷이 흡수.
        deal_damage(self.game, player.actor, damage=30)
        self.assertEqual(player.health, 80)  # 30 중 10만큼 갑옷이 흡수.
        self.assertEqual(player.armor, 90)


class FireWeaponExampleTest(DoomGameTestBase):
    """game.md의 '## 예제: 탄약이 없으면 발사되지 않는다'를 그대로 옮긴 테스트."""

    def test_no_ammo_means_no_state_change(self):
        self.game.player.currentWeapon = "shotgun"
        self.game.player.ammo["shells"] = 0
        before = self.game.playerWeapon.state
        fired = fire_weapon_input(self.game)
        self.assertFalse(fired)
        self.assertIs(self.game.playerWeapon.state, before)

    def test_firing_consumes_ammo_and_changes_weapon_state(self):
        self.game.player.currentWeapon = "pistol"
        self.game.player.ammo["bullets"] = 5
        fired = fire_weapon_input(self.game)
        self.assertTrue(fired)
        self.assertEqual(self.game.player.ammo["bullets"], 4)
        self.assertIsNot(self.game.playerWeapon.state, self.game.playerWeapon.type.readyState)

    def test_firing_hits_actor_in_crosshair(self):
        actor = self.game.player.actor
        target = self.game.monsters()[0]
        actor.x, actor.y, actor.angle = target.x - 10, target.y, 0.0
        healthBefore = target.health
        self.game.player.currentWeapon = "pistol"
        self.game.player.ammo["bullets"] = 5
        fire_weapon_input(self.game)
        self.assertLess(target.health, healthBefore)


class UseKeyTest(DoomGameTestBase):
    """game.md의 '## Feature: 사용 키 처리' 검증."""

    def test_use_triggers_special_on_facing_line(self):
        actor = self.game.player.actor
        middleLine = self.game.map.lineDefs[1]  # L1: 두 방 사이 문, x=32.
        middleLine.special = 1  # "문 열기" 특수 효과가 걸려 있다고 가정한다.
        actor.x, actor.y, actor.angle = 20.0, 32.0, 0.0  # 문을 정면으로 바라본다.

        def make_mover(line):
            return Door(line.backSide.sector, "Open", targetCeilingHeight=96, speed=64)

        mover = use_key(self.game, make_mover=make_mover)
        self.assertIsNotNone(mover)
        self.assertIn(mover, self.game.specials)
        self.assertEqual(middleLine.special, 0)  # 한 번 쓰고 나면 다시 발동하지 않는다.


class ItemPickupTest(DoomGameTestBase):
    """game.md의 '## Feature: 아이템 획득' 검증."""

    def _spawn_item(self, name, x, y):
        item = Actor.Spawn(ITEM_TYPES[name], x, y, 0, self.game.player.actor.sector)
        item.itemName = name
        self.game.actors.append(item)
        return item

    def test_touching_stimpack_heals_and_removes_it(self):
        actor = self.game.player.actor
        self.game.player.health = 80
        item = self._spawn_item("Stimpack", actor.x, actor.y)
        move_and_collide(self.game, actor, 0.0, 0.0)
        self.assertEqual(self.game.player.health, 90)
        self.assertTrue(item.isRemoved)
        self.assertEqual(self.game.itemCount, 1)

    def test_item_out_of_range_is_not_picked_up(self):
        actor = self.game.player.actor
        self.game.player.health = 80
        item = self._spawn_item("Stimpack", actor.x + 500, actor.y)
        move_and_collide(self.game, actor, 0.0, 0.0)
        self.assertEqual(self.game.player.health, 80)
        self.assertFalse(item.isRemoved)

    def test_items_do_not_block_movement(self):
        actor = self.game.player.actor
        self.game.actors = [actor]  # 몬스터와의 충돌은 이 테스트의 관심사가 아니다.
        self._spawn_item("Green Armor", actor.x + 2.0, actor.y)
        moved = move_and_collide(self.game, actor, 2.0, 0.0)
        self.assertTrue(moved)  # MF_SOLID가 없는 아이템은 통과할 수 있다.

    def test_monster_does_not_pick_up_items(self):
        monster = self.game.monsters()[0]
        item = self._spawn_item("Medikit", monster.x, monster.y)
        move_and_collide(self.game, monster, 0.0, 0.0)
        self.assertFalse(item.isRemoved)  # 몬스터는 아이템을 줍지 않는다.


class MapExitTest(DoomGameTestBase):
    """game.md의 '## Feature: 맵 종료 조건' 검증."""

    def test_exit_special_ends_the_map(self):
        exitLine = self.game.map.lineDefs[3]
        exitLine.special = 11
        result = check_map_exit(self.game, exitLine)
        self.assertTrue(result)
        self.assertTrue(self.game.exited)

    def test_non_exit_special_does_not_end_the_map(self):
        line = self.game.map.lineDefs[1]
        line.special = 1  # 문 특수 효과(11이 아님).
        result = check_map_exit(self.game, line)
        self.assertFalse(result)
        self.assertFalse(self.game.exited)


class TickIntegrationTest(DoomGameTestBase):
    """game.md의 '## Feature: 틱 진행' 전체 루프가 오류 없이 도는지 확인한다."""

    def test_full_tick_runs_without_error_and_advances_tic_counter(self):
        for _ in range(35):  # 1초 분량.
            self.game.tick({"forwardMove": 10, "sideMove": 0, "angleTurn": 1, "buttons": 0})
        self.assertEqual(self.game.tic, 35)

    def test_menu_open_freezes_simulation(self):
        from doom_menu import Menu
        self.game.menuStack.open(Menu("Main", []))
        ticBefore = self.game.tic
        self.game.tick({"forwardMove": 50, "sideMove": 0, "angleTurn": 0, "buttons": 0})
        self.assertEqual(self.game.tic, ticBefore)


if __name__ == "__main__":
    unittest.main()
