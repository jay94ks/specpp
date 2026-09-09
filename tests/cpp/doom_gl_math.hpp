// render.md의 뷰/투영 행렬 계산을 위한 아주 작은 4x4 행렬 유틸리티 (C++17).
// tests/doom_gl_math.py와 같은 알고리즘 — 컬럼 메이저 16-float 배열.
#pragma once
#include <array>
#include <cmath>

namespace Doom {

using Mat4 = std::array<float, 16>;
using Vec3 = std::array<float, 3>;

inline Mat4 identity() {
    Mat4 m{};
    m[0] = m[5] = m[10] = m[15] = 1.0f;
    return m;
}

inline Mat4 multiply(const Mat4& a, const Mat4& b) {
    Mat4 result{};
    for (int col = 0; col < 4; col++) {
        for (int row = 0; row < 4; row++) {
            float s = 0.0f;
            for (int k = 0; k < 4; k++) s += a[k * 4 + row] * b[col * 4 + k];
            result[col * 4 + row] = s;
        }
    }
    return result;
}

inline Mat4 perspective(float fovYDeg, float aspect, float near_, float far_) {
    float f = 1.0f / std::tan(fovYDeg * 3.14159265f / 180.0f / 2.0f);
    Mat4 m{};
    m[0] = f / aspect;
    m[5] = f;
    m[10] = (far_ + near_) / (near_ - far_);
    m[11] = -1.0f;
    m[14] = (2 * far_ * near_) / (near_ - far_);
    return m;
}

inline Mat4 ortho(float left, float right, float bottom, float top, float near_, float far_) {
    Mat4 m = identity();
    m[0] = 2.0f / (right - left);
    m[5] = 2.0f / (top - bottom);
    m[10] = -2.0f / (far_ - near_);
    m[12] = -(right + left) / (right - left);
    m[13] = -(top + bottom) / (top - bottom);
    m[14] = -(far_ + near_) / (far_ - near_);
    return m;
}

inline float length(const Vec3& v) { return std::sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]); }

inline Vec3 normalize(const Vec3& v) {
    float len = length(v);
    if (len < 1e-9f) return {0.0f, 0.0f, 0.0f};
    return {v[0] / len, v[1] / len, v[2] / len};
}

inline Vec3 cross(const Vec3& a, const Vec3& b) {
    return {a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]};
}

inline float dot(const Vec3& a, const Vec3& b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }

inline Vec3 sub(const Vec3& a, const Vec3& b) { return {a[0] - b[0], a[1] - b[1], a[2] - b[2]}; }

inline Mat4 lookAt(const Vec3& eye, const Vec3& center, const Vec3& up) {
    Vec3 f = normalize(sub(center, eye));
    Vec3 s = normalize(cross(f, up));
    Vec3 u = cross(s, f);
    Mat4 m = identity();
    m[0] = s[0]; m[4] = s[1]; m[8] = s[2];
    m[1] = u[0]; m[5] = u[1]; m[9] = u[2];
    m[2] = -f[0]; m[6] = -f[1]; m[10] = -f[2];
    m[12] = -dot(s, eye);
    m[13] = -dot(u, eye);
    m[14] = dot(f, eye);
    return m;
}

inline Mat4 viewFromPlayer(float x, float height, float z, float yawDeg) {
    float yaw = yawDeg * 3.14159265f / 180.0f;
    Vec3 forward = {std::cos(yaw), 0.0f, std::sin(yaw)};
    Vec3 eye = {x, height, z};
    Vec3 center = {x + forward[0], height, z + forward[2]};
    return lookAt(eye, center, {0.0f, 1.0f, 0.0f});
}

inline void rightAndUpFromView(const Mat4& view, Vec3& right, Vec3& up) {
    right = {view[0], view[4], view[8]};
    up = {view[1], view[5], view[9]};
}

}  // namespace Doom
