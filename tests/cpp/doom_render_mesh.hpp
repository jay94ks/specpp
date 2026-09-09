// examples/doom/render.md 의 'Feature: 레벨 지오메트리 만들기' 참조 구현 (C++17).
// GPU에 의존하지 않는 순수 정점/인덱스 데이터 생성 — tests/doom_render_mesh.py와
// 같은 알고리즘. 좌표계: (glX, glY, glZ) = (doomX, height, doomY).
#pragma once
#include "doom_map.hpp"
#include <cmath>
#include <cstdint>
#include <functional>
#include <string>
#include <vector>

namespace Doom {

constexpr int FLOATS_PER_VERTEX = 7;  // x,y,z,r,g,b,light

struct Color3 {
    float r, g, b;
};

inline Color3 textureColor(const std::string& name, float lightLevel) {
    // Python의 colorsys.hsv_to_rgb(hue, 0.5, brightness)와 같은 결과를 내는
    // 아주 작은 HSV->RGB 변환. hash는 std::hash로 대체한다(값 자체는 달라도
    // "텍스처 이름마다 다른 색"이라는 성질만 필요하다).
    auto h = std::hash<std::string>{}(name);
    float hue = float(h % 360) / 360.0f;
    float brightness = std::max(0.15f, std::min(1.0f, lightLevel / 255.0f));
    float sat = 0.5f;

    float c = brightness * sat;
    float hh = hue * 6.0f;
    float x = c * (1 - std::abs(std::fmod(hh, 2.0f) - 1));
    float r1, g1, b1;
    if (hh < 1) { r1 = c; g1 = x; b1 = 0; }
    else if (hh < 2) { r1 = x; g1 = c; b1 = 0; }
    else if (hh < 3) { r1 = 0; g1 = c; b1 = x; }
    else if (hh < 4) { r1 = 0; g1 = x; b1 = c; }
    else if (hh < 5) { r1 = x; g1 = 0; b1 = c; }
    else { r1 = c; g1 = 0; b1 = x; }
    float m = brightness - c;
    return {r1 + m, g1 + m, b1 + m};
}

struct Point3 {
    float x, y, z;
};

class MeshData {
public:
    std::vector<float> vertices;
    std::vector<uint32_t> indices;

    int vertexCount() const { return int(vertices.size()) / FLOATS_PER_VERTEX; }
    int triangleCount() const { return int(indices.size()) / 3; }

    void addVertex(Point3 p, Color3 c, float light) {
        vertices.insert(vertices.end(), {p.x, p.y, p.z, c.r, c.g, c.b, light});
    }

    // spp-source: examples/doom/render.md#Feature:_레벨_지오메트리_만들기 (벽 사각형)
    void addQuad(Point3 p1, Point3 p2, Point3 p3, Point3 p4, Color3 color, float light) {
        uint32_t base = uint32_t(vertexCount());
        addVertex(p1, color, light);
        addVertex(p2, color, light);
        addVertex(p3, color, light);
        addVertex(p4, color, light);
        indices.insert(indices.end(), {base, base + 1, base + 2, base, base + 2, base + 3});
    }

    // spp-source: examples/doom/render.md#Feature:_레벨_지오메트리_만들기 (바닥/천장 부채꼴)
    int addFan(const std::vector<Point3>& points, Color3 color, float light) {
        if (points.size() < 3) return 0;
        uint32_t base = uint32_t(vertexCount());
        for (auto& p : points) addVertex(p, color, light);
        int triangles = 0;
        for (size_t i = 1; i + 1 < points.size(); i++) {
            indices.insert(indices.end(), {base, uint32_t(base + i), uint32_t(base + i + 1)});
            triangles++;
        }
        return triangles;
    }
};

inline void wallQuadsForLineDef(Map::LineDef* line, MeshData& mesh) {
    float x1 = line->v1->x, y1 = line->v1->y;
    float x2 = line->v2->x, y2 = line->v2->y;

    if (!line->isPassable()) {
        auto* front = line->frontSide->sector;
        Color3 color = textureColor(line->frontSide->middleTexture, float(front->lightLevel));
        mesh.addQuad({x1, front->floorHeight, y1}, {x2, front->floorHeight, y2},
                      {x2, front->ceilingHeight, y2}, {x1, front->ceilingHeight, y1},
                      color, float(front->lightLevel));
        return;
    }

    auto* front = line->frontSide->sector;
    auto* back = line->backSide->sector;

    if (front->ceilingHeight > back->ceilingHeight) {
        Color3 color = textureColor(line->frontSide->topTexture, float(front->lightLevel));
        mesh.addQuad({x1, back->ceilingHeight, y1}, {x2, back->ceilingHeight, y2},
                      {x2, front->ceilingHeight, y2}, {x1, front->ceilingHeight, y1},
                      color, float(front->lightLevel));
    }
    if (back->floorHeight > front->floorHeight) {
        Color3 color = textureColor(line->frontSide->bottomTexture, float(front->lightLevel));
        mesh.addQuad({x1, front->floorHeight, y1}, {x2, front->floorHeight, y2},
                      {x2, back->floorHeight, y2}, {x1, back->floorHeight, y1},
                      color, float(front->lightLevel));
    }
}

inline int floorCeilingFansForSubsector(Map::Subsector* subsector, MeshData& mesh) {
    if (subsector->segs.empty()) return 0;
    std::vector<std::pair<float, float>> boundary;
    for (auto* seg : subsector->segs) boundary.push_back({seg->v1->x, seg->v1->y});

    auto* sector = subsector->sector;
    Color3 floorColor = textureColor(sector->floorTexture, float(sector->lightLevel));
    Color3 ceilColor = textureColor(sector->ceilingTexture, float(sector->lightLevel));

    std::vector<Point3> floorPts, ceilPts;
    for (auto& [x, y] : boundary) floorPts.push_back({x, sector->floorHeight, y});
    for (auto it = boundary.rbegin(); it != boundary.rend(); ++it)
        ceilPts.push_back({it->first, sector->ceilingHeight, it->second});

    int triangles = mesh.addFan(floorPts, floorColor, float(sector->lightLevel));
    triangles += mesh.addFan(ceilPts, ceilColor, float(sector->lightLevel));
    return triangles;
}

// spp-source: examples/doom/render.md#Feature:_레벨_지오메트리_만들기
inline MeshData buildLevelMesh(Map::MapData& map) {
    MeshData mesh;
    for (auto* line : map.lineDefs) wallQuadsForLineDef(line, mesh);
    for (auto* subsector : map.subsectors) floorCeilingFansForSubsector(subsector, mesh);
    return mesh;
}

}  // namespace Doom
