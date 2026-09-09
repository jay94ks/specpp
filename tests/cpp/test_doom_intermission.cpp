// examples/doom/intermission.md 검증 (C++17).
#include "doom_intermission.hpp"
#include "minitest.hpp"

using namespace Doom;

TEST(intermission_percentages_from_counts) {
    auto im = makeIntermission("E1M1", std::optional<std::string>("E1M2"), 5, 10, 3, 4, 1, 2, 1050, 900);
    CHECK_EQ(im.killPercent, 50);
    CHECK_EQ(im.itemPercent, 75);
    CHECK_EQ(im.secretPercent, 50);
    CHECK_EQ(*im.nextMapName, std::string("E1M2"));
}

TEST(intermission_full_clear_is_100_percent) {
    auto im = makeIntermission("E1M1", std::optional<std::string>("E1M2"), 10, 10, 4, 4, 2, 2, 1050, 900);
    CHECK_EQ(im.killPercent, 100);
    CHECK_EQ(im.itemPercent, 100);
    CHECK_EQ(im.secretPercent, 100);
}

TEST(intermission_zero_total_defaults_to_100) {
    auto im = makeIntermission("E1M1", std::nullopt, 0, 0, 0, 0, 0, 0, 1050, 900);
    CHECK_EQ(im.killPercent, 100);
    CHECK_EQ(im.itemPercent, 100);
    CHECK_EQ(im.secretPercent, 100);
}

TEST(intermission_last_map_has_no_next) {
    auto im = makeIntermission("E1M8", std::nullopt, 8, 8, 4, 4, 1, 1, 1050, 900);
    CHECK(!im.nextMapName.has_value());
}

TEST_MAIN()
