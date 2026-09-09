// examples/doom/map.md 검증 (C++17).
#include "doom_map.hpp"
#include "doom_test_fixtures.hpp"
#include "minitest.hpp"
#include <fstream>

using namespace Doom::Map;

TEST(bsp_point_on_side_always_zero_or_one) {
    Sector west{0, 128, "F0", "C0", 160, 0, 0};
    Sector east{0, 96, "F1", "C1", 120, 0, 0};
    Subsector subWest{{}, &west};
    Subsector subEast{{}, &east};
    BspNode root{32, 0, 0, 1, &subWest, &subEast, {64, 0, 0, 32}, {64, 0, 32, 64}};

    for (auto [x, y] : {std::pair{-100.0f, -100.0f}, {0.0f, 0.0f}, {32.0f, 32.0f}, {1000.0f, 1000.0f}}) {
        int side = BspNode::PointOnSide(x, y, root);
        CHECK(side == 0 || side == 1);
    }
}

TEST(bsp_find_subsector_west_and_east_of_split) {
    Sector west{0, 128, "F0", "C0", 160, 0, 0};
    Sector east{0, 96, "F1", "C1", 120, 0, 0};
    Subsector subWest{{}, &west};
    Subsector subEast{{}, &east};
    BspNode root{32, 0, 0, 1, &subWest, &subEast, {64, 0, 0, 32}, {64, 0, 32, 64}};

    Subsector* foundWest = BspNode::FindSubsector(10, 30, &root);
    Subsector* foundEast = BspNode::FindSubsector(50, 30, &root);
    CHECK(foundWest == &subWest);
    CHECK(foundEast == &subEast);
}

static std::string writeFixtureWad() {
    auto bytes = DoomFixtures::buildTwoRoomMapWad();
    std::string path = "tmp_map_test.wad";
    std::ofstream f(path, std::ios::binary);
    f.write(reinterpret_cast<const char*>(bytes.data()), bytes.size());
    return path;
}

TEST(map_load_parses_vertices_sectors_linedefs_things) {
    auto path = writeFixtureWad();
    Doom::WadFile wad(path);
    MapData map = MapData::Load(wad, DoomFixtures::MAP_NAME);

    CHECK_EQ(map.vertices.size(), 6u);
    CHECK_EQ(map.vertices[0]->x, 0.0f);
    CHECK_EQ(map.vertices[2]->x, 64.0f);

    CHECK_EQ(map.sectors.size(), 2u);
    CHECK_EQ(map.sectors[0]->ceilingHeight, 128.0f);
    CHECK_EQ(map.sectors[1]->ceilingHeight, 96.0f);
    CHECK_EQ(map.sectors[0]->floorTexture, "FLOOR0");

    LineDef* middle = map.lineDefs[1];
    CHECK(middle->isPassable());
    CHECK(middle->frontSide->sector == map.sectors[0]);
    CHECK(middle->backSide->sector == map.sectors[1]);

    LineDef* wall = map.lineDefs[0];
    CHECK(!wall->isPassable());

    CHECK_EQ(map.things.size(), 2u);
    CHECK_EQ(map.things[1]->type, 3004);
}

TEST(map_load_find_subsector_matches_expected_sector) {
    auto path = writeFixtureWad();
    Doom::WadFile wad(path);
    MapData map = MapData::Load(wad, DoomFixtures::MAP_NAME);

    Subsector* west = BspNode::FindSubsector(16, 32, map.bspRoot);
    Subsector* east = BspNode::FindSubsector(48, 32, map.bspRoot);
    CHECK(west->sector == map.sectors[0]);
    CHECK(east->sector == map.sectors[1]);
}

TEST_MAIN()
