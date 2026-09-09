// examples/doom/hud.md 검증 (C++17).
#include "doom_hud.hpp"
#include "minitest.hpp"

using namespace Doom;

TEST(hud_low_health_shows_hurt_face) {
    auto actor = Actor::Spawn(monsterTypes().at("Zombieman"), 0, 0);
    Player player(actor);
    player.health = 10;
    Hud hud;
    hud.updateFace(player);
    CHECK(hud.faceFrame.find("STFEVL") != std::string::npos);
}

TEST(hud_full_health_shows_calm_face) {
    auto actor = Actor::Spawn(monsterTypes().at("Zombieman"), 0, 0);
    Player player(actor);
    player.health = 100;
    Hud hud;
    hud.updateFace(player);
    CHECK(hud.faceFrame.find("STFST") != std::string::npos);
}

TEST(hud_zero_health_shows_dead_face) {
    auto actor = Actor::Spawn(monsterTypes().at("Zombieman"), 0, 0);
    Player player(actor);
    player.health = 0;
    Hud hud;
    hud.updateFace(player);
    CHECK_EQ(hud.faceFrame, std::string("STFDEAD0"));
}

TEST(hud_recent_hit_shows_directional_face) {
    auto actor = Actor::Spawn(monsterTypes().at("Zombieman"), 0, 0);
    Player player(actor);
    player.health = 80;
    Hud hud;
    hud.updateFace(player, std::optional<std::string>("left"));
    CHECK(hud.faceFrame.find("HIT_left") != std::string::npos);
}

TEST_MAIN()
