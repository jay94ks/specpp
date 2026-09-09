// examples/doom/game.md 검증 (C++17).
#include "doom_game.hpp"
#include "doom_test_fixtures.hpp"
#include "minitest.hpp"
#include <fstream>

using namespace Doom;

static std::string writeFixtureWad(const char* suffix) {
    auto bytes = DoomFixtures::buildTwoRoomMapWad();
    std::string path = std::string("tmp_game_test") + suffix + ".wad";
    std::ofstream f(path, std::ios::binary);
    f.write(reinterpret_cast<const char*>(bytes.data()), bytes.size());
    return path;
}

static std::shared_ptr<Game> startGame(std::unique_ptr<WadFile>& wadOut, const char* suffix) {
    auto path = writeFixtureWad(suffix);
    wadOut = std::make_unique<WadFile>(path);
    return Game::Start(*wadOut, DoomFixtures::MAP_NAME, [] { return 0.0; });
}

TEST(game_start_spawns_player_and_monster_from_things) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_1");
    CHECK(game->player != nullptr);
    CHECK_EQ(game->player->actor->x, 16.0f);
    CHECK_EQ(game->player->actor->y, 32.0f);
    auto monsters = game->monsters();
    CHECK_EQ(monsters.size(), 1u);
    CHECK_EQ(monsters[0]->type->name, std::string("Zombieman"));
    CHECK_EQ(game->totalKills, 1);
}

TEST(movement_does_not_pass_through_impassable_wall) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_2");
    Actor* actor = game->player->actor.get();
    actor->x = 5.0f; actor->y = 5.0f;
    for (int i = 0; i < 50; i++) game->moveAndCollide(actor, 0.0f, -1.0f);
    CHECK(actor->y > 0.0f);
}

TEST(movement_fully_blocked_stays_put_without_crashing) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_3");
    Actor* actor = game->player->actor.get();
    actor->x = 1.0f; actor->y = 1.0f;
    for (int i = 0; i < 20; i++) game->moveAndCollide(actor, -5.0f, -5.0f);
    CHECK(actor->x >= 0.0f);
    CHECK(actor->y >= 0.0f);
}

TEST(movement_crossing_doorway_updates_sector) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_4");
    Actor* actor = game->player->actor.get();
    game->actors = {game->player->actor};  // 이 테스트는 벽만 본다.
    auto* west = game->map.sectors[0];
    auto* east = game->map.sectors[1];
    CHECK(actor->sector == west);
    for (int i = 0; i < 10; i++) game->moveAndCollide(actor, 2.0f, 0.0f);
    CHECK(actor->sector == east);
}

TEST(movement_blocked_by_another_solid_actor) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_5");
    Actor* actor = game->player->actor.get();
    Actor* blocker = game->monsters()[0];
    blocker->x = actor->x + 20.0f;
    blocker->y = actor->y;
    float startX = actor->x;
    for (int i = 0; i < 10; i++) game->moveAndCollide(actor, 2.0f, 0.0f);
    CHECK(actor->x - startX < 20.0f);
}

TEST(combat_health_reaching_zero_increments_kill_count) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_6");
    Actor* target = game->monsters()[0];
    target->health = 5;
    int before = game->killCount;
    game->dealDamage(target, 10);
    CHECK_EQ(target->health, 0);
    CHECK(target->state == target->type->deathState);
    CHECK_EQ(game->killCount, before + 1);
}

TEST(combat_non_countkill_actor_does_not_increment_kills) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_7");
    // monsterTypes() 레지스트리의 공유 MobjType은 건드리지 않는다 — MF_COUNTKILL이
    // 없는 전용 MobjType(예: 파괴 가능한 소품)을 새로 만들어 스폰한다.
    auto propType = std::make_shared<MobjType>();
    propType->name = "Barrel";
    propType->spawnHealth = 10;
    propType->radius = 10; propType->height = 32; propType->speed = 0;
    propType->flags = MF_SOLID | MF_SHOOTABLE;  // MF_COUNTKILL 없음.
    propType->spawnState = propType->addState("BAR1", 0, -1);
    auto target = Actor::Spawn(propType, 200, 200);
    game->actors.push_back(target);
    game->dealDamage(target.get(), 1000);
    CHECK_EQ(game->killCount, 0);
}

TEST(combat_armored_player_absorbs_partial_damage) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_8");
    game->player->armor = 100;
    game->player->armorClass = 1;  // 초록 갑옷: 1/3 흡수.
    game->dealDamage(game->player->actor.get(), 30);
    CHECK_EQ(game->player->health, 80);
    CHECK_EQ(game->player->armor, 90);
}

TEST(fire_weapon_no_ammo_means_no_state_change) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_9");
    game->player->currentWeapon = "shotgun";
    game->player->ammo["shells"] = 0;
    State* before = game->playerWeapon->state;
    bool fired = game->fireWeaponInput();
    CHECK(!fired);
    CHECK(game->playerWeapon->state == before);
}

TEST(fire_weapon_consumes_ammo_and_changes_state) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_10");
    game->player->currentWeapon = "pistol";
    game->player->ammo["bullets"] = 5;
    bool fired = game->fireWeaponInput();
    CHECK(fired);
    CHECK_EQ(game->player->ammo["bullets"], 4);
    CHECK(game->playerWeapon->state != game->playerWeapon->type->readyState);
}

TEST(fire_weapon_hits_actor_in_crosshair) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_11");
    Actor* actor = game->player->actor.get();
    Actor* target = game->monsters()[0];
    actor->x = target->x - 10.0f;
    actor->y = target->y;
    actor->angle = 0.0f;
    int healthBefore = target->health;
    game->player->currentWeapon = "pistol";
    game->player->ammo["bullets"] = 5;
    game->fireWeaponInput();
    CHECK(target->health < healthBefore);
}

TEST(use_key_triggers_special_on_facing_line) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_12");
    Actor* actor = game->player->actor.get();
    Map::LineDef* middleLine = game->map.lineDefs[1];
    middleLine->special = 1;
    actor->x = 20.0f; actor->y = 32.0f; actor->angle = 0.0f;

    auto makeMover = [&](Map::LineDef* line) -> std::shared_ptr<SectorMover> {
        return std::make_shared<Door>(line->backSide->sector, "Open", 96.0f, 64.0f);
    };
    auto isLockedCheck = [&](Map::LineDef*) -> std::shared_ptr<Door> { return nullptr; };

    auto mover = game->useKey(makeMover, isLockedCheck);
    CHECK(mover != nullptr);
    CHECK(std::find(game->specials.begin(), game->specials.end(), mover) != game->specials.end());
    CHECK_EQ(middleLine->special, 0);
}

TEST(map_exit_special_ends_the_map) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_13");
    Map::LineDef* exitLine = game->map.lineDefs[3];
    exitLine->special = EXIT_SPECIAL;
    CHECK(game->checkMapExit(exitLine));
    CHECK(game->exited);
}

TEST(map_exit_non_exit_special_does_nothing) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_14");
    Map::LineDef* line = game->map.lineDefs[1];
    line->special = 1;
    CHECK(!game->checkMapExit(line));
    CHECK(!game->exited);
}

TEST(tick_runs_full_loop_without_error) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_15");
    for (int i = 0; i < 35; i++) game->tickOnce(RawPlayerInput{10, 0, 1, 0});
    CHECK_EQ(game->tic, 35);
}

TEST(tick_menu_open_freezes_simulation) {
    std::unique_ptr<WadFile> wad;
    auto game = startGame(wad, "_16");
    game->menuStack.open(std::make_shared<Menu>("Main", std::vector<MenuItem>{}));
    int before = game->tic;
    game->tickOnce(RawPlayerInput{50, 0, 0, 0});
    CHECK_EQ(game->tic, before);
}

TEST_MAIN()
