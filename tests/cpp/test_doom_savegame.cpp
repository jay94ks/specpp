// examples/doom/savegame.md 검증 (C++17).
#include "doom_savegame.hpp"
#include "doom_test_fixtures.hpp"
#include "minitest.hpp"
#include <fstream>

using namespace Doom;

static std::unique_ptr<WadFile> writeAndOpenFixtureWad(const char* suffix) {
    auto bytes = DoomFixtures::buildTwoRoomMapWad();
    std::string path = std::string("tmp_savegame_test") + suffix + ".wad";
    std::ofstream f(path, std::ios::binary);
    f.write(reinterpret_cast<const char*>(bytes.data()), bytes.size());
    f.close();
    return std::make_unique<WadFile>(path);
}

TEST(savegame_restore_immediately_after_save_matches_original) {
    auto wad = writeAndOpenFixtureWad("_1");
    auto game = Game::Start(*wad, DoomFixtures::MAP_NAME, [] { return 0.0; });

    game->player->health = 63;
    game->player->armor = 40;
    game->player->ammo["bullets"] = 17;
    game->killCount = 2;
    auto door = std::make_shared<Door>(game->map.sectors[1], "Open", 96.0f, 4.0f);
    door->sector->ceilingHeight = 50;
    game->specials.push_back(door);

    SaveGame snapshot = SaveGame::Save(*game, "E1M1 테스트 저장");
    auto restored = snapshot.restore(*wad);

    CHECK_EQ(restored->player->health, 63);
    CHECK_EQ(restored->player->armor, 40);
    CHECK_EQ(restored->player->ammo["bullets"], 17);
    CHECK_EQ(restored->killCount, 2);
    CHECK_EQ(restored->player->actor->x, game->player->actor->x);
    CHECK_EQ(restored->player->actor->y, game->player->actor->y);
    CHECK_EQ(restored->specials.size(), 1u);
    CHECK_EQ(restored->specials[0]->getSector()->ceilingHeight, 50.0f);
    CHECK_EQ(restored->actors.size(), game->actors.size());
}

TEST(savegame_restoring_does_not_mutate_original_snapshot) {
    auto wad = writeAndOpenFixtureWad("_2");
    auto game = Game::Start(*wad, DoomFixtures::MAP_NAME, [] { return 0.0; });

    SaveGame snapshot = SaveGame::Save(*game, "slot 1");
    auto restored = snapshot.restore(*wad);
    restored->player->health = 1;
    CHECK(snapshot.playerHealth != 1);
}

TEST_MAIN()
