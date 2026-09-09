// hud.md의 얼굴 표정/체력 막대/열쇠 아이콘 2D 지오메트리 검증 (C++17).
#include "doom_ui_geometry.hpp"
#include "minitest.hpp"
#include <cmath>

using namespace Doom;

TEST(rect_produces_two_triangles_six_vertices) {
    auto verts = rect(0, 0, 10, 10, {1, 0, 0});
    CHECK_EQ(verts.size(), 6u * 5u);
}

TEST(circle_fan_segment_count_controls_triangle_count) {
    auto verts = circleFan(0, 0, 5, {1, 1, 1}, 16);
    CHECK_EQ(verts.size(), size_t(16 * 3 * 5));
}

TEST(circle_fan_points_lie_on_circle) {
    auto verts = circleFan(10, 20, 5, {1, 1, 1}, 8);
    float x = verts[5], y = verts[6];
    float dist = std::sqrt((x - 10) * (x - 10) + (y - 20) * (y - 20));
    CHECK(std::abs(dist - 5.0f) < 1e-4f);
}

TEST(thick_line_zero_length_is_empty) {
    CHECK(thickLine(1, 1, 1, 1, 2, {1, 0, 0}).empty());
}

TEST(thick_line_produces_two_triangles) {
    auto verts = thickLine(0, 0, 10, 0, 2, {1, 0, 0});
    CHECK_EQ(verts.size(), 6u * 5u);
}

TEST(face_all_known_categories_produce_geometry) {
    for (auto category : {"STFST", "STFKILL", "STFOUCH", "STFEVL", "STFDEAD0",
                           "STFST_GRIN", "STFKILL_HIT_front", "STFEVL_HIT_front"}) {
        auto verts = faceTriangles(50, 50, 24, category);
        CHECK(!verts.empty());
        CHECK_EQ(verts.size() % 5, 0u);
    }
}

TEST(face_dead_uses_gray_skin) {
    auto verts = faceTriangles(0, 0, 24, "STFDEAD0");
    CHECK(std::abs(verts[2] - 0.48f) < 0.01f);
    CHECK(std::abs(verts[3] - 0.48f) < 0.01f);
}

TEST(face_calm_uses_warm_skin_tone) {
    auto verts = faceTriangles(0, 0, 24, "STFST");
    CHECK(verts[2] > verts[3]);  // r > g for a warm/peach tone.
}

TEST(health_bar_color_thresholds) {
    auto full = healthBarColor(1.0f);
    auto seventy = healthBarColor(0.7f);
    auto low = healthBarColor(0.1f);
    CHECK(std::abs(full.r - seventy.r) < 1e-6f);
    CHECK(std::abs(full.r - low.r) > 1e-6f);
}

TEST(hud_bar_full_fill_matches_width) {
    auto verts = hudBarGeometry(0, 0, 100, 10, 1.0f, {0, 1, 0});
    float maxX = 0;
    for (size_t i = 30; i < 60; i += 5) maxX = std::max(maxX, verts[i]);
    CHECK(std::abs(maxX - 98.0f) < 1e-4f);
}

TEST(hud_bar_half_fill_is_half_width) {
    auto verts = hudBarGeometry(0, 0, 100, 10, 0.5f, {0, 1, 0});
    float maxX = 0;
    for (size_t i = 30; i < 60; i += 5) maxX = std::max(maxX, verts[i]);
    CHECK(std::abs(maxX - (2 + 96 * 0.5f)) < 1e-4f);
}

TEST(key_icon_owned_uses_its_color) {
    auto verts = keyIconGeometry(0, 0, 10, "blue", true);
    CHECK(std::abs(verts[4] - 0.82f) < 0.01f);  // b channel.
}

TEST(key_icon_unowned_is_gray) {
    auto verts = keyIconGeometry(0, 0, 10, "blue", false);
    CHECK(std::abs(verts[2] - verts[3]) < 1e-6f);
    CHECK(std::abs(verts[3] - verts[4]) < 1e-6f);
}

TEST_MAIN()
