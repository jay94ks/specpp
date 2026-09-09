// hud.md/menu.md/automap.md의 2D 오버레이를 위한 순수 지오메트리 생성기 (C++17).
// tests/doom_ui_geometry.py와 같은 알고리즘. OpenGL에 의존하지 않는다.
#pragma once
#include <algorithm>
#include <cmath>
#include <map>
#include <string>
#include <vector>

namespace Doom {

struct UiColor {
    float r, g, b;
};

inline void appendVertex(std::vector<float>& out, float x, float y, UiColor c) {
    out.insert(out.end(), {x, y, c.r, c.g, c.b});
}

inline std::vector<float> rect(float x0, float y0, float x1, float y1, UiColor color) {
    std::vector<float> v;
    appendVertex(v, x0, y0, color); appendVertex(v, x1, y0, color); appendVertex(v, x1, y1, color);
    appendVertex(v, x0, y0, color); appendVertex(v, x1, y1, color); appendVertex(v, x0, y1, color);
    return v;
}

inline std::vector<float> circleFan(float cx, float cy, float radius, UiColor color, int segments = 20) {
    std::vector<float> v;
    for (int i = 0; i < segments; i++) {
        float a0 = 2.0f * 3.14159265f * i / segments;
        float a1 = 2.0f * 3.14159265f * (i + 1) / segments;
        appendVertex(v, cx, cy, color);
        appendVertex(v, cx + std::cos(a0) * radius, cy + std::sin(a0) * radius, color);
        appendVertex(v, cx + std::cos(a1) * radius, cy + std::sin(a1) * radius, color);
    }
    return v;
}

inline std::vector<float> thickLine(float x1, float y1, float x2, float y2, float width, UiColor color) {
    float dx = x2 - x1, dy = y2 - y1;
    float length = std::sqrt(dx * dx + dy * dy);
    if (length < 1e-6f) return {};
    float nx = -dy / length * width / 2.0f, ny = dx / length * width / 2.0f;
    float p1x = x1 + nx, p1y = y1 + ny, p2x = x2 + nx, p2y = y2 + ny;
    float p3x = x2 - nx, p3y = y2 - ny, p4x = x1 - nx, p4y = y1 - ny;
    std::vector<float> v;
    appendVertex(v, p1x, p1y, color); appendVertex(v, p2x, p2y, color); appendVertex(v, p3x, p3y, color);
    appendVertex(v, p1x, p1y, color); appendVertex(v, p3x, p3y, color); appendVertex(v, p4x, p4y, color);
    return v;
}

inline UiColor skinColorFor(const std::string& base) {
    static const std::map<std::string, UiColor> table = {
        {"STFST", {0.89f, 0.65f, 0.44f}}, {"STFKILL", {0.89f, 0.65f, 0.44f}},
        {"STFOUCH", {0.85f, 0.56f, 0.35f}}, {"STFEVL", {0.79f, 0.42f, 0.29f}},
        {"STFDEAD0", {0.48f, 0.48f, 0.48f}},
    };
    auto it = table.find(base);
    return it != table.end() ? it->second : table.at("STFST");
}

// spp-source: examples/doom/hud.md#Feature:_얼굴_표정_갱신 (2D 지오메트리로 옮긴 것)
inline std::vector<float> faceTriangles(float cx, float cy, float r, const std::string& faceFrame) {
    std::string base = faceFrame.substr(0, faceFrame.find('_'));
    bool grin = faceFrame.find("GRIN") != std::string::npos;
    bool hit = faceFrame.find("HIT") != std::string::npos;
    UiColor skin = skinColorFor(base);
    constexpr UiColor WHITE{1.0f, 1.0f, 1.0f};
    constexpr UiColor BLACK{0.05f, 0.05f, 0.05f};

    std::vector<float> verts = circleFan(cx, cy, r, skin, 24);

    float eyeDx = r * 0.35f, eyeDy = -r * 0.15f;
    float eyeR = (base != "STFEVL") ? r * 0.16f : r * 0.22f;
    float pupilShift = hit ? r * 0.06f : 0.0f;
    float mouthY = cy + r * 0.42f;

    auto append = [&](std::vector<float> extra) { verts.insert(verts.end(), extra.begin(), extra.end()); };

    if (base == "STFDEAD0") {
        for (int sign : {-1, 1}) {
            float ex = cx + sign * eyeDx, ey = cy + eyeDy;
            append(thickLine(ex - 5, ey - 5, ex + 5, ey + 5, 2, BLACK));
            append(thickLine(ex - 5, ey + 5, ex + 5, ey - 5, 2, BLACK));
        }
        append(thickLine(cx - r * 0.4f, mouthY, cx + r * 0.4f, mouthY, 2, BLACK));
        return verts;
    }

    for (int sign : {-1, 1}) {
        float ex = cx + sign * eyeDx, ey = cy + eyeDy;
        append(circleFan(ex, ey, eyeR, WHITE, 14));
        append(circleFan(ex + pupilShift, ey, eyeR * 0.45f, BLACK, 10));
    }

    if (grin) {
        append(thickLine(cx - r * 0.3f, mouthY - r * 0.05f, cx + r * 0.3f, mouthY - r * 0.05f, 3, BLACK));
    } else if (base == "STFST") {
        append(thickLine(cx - r * 0.3f, mouthY, cx + r * 0.3f, mouthY, 2, BLACK));
    } else if (base == "STFKILL") {
        append(thickLine(cx - r * 0.3f, mouthY - r * 0.05f, cx + r * 0.3f, mouthY + r * 0.1f, 2, BLACK));
    } else {
        append(circleFan(cx, mouthY, r * 0.18f, {0.23f, 0.06f, 0.06f}, 12));
    }
    return verts;
}

inline UiColor healthBarColor(float ratio) {
    if (ratio > 0.66f) return {0.22f, 0.76f, 0.35f};
    if (ratio > 0.33f) return {0.82f, 0.77f, 0.23f};
    return {0.82f, 0.23f, 0.23f};
}

// spp-source: examples/doom/hud.md#Class:_Doom.Hud.render
inline std::vector<float> hudBarGeometry(float x, float y, float w, float h, float ratio, UiColor fillColor) {
    std::vector<float> verts = rect(x, y, x + w, y + h, {0.3f, 0.3f, 0.3f});
    float fillW = std::max(0.0f, (w - 4) * ratio);
    auto fill = rect(x + 2, y + 2, x + 2 + fillW, y + h - 2, fillColor);
    verts.insert(verts.end(), fill.begin(), fill.end());
    return verts;
}

inline UiColor keyColorFor(const std::string& name) {
    static const std::map<std::string, UiColor> table = {
        {"blue", {0.23f, 0.44f, 0.82f}}, {"yellow", {0.82f, 0.77f, 0.23f}}, {"red", {0.82f, 0.23f, 0.23f}},
    };
    return table.at(name);
}

inline std::vector<float> keyIconGeometry(float x, float y, float size, const std::string& colorName, bool owned) {
    UiColor color = owned ? keyColorFor(colorName) : UiColor{0.2f, 0.2f, 0.2f};
    return rect(x, y, x + size, y + size, color);
}

}  // namespace Doom
