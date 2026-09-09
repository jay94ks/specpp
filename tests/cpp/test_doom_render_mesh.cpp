// examples/doom/render.md 의 레벨 지오메트리 생성 검증 (C++17).
// doom_test_fixtures.hpp의 합성 맵과, 실제 셰어웨어 doom1.wad의 E1M1로 둘 다 검증한다.
#include "doom_render_mesh.hpp"
#include "doom_test_fixtures.hpp"
#include "minitest.hpp"
#include <fstream>

using namespace Doom;

TEST(mesh_add_quad_makes_two_triangles) {
    MeshData mesh;
    mesh.addQuad({0, 0, 0}, {1, 0, 0}, {1, 1, 0}, {0, 1, 0}, {1, 0, 0}, 160);
    CHECK_EQ(mesh.vertexCount(), 4);
    CHECK_EQ(mesh.triangleCount(), 2);
}

TEST(mesh_add_fan_n_minus_2_triangles) {
    MeshData mesh;
    std::vector<Point3> pentagon = {{0, 0, 0}, {1, 0, 0}, {1.5f, 0, 1}, {0.5f, 0, 2}, {-0.5f, 0, 1}};
    int triangles = mesh.addFan(pentagon, {0, 1, 0}, 160);
    CHECK_EQ(triangles, int(pentagon.size()) - 2);
    CHECK_EQ(mesh.triangleCount(), int(pentagon.size()) - 2);
}

TEST(mesh_multiple_adds_accumulate) {
    MeshData mesh;
    mesh.addQuad({0, 0, 0}, {1, 0, 0}, {1, 1, 0}, {0, 1, 0}, {1, 0, 0}, 160);
    mesh.addQuad({0, 0, 0}, {1, 0, 0}, {1, 1, 0}, {0, 1, 0}, {1, 0, 0}, 160);
    CHECK_EQ(mesh.vertexCount(), 8);
    CHECK_EQ(mesh.triangleCount(), 4);
    CHECK_EQ(mesh.indices[6], 4u);
}

static std::string writeFixtureWad() {
    auto bytes = DoomFixtures::buildTwoRoomMapWad();
    std::string path = "tmp_meshtest.wad";
    std::ofstream f(path, std::ios::binary);
    f.write(reinterpret_cast<const char*>(bytes.data()), bytes.size());
    return path;
}

TEST(fixture_single_sided_wall_makes_one_quad) {
    auto path = writeFixtureWad();
    WadFile wad(path);
    Map::MapData map = Map::MapData::Load(wad, DoomFixtures::MAP_NAME);
    MeshData mesh;
    wallQuadsForLineDef(map.lineDefs[0], mesh);  // L0: 단면 벽.
    CHECK(!map.lineDefs[0]->isPassable());
    CHECK_EQ(mesh.triangleCount(), 2);
}

TEST(fixture_two_sided_wall_with_ceiling_step_makes_one_quad) {
    auto path = writeFixtureWad();
    WadFile wad(path);
    Map::MapData map = Map::MapData::Load(wad, DoomFixtures::MAP_NAME);
    MeshData mesh;
    wallQuadsForLineDef(map.lineDefs[1], mesh);  // L1: 문, 천장 차이만 있음.
    CHECK(map.lineDefs[1]->isPassable());
    CHECK_EQ(mesh.triangleCount(), 2);
}

TEST(fixture_full_level_mesh_nontrivial) {
    auto path = writeFixtureWad();
    WadFile wad(path);
    Map::MapData map = Map::MapData::Load(wad, DoomFixtures::MAP_NAME);
    MeshData mesh = buildLevelMesh(map);
    CHECK(mesh.triangleCount() > 0);
}

TEST(fixture_subsector_fan_triangle_count_matches_seg_count_minus_two) {
    auto path = writeFixtureWad();
    WadFile wad(path);
    Map::MapData map = Map::MapData::Load(wad, DoomFixtures::MAP_NAME);
    for (auto* subsector : map.subsectors) {
        MeshData mesh;
        int triangles = floorCeilingFansForSubsector(subsector, mesh);
        int expected = 2 * (int(subsector->segs.size()) - 2);
        CHECK_EQ(triangles, expected);
    }
}

TEST(real_e1m1_mesh_is_nontrivial_and_indices_in_bounds) {
    WadFile wad("../../examples/doom/assets/doom1.wad");
    Map::MapData map = Map::MapData::Load(wad, "E1M1");
    MeshData mesh = buildLevelMesh(map);
    CHECK(mesh.triangleCount() > 500);
    CHECK(mesh.vertexCount() > 500);
    for (auto idx : mesh.indices) {
        CHECK(int(idx) >= 0);
        CHECK(int(idx) < mesh.vertexCount());
    }
}

TEST(real_e1m1_every_subsector_contributes_convex_fan) {
    WadFile wad("../../examples/doom/assets/doom1.wad");
    Map::MapData map = Map::MapData::Load(wad, "E1M1");
    int totalExpected = 0, totalActual = 0;
    for (auto* subsector : map.subsectors) {
        if (subsector->segs.size() >= 3) totalExpected += 2 * (int(subsector->segs.size()) - 2);
        MeshData mesh;
        totalActual += floorCeilingFansForSubsector(subsector, mesh);
    }
    CHECK_EQ(totalActual, totalExpected);
}

TEST_MAIN()
