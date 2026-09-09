// examples/doom/render.md 의 뷰/투영 행렬 계산 검증 (C++17).
#include "doom_gl_math.hpp"
#include "minitest.hpp"

using namespace Doom;

TEST(identity_times_identity_is_identity) {
    Mat4 result = multiply(identity(), identity());
    for (int i = 0; i < 16; i++) CHECK_EQ(result[i], identity()[i]);
}

TEST(multiply_matches_translation_composition) {
    auto translation = [](float x, float y, float z) {
        Mat4 m = identity();
        m[12] = x; m[13] = y; m[14] = z;
        return m;
    };
    Mat4 combined = multiply(translation(1, 0, 0), translation(0, 2, 0));
    CHECK(std::abs(combined[12] - 1.0f) < 1e-5f);
    CHECK(std::abs(combined[13] - 2.0f) < 1e-5f);
}

TEST(perspective_center_point_maps_near_zero_ndc) {
    Mat4 proj = perspective(90.0f, 1.0f, 0.1f, 100.0f);
    float x = 0.0f, y = 0.0f, z = -5.0f, w = 1.0f;
    float clipX = proj[0] * x + proj[4] * y + proj[8] * z + proj[12] * w;
    float clipW = proj[3] * x + proj[7] * y + proj[11] * z + proj[15] * w;
    CHECK(std::abs(clipX) < 1e-5f);
    CHECK(clipW > 0.0f);
}

TEST(ortho_maps_top_left_corner_to_minus1_plus1) {
    Mat4 m = ortho(0, 640, 400, 0, -1, 1);
    float x = m[0] * 0 + m[12];
    float y = m[5] * 0 + m[13];
    CHECK(std::abs(x - (-1.0f)) < 1e-5f);
    CHECK(std::abs(y - 1.0f) < 1e-5f);
}

TEST(look_at_positive_x_axis_point_is_in_front) {
    Mat4 view = lookAt({0, 0, 0}, {1, 0, 0}, {0, 1, 0});
    float wx = 5.0f, wy = 0.0f, wz = 0.0f;
    float camZ = view[2] * wx + view[6] * wy + view[10] * wz + view[14];
    CHECK(camZ < 0.0f);
}

TEST(view_from_player_right_and_up_orthonormal) {
    Mat4 view = viewFromPlayer(0, 41, 0, 45.0f);
    Vec3 right, up;
    rightAndUpFromView(view, right, up);
    CHECK(std::abs(length(right) - 1.0f) < 1e-4f);
    CHECK(std::abs(length(up) - 1.0f) < 1e-4f);
    CHECK(std::abs(dot(right, up)) < 1e-4f);
}

TEST(view_from_player_yaw_zero_faces_positive_x) {
    Mat4 view = viewFromPlayer(0, 0, 0, 0.0f);
    float camZ = view[2] * 10 + view[14];
    CHECK(camZ < 0.0f);
}

TEST_MAIN()
