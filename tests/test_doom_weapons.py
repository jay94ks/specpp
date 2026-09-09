import unittest

from doom_weapons import WEAPON_TYPES, PlayerWeapon


class PistolExampleTest(unittest.TestCase):
    """weapons.md의 '## 예제: 권총 발사 한 번'을 그대로 옮긴 테스트."""

    def test_fire_cycles_through_attack_and_flash_back_to_ready(self):
        pistol = WEAPON_TYPES["pistol"]
        w = PlayerWeapon(pistol)
        self.assertIs(w.state, pistol.readyState)

        w.setState(pistol.attackState)
        for _ in range(pistol.attackState.duration):
            w.tick()
        self.assertIs(w.state, pistol.flashState)

        for _ in range(pistol.flashState.duration):
            w.tick()
        self.assertIs(w.state, pistol.readyState)


class WeaponRosterTest(unittest.TestCase):
    """weapons.md의 '## 전체 무기 로스터' 표 검증 — 탄약 종류·소비량·피해 공식."""

    def test_all_eight_weapons_present(self):
        expected = {"fist", "chainsaw", "pistol", "shotgun", "chaingun",
                    "rocketLauncher", "plasmaRifle", "bfg9000"}
        self.assertEqual(set(WEAPON_TYPES.keys()), expected)

    def test_fist_and_chainsaw_need_no_ammo(self):
        self.assertIsNone(WEAPON_TYPES["fist"].ammoType)
        self.assertIsNone(WEAPON_TYPES["chainsaw"].ammoType)

    def test_bullet_weapons_use_5_10_15_formula(self):
        for name in ("pistol", "chaingun"):
            wt = WEAPON_TYPES[name]
            for r in range(3):
                self.assertIn(wt.damage(lambda v=r: v), (5, 10, 15))

    def test_shotgun_fires_seven_pellets(self):
        # 펠릿 7발 * 최소 5 ~ 최대 15 사이.
        dmg = WEAPON_TYPES["shotgun"].damage(lambda: 0)
        self.assertEqual(dmg, 7 * 5)
        dmg_max = WEAPON_TYPES["shotgun"].damage(lambda: 2)
        self.assertEqual(dmg_max, 7 * 15)

    def test_bfg_costs_40_cells(self):
        self.assertEqual(WEAPON_TYPES["bfg9000"].ammoType, "cells")
        self.assertEqual(WEAPON_TYPES["bfg9000"].ammoPerShot, 40)

    def test_rocket_launcher_uses_rockets(self):
        self.assertEqual(WEAPON_TYPES["rocketLauncher"].ammoType, "rockets")
        self.assertEqual(WEAPON_TYPES["rocketLauncher"].ammoPerShot, 1)

    def test_bfg_hits_hardest_at_max_roll(self):
        bfg = WEAPON_TYPES["bfg9000"].damage(lambda: 700)
        rocket = WEAPON_TYPES["rocketLauncher"].damage(lambda: 132)
        self.assertGreater(bfg, rocket)


if __name__ == "__main__":
    unittest.main()
