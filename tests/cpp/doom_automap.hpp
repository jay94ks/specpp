// examples/doom/automap.md 의 # Domain/# Behavior 참조 구현 (C++17).
#pragma once
#include "doom_map.hpp"
#include <algorithm>
#include <vector>

namespace Doom {

constexpr float AUTOMAP_MIN_ZOOM = 0.25f;
constexpr float AUTOMAP_MAX_ZOOM = 4.0f;

class AutoMap {
public:
    bool isOpen_ = false;
    float centerX = 0, centerY = 0;
    float zoom = 1.0f;
    std::vector<Map::LineDef*> revealedLines;

    bool isOpen() const { return isOpen_; }

    // spp-source: examples/doom/automap.md#Feature:_자동_지도_토글
    void toggle() { isOpen_ = !isOpen_; }

    // spp-source: examples/doom/automap.md#Feature:_지도에_선_드러내기
    void revealFromSubsector(Map::Subsector* subsector) {
        for (auto* seg : subsector->segs) {
            auto* line = seg->lineDef;
            if (line->isSecret()) continue;
            if (std::find(revealedLines.begin(), revealedLines.end(), line) == revealedLines.end()) {
                revealedLines.push_back(line);
            }
        }
    }

    // spp-source: examples/doom/automap.md#Feature:_지도_이동·확대
    void panAndZoom(float panX, float panY, float zoomDelta) {
        centerX += panX;
        centerY += panY;
        zoom = std::max(AUTOMAP_MIN_ZOOM, std::min(AUTOMAP_MAX_ZOOM, zoom + zoomDelta));
    }
};

}  // namespace Doom
