// examples/doom/actors.md 검증 (C++17).
#include "doom_actors.hpp"
#include "minitest.hpp"

using namespace Doom;

TEST(zombieman_settles_into_final_death_frame) {
    auto z = Actor::Spawn(monsterTypes().at("Zombieman"), 100, 200, 0, nullptr);
    z->setState(z->type->deathState);
    for (int i = 0; i < 5; i++) z->tick();
    CHECK_EQ(z->state->duration, -1);
    State* before = z->state;
    for (int i = 0; i < 10; i++) z->tick();
    CHECK(z->state == before);
}

TEST(actor_required_set_state_null_removes_actor) {
    auto z = Actor::Spawn(monsterTypes().at("Zombieman"), 0, 0);
    z->setState(nullptr);
    CHECK(z->removed);
}

TEST(actor_required_tick_exactly_duration_times_advances_state) {
    auto z = Actor::Spawn(monsterTypes().at("Zombieman"), 0, 0);
    State* original = z->state;
    for (int i = 0; i < original->duration; i++) z->tick();
    CHECK(z->state == original->nextState);
}

TEST(actor_required_infinite_duration_never_advances) {
    State forever{"XXXX", 0, -1, nullptr, nullptr};
    Actor a;
    a.state = &forever;
    a.ticsRemaining = -1;
    for (int i = 0; i < 1000; i++) a.tick();
    CHECK(a.state == &forever);
}

TEST(monster_roster_has_all_18_with_correct_doomednum) {
    static const std::map<std::string, int> expected = {
        {"Zombieman", 3004}, {"Shotgun Guy", 9}, {"Chaingunner", 65},
        {"Wolfenstein SS", 84}, {"Imp", 3001}, {"Demon", 3002}, {"Spectre", 58},
        {"Lost Soul", 3006}, {"Cacodemon", 3005}, {"Hell Knight", 69},
        {"Baron of Hell", 3003}, {"Arachnotron", 68}, {"Pain Elemental", 71},
        {"Revenant", 66}, {"Mancubus", 67}, {"Arch-vile", 64},
        {"Spider Mastermind", 7}, {"Cyberdemon", 16},
    };
    CHECK_EQ(monsterTypes().size(), 18u);
    for (auto& [name, doomednum] : expected) {
        CHECK(monsterTypes().count(name) == 1);
        CHECK_EQ(monsterTypes().at(name)->doomednum, doomednum);
    }
}

TEST(monster_roster_all_are_shootable_and_countkill) {
    for (auto& [name, type] : monsterTypes()) {
        CHECK((type->flags & MF_SOLID) != 0);
        CHECK((type->flags & MF_COUNTKILL) != 0);
    }
}

TEST(spectre_matches_demon_stats_plus_shadow) {
    auto demon = monsterTypes().at("Demon");
    auto spectre = monsterTypes().at("Spectre");
    CHECK_EQ(demon->spawnHealth, spectre->spawnHealth);
    CHECK_EQ(demon->radius, spectre->radius);
    CHECK((demon->flags & MF_SHADOW) == 0);
    CHECK((spectre->flags & MF_SHADOW) != 0);
}

TEST(cyberdemon_is_the_toughest) {
    auto cyber = monsterTypes().at("Cyberdemon");
    CHECK_EQ(cyber->spawnHealth, 4000);
    for (auto& [name, type] : monsterTypes()) CHECK(cyber->spawnHealth >= type->spawnHealth);
}

TEST(item_roster_has_34_entries) {
    CHECK_EQ(itemPickups().size(), 34u);
}

TEST(item_stimpack_heals_ten_capped_at_100) {
    Player p(nullptr);
    p.health = 95;
    findItemByName("Stimpack")->apply(p);
    CHECK_EQ(p.health, 100);
}

TEST(item_soulsphere_can_exceed_100_up_to_200) {
    Player p(nullptr);
    p.health = 150;
    findItemByName("Soulsphere")->apply(p);
    CHECK_EQ(p.health, 200);
}

TEST(item_blue_armor_sets_class_2) {
    Player p(nullptr);
    findItemByName("Blue Armor")->apply(p);
    CHECK_EQ(p.armor, 200);
    CHECK_EQ(p.armorClass, 2);
}

TEST(item_card_and_skull_key_interchangeable_by_color) {
    Player p(nullptr);
    findItemByName("Blue Keycard")->apply(p);
    findItemByName("Blue Skull Key")->apply(p);
    CHECK_EQ(int(std::count(p.keys.begin(), p.keys.end(), "blue")), 1);
}

TEST(item_backpack_adds_ammo_of_every_kind) {
    Player p(nullptr);
    auto before = p.ammo;
    findItemByName("Backpack")->apply(p);
    for (auto& kind : {"bullets", "shells", "rockets", "cells"}) CHECK(p.ammo[kind] > before[kind]);
}

TEST(item_no_doomednum_collides_with_monster) {
    for (auto& item : itemPickups()) {
        for (auto& [name, type] : monsterTypes()) {
            CHECK(item.doomednum != type->doomednum);
        }
    }
}

TEST(item_berserk_heals_and_never_expires) {
    Player p(nullptr);
    p.health = 40;
    findItemByName("Berserk")->apply(p);
    CHECK_EQ(p.health, 100);
    CHECK_EQ(p.powerups["berserk"], -1);
}

TEST(projectile_imp_fireball_damage_range) {
    auto imp = findProjectileByName("Imp Fireball");
    for (int r = 0; r < 8; r++) {
        int dmg = imp->damage([r] { return r; });
        CHECK(dmg >= 3 && dmg <= 24);
    }
}

TEST(projectile_baron_hits_harder_than_imp) {
    auto imp = findProjectileByName("Imp Fireball");
    auto baron = findProjectileByName("Baron Fireball");
    CHECK(baron->damage([] { return 7; }) > imp->damage([] { return 7; }));
}

TEST(projectile_arachnotron_plasma_is_fixed_damage) {
    auto plasma = findProjectileByName("Arachnotron Plasma");
    CHECK_EQ(plasma->damage([] { return 0; }), 5);
    CHECK_EQ(plasma->damage([] { return 7; }), 5);
}

TEST(archvile_finds_and_resurrects_dead_monster) {
    auto archvile = Actor::Spawn(monsterTypes().at("Arch-vile"), 0, 0);
    auto zombie = Actor::Spawn(monsterTypes().at("Zombieman"), 50, 0);
    zombie->health = 0;
    zombie->setState(zombie->type->deathState);
    for (int i = 0; i < zombie->type->deathState->duration; i++) zombie->tick();
    CHECK(zombie->state == zombie->type->deathState->nextState);

    std::vector<std::shared_ptr<Actor>> actors = {archvile, zombie};
    Actor* found = findResurrectable(archvile.get(), actors);
    CHECK(found == zombie.get());

    resurrect(found);
    CHECK_EQ(zombie->health, zombie->type->spawnHealth);
    CHECK((zombie->flags & MF_SOLID) != 0);
}

TEST(archvile_does_not_resurrect_still_alive_monster) {
    auto archvile = Actor::Spawn(monsterTypes().at("Arch-vile"), 0, 0);
    auto zombie = Actor::Spawn(monsterTypes().at("Zombieman"), 50, 0);
    std::vector<std::shared_ptr<Actor>> actors = {archvile, zombie};
    CHECK(findResurrectable(archvile.get(), actors) == nullptr);
}

TEST_MAIN()
