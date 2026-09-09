// examples/doom/ai.md 검증 (C++17).
#include "doom_ai.hpp"
#include "minitest.hpp"

using namespace Doom;
using namespace Doom::Map;

static LineDef* makeSolidWall(std::vector<std::unique_ptr<Vertex>>& vstore,
                               std::vector<std::unique_ptr<Sector>>& sstore,
                               std::vector<std::unique_ptr<SideDef>>& sdstore,
                               std::vector<std::unique_ptr<LineDef>>& lstore,
                               float x1, float y1, float x2, float y2) {
    vstore.push_back(std::make_unique<Vertex>(Vertex{x1, y1}));
    vstore.push_back(std::make_unique<Vertex>(Vertex{x2, y2}));
    sstore.push_back(std::make_unique<Sector>(Sector{0, 0, "F", "C", 160, 0, 0}));
    sdstore.push_back(std::make_unique<SideDef>(SideDef{0, 0, "-", "-", "WALL", sstore.back().get()}));
    lstore.push_back(std::make_unique<LineDef>(
        LineDef{vstore[vstore.size() - 2].get(), vstore.back().get(), 0, 0, 0, sdstore.back().get(), nullptr}));
    return lstore.back().get();
}

TEST(los_open_space_has_sight) {
    std::vector<LineDef*> none;
    CHECK(hasLineOfSight(0, 0, 100, 0, none));
}

TEST(los_wall_between_blocks_sight) {
    std::vector<std::unique_ptr<Vertex>> vs; std::vector<std::unique_ptr<Sector>> ss;
    std::vector<std::unique_ptr<SideDef>> sds; std::vector<std::unique_ptr<LineDef>> ls;
    auto* wall = makeSolidWall(vs, ss, sds, ls, 50, -50, 50, 50);
    std::vector<LineDef*> lines = {wall};
    CHECK(!hasLineOfSight(0, 0, 100, 0, lines));
}

TEST(los_wall_off_to_the_side_does_not_block) {
    std::vector<std::unique_ptr<Vertex>> vs; std::vector<std::unique_ptr<Sector>> ss;
    std::vector<std::unique_ptr<SideDef>> sds; std::vector<std::unique_ptr<LineDef>> ls;
    auto* wall = makeSolidWall(vs, ss, sds, ls, 50, 100, 50, 150);
    std::vector<LineDef*> lines = {wall};
    CHECK(hasLineOfSight(0, 0, 100, 0, lines));
}

TEST(look_for_players_visible_becomes_target) {
    auto zombie = Actor::Spawn(monsterTypes().at("Zombieman"), 0, 0);
    auto playerActor = Actor::Spawn(monsterTypes().at("Zombieman"), 100, 0);
    Player player(playerActor);
    std::vector<LineDef*> none;
    std::vector<Player*> players = {&player};
    bool found = lookForPlayers(zombie.get(), players, none);
    CHECK(found);
    CHECK(zombie->target == playerActor.get());
    CHECK(zombie->state == zombie->type->seeState);
}

TEST(look_for_players_blocked_by_wall_not_found) {
    std::vector<std::unique_ptr<Vertex>> vs; std::vector<std::unique_ptr<Sector>> ss;
    std::vector<std::unique_ptr<SideDef>> sds; std::vector<std::unique_ptr<LineDef>> ls;
    auto* wall = makeSolidWall(vs, ss, sds, ls, 50, -50, 50, 50);
    auto zombie = Actor::Spawn(monsterTypes().at("Zombieman"), 0, 0);
    auto playerActor = Actor::Spawn(monsterTypes().at("Zombieman"), 100, 0);
    Player player(playerActor);
    std::vector<LineDef*> lines = {wall};
    std::vector<Player*> players = {&player};
    CHECK(!lookForPlayers(zombie.get(), players, lines));
    CHECK(zombie->target == nullptr);
}

TEST(melee_range_close_target) {
    auto demon = Actor::Spawn(monsterTypes().at("Demon"), 0, 0);
    auto victim = Actor::Spawn(monsterTypes().at("Zombieman"), 10, 0);
    demon->target = victim.get();
    CHECK(checkMeleeRange(demon.get()));
}

TEST(melee_range_far_target) {
    auto demon = Actor::Spawn(monsterTypes().at("Demon"), 0, 0);
    auto victim = Actor::Spawn(monsterTypes().at("Zombieman"), 500, 0);
    demon->target = victim.get();
    CHECK(!checkMeleeRange(demon.get()));
}

TEST(face_target_points_directly_at_target) {
    auto a = Actor::Spawn(monsterTypes().at("Imp"), 0, 0);
    auto t = Actor::Spawn(monsterTypes().at("Zombieman"), 0, 100);
    a->target = t.get();
    faceTarget(a.get());
    CHECK(std::abs(a->angle - 90.0f) < 0.001f);
}

TEST(melee_attack_deals_damage_when_in_range) {
    auto demon = Actor::Spawn(monsterTypes().at("Demon"), 0, 0);
    auto victim = Actor::Spawn(monsterTypes().at("Zombieman"), 10, 0);
    demon->target = victim.get();
    int dealtDamage = -1;
    meleeAttack(demon.get(), [](std::function<int()>) { return 24; }, [] { return 0; },
                [&](Actor* t, int d, Actor*) { dealtDamage = d; t->health -= d; });
    CHECK_EQ(dealtDamage, 24);
}

TEST(pain_and_death_high_health_may_pain) {
    auto zombie = Actor::Spawn(monsterTypes().at("Zombieman"), 0, 0);
    zombie->health = 10;
    auto result = painAndDeath(zombie.get(), [] { return 0.0; });
    CHECK_EQ(result, std::string("pain"));
    CHECK(zombie->state == zombie->type->painState);
}

TEST(pain_and_death_zero_health_dies_and_loses_solid) {
    auto zombie = Actor::Spawn(monsterTypes().at("Zombieman"), 0, 0);
    zombie->health = 0;
    auto result = painAndDeath(zombie.get(), [] { return 0.0; });
    CHECK_EQ(result, std::string("death"));
    CHECK(zombie->state == zombie->type->deathState);
    CHECK((zombie->flags & MF_SOLID) == 0);
}

TEST_MAIN()
