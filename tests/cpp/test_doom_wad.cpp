// examples/doom/wad.md 검증 (C++17).
#include "doom_wad.hpp"
#include "minitest.hpp"
#include <cstdio>
#include <fstream>

using namespace Doom;

static std::string writeTempWad(const std::vector<uint8_t>& bytes, const char* suffix) {
    std::string path = std::string("tmp_wad_test") + suffix + ".wad";
    std::ofstream f(path, std::ios::binary);
    f.write(reinterpret_cast<const char*>(bytes.data()), bytes.size());
    f.close();
    return path;
}

TEST(wad_find_and_read_known_lump) {
    auto bytes = buildWadBytes({{"E1M1", {'m', 'a', 'p', '-', 'd', 'a', 't', 'a'}}});
    auto path = writeTempWad(bytes, "_1");
    WadFile wad(path);
    int idx = wad.findLump("E1M1");
    CHECK(idx != -1);
    auto data = wad.readLump(idx);
    CHECK_EQ(static_cast<int>(data.size()), wad.lumps[idx].size);
    std::remove(path.c_str());
}

TEST(wad_missing_name_returns_minus_one) {
    auto bytes = buildWadBytes({{"A", {1}}});
    auto path = writeTempWad(bytes, "_2");
    WadFile wad(path);
    CHECK_EQ(wad.findLump("NOPE"), -1);
    std::remove(path.c_str());
}

TEST(wad_duplicate_name_returns_latest) {
    auto bytes = buildWadBytes({{"DUP", {1, 2, 3}}, {"DUP", {9, 9}}});
    auto path = writeTempWad(bytes, "_3");
    WadFile wad(path);
    int idx = wad.findLump("DUP");
    auto data = wad.readLump(idx);
    CHECK_EQ(data.size(), 2u);
    CHECK_EQ(data[0], 9);
    std::remove(path.c_str());
}

TEST(wad_case_insensitive_lookup) {
    auto bytes = buildWadBytes({{"E1M1", {1}}});
    auto path = writeTempWad(bytes, "_4");
    WadFile wad(path);
    CHECK_EQ(wad.findLump("e1m1"), 0);
    std::remove(path.c_str());
}

TEST(wad_rejects_non_wad_file) {
    std::vector<uint8_t> junk(30, 0);
    junk[0] = 'N'; junk[1] = 'O'; junk[2] = 'P'; junk[3] = 'E';
    auto path = writeTempWad(junk, "_5");
    bool threw = false;
    try {
        WadFile wad(path);
    } catch (const std::exception&) {
        threw = true;
    }
    CHECK(threw);
    std::remove(path.c_str());
}

TEST(palette_color_at_reads_rgb_triplet) {
    std::vector<uint8_t> playpal(768, 0);
    playpal[0] = 10; playpal[1] = 20; playpal[2] = 30;
    playpal[3] = 40; playpal[4] = 50; playpal[5] = 60;
    Palette pal(playpal);
    auto c0 = pal.colorAt(0);
    CHECK_EQ(c0[0], 10); CHECK_EQ(c0[1], 20); CHECK_EQ(c0[2], 30);
    auto c1 = pal.colorAt(1);
    CHECK_EQ(c1[0], 40); CHECK_EQ(c1[1], 50); CHECK_EQ(c1[2], 60);
}

TEST_MAIN()
