// examples/doom/weapons.md 검증 (C++17).
#include "doom_weapons.hpp"
#include "minitest.hpp"

using namespace Doom;

TEST(pistol_fire_cycles_through_attack_and_flash_back_to_ready) {
    auto pistol = weaponTypes().at("pistol");
    PlayerWeapon w(pistol);
    CHECK(w.state == pistol->readyState);

    w.setState(pistol->attackState);
    for (int i = 0; i < pistol->attackState->duration; i++) w.tick();
    CHECK(w.state == pistol->flashState);

    for (int i = 0; i < pistol->flashState->duration; i++) w.tick();
    CHECK(w.state == pistol->readyState);
}

TEST(weapon_roster_has_all_8) {
    static const char* expected[] = {"fist", "chainsaw", "pistol", "shotgun",
                                      "chaingun", "rocketLauncher", "plasmaRifle", "bfg9000"};
    CHECK_EQ(weaponTypes().size(), 8u);
    for (auto name : expected) CHECK(weaponTypes().count(name) == 1);
}

TEST(fist_and_chainsaw_need_no_ammo) {
    CHECK(weaponTypes().at("fist")->ammoType.empty());
    CHECK(weaponTypes().at("chainsaw")->ammoType.empty());
}

TEST(bullet_weapons_use_5_10_15_formula) {
    for (auto name : {"pistol", "chaingun"}) {
        auto wt = weaponTypes().at(name);
        for (int r = 0; r < 3; r++) {
            int dmg = wt->damage([r] { return r; });
            CHECK(dmg == 5 || dmg == 10 || dmg == 15);
        }
    }
}

TEST(shotgun_fires_seven_pellets) {
    auto shotgun = weaponTypes().at("shotgun");
    CHECK_EQ(shotgun->damage([] { return 0; }), 7 * 5);
    CHECK_EQ(shotgun->damage([] { return 2; }), 7 * 15);
}

TEST(bfg_costs_40_cells) {
    auto bfg = weaponTypes().at("bfg9000");
    CHECK_EQ(bfg->ammoType, "cells");
    CHECK_EQ(bfg->ammoPerShot, 40);
}

TEST(bfg_hits_hardest_at_max_roll) {
    int bfg = weaponTypes().at("bfg9000")->damage([] { return 700; });
    int rocket = weaponTypes().at("rocketLauncher")->damage([] { return 132; });
    CHECK(bfg > rocket);
}

TEST_MAIN()
