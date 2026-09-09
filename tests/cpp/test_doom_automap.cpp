// examples/doom/automap.md 검증 (C++17).
#include "doom_automap.hpp"
#include "minitest.hpp"

using namespace Doom;
using namespace Doom::Map;

static Seg makeSegWithSecret(Vertex& v1, Vertex& v2, Sector& sector, SideDef& side, LineDef& line, bool secret) {
    side.sector = &sector;
    line = LineDef{&v1, &v2, secret ? uint16_t(LineDef::SECRET_FLAG) : uint16_t(0), 0, 0, &side, nullptr};
    return Seg{&v1, &v2, 0, &line, 0, 0};
}

TEST(automap_toggle_flips_open_state) {
    AutoMap m;
    CHECK(!m.isOpen());
    m.toggle();
    CHECK(m.isOpen());
    m.toggle();
    CHECK(!m.isOpen());
}

TEST(automap_reveals_lines_from_subsector) {
    Vertex v1{0, 0}, v2{10, 0};
    Sector sector{0, 0, "F", "C", 160, 0, 0};
    SideDef side{0, 0, "-", "-", "-", nullptr};
    LineDef line{nullptr, nullptr, 0, 0, 0, nullptr, nullptr};
    Seg seg = makeSegWithSecret(v1, v2, sector, side, line, false);
    Subsector subsector{{&seg}, seg.lineDef->frontSide->sector};

    AutoMap m;
    m.revealFromSubsector(&subsector);
    CHECK(std::find(m.revealedLines.begin(), m.revealedLines.end(), seg.lineDef) != m.revealedLines.end());
}

TEST(automap_secret_lines_not_revealed) {
    Vertex v1{0, 0}, v2{10, 0};
    Sector sector{0, 0, "F", "C", 160, 0, 0};
    SideDef side{0, 0, "-", "-", "-", nullptr};
    LineDef line{nullptr, nullptr, 0, 0, 0, nullptr, nullptr};
    Seg seg = makeSegWithSecret(v1, v2, sector, side, line, true);
    Subsector subsector{{&seg}, seg.lineDef->frontSide->sector};

    AutoMap m;
    m.revealFromSubsector(&subsector);
    CHECK(m.revealedLines.empty());
}

TEST(automap_zoom_clamped_to_min_max) {
    AutoMap m;
    m.panAndZoom(0, 0, -100);
    CHECK(m.zoom >= AUTOMAP_MIN_ZOOM);
    m.panAndZoom(0, 0, 100);
    CHECK(m.zoom <= AUTOMAP_MAX_ZOOM);
}

TEST(automap_pan_moves_center) {
    AutoMap m;
    m.panAndZoom(10, -5, 0);
    CHECK_EQ(m.centerX, 10.0f);
    CHECK_EQ(m.centerY, -5.0f);
}

TEST_MAIN()
