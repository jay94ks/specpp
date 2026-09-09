// 여러 test_doom_*.cpp가 공유하는, 손으로 만든 아주 작은 2방 맵 WAD.
// tests/doom_test_fixtures.py의 build_two_room_map_wad()와 동일한 배치다.
#pragma once
#include "doom_wad.hpp"
#include <cstring>
#include <vector>

namespace DoomFixtures {

inline const std::string MAP_NAME = "TESTMAP";
constexpr uint16_t NO_SIDE = 0xFFFF;
constexpr uint16_t SUBSECTOR_BIT = 0x8000;

template <typename T>
inline void appendLE(std::vector<uint8_t>& out, T value) {
    auto p = reinterpret_cast<uint8_t*>(&value);
    out.insert(out.end(), p, p + sizeof(T));
}

inline void appendName8(std::vector<uint8_t>& out, const std::string& name) {
    char buf[8] = {0};
    std::memcpy(buf, name.c_str(), std::min<size_t>(8, name.size()));
    out.insert(out.end(), buf, buf + 8);
}

inline std::vector<uint8_t> buildTwoRoomMapWad() {
    // 정점: V0..V5.
    std::vector<std::pair<int16_t, int16_t>> vertices = {
        {0, 0}, {32, 0}, {64, 0}, {64, 64}, {32, 64}, {0, 64},
    };
    enum { V0 = 0, V1, V2, V3, V4, V5 };

    std::vector<uint8_t> vertexes;
    for (auto& [x, y] : vertices) { appendLE<int16_t>(vertexes, x); appendLE<int16_t>(vertexes, y); }

    std::vector<uint8_t> sectors;
    auto packSector = [&](int16_t floorH, int16_t ceilH, const std::string& ft, const std::string& ct,
                           int16_t light, int16_t special, int16_t tag) {
        appendLE<int16_t>(sectors, floorH); appendLE<int16_t>(sectors, ceilH);
        appendName8(sectors, ft); appendName8(sectors, ct);
        appendLE<int16_t>(sectors, light); appendLE<int16_t>(sectors, special); appendLE<int16_t>(sectors, tag);
    };
    packSector(0, 128, "FLOOR0", "CEIL0", 160, 0, 0);
    packSector(0, 96, "FLOOR1", "CEIL1", 120, 0, 0);

    std::vector<uint8_t> sidedefs;
    auto packSide = [&](int16_t offX, int16_t offY, const std::string& top, const std::string& bottom,
                         const std::string& mid, int16_t secIdx) {
        appendLE<int16_t>(sidedefs, offX); appendLE<int16_t>(sidedefs, offY);
        appendName8(sidedefs, top); appendName8(sidedefs, bottom); appendName8(sidedefs, mid);
        appendLE<int16_t>(sidedefs, secIdx);
    };
    packSide(0, 0, "-", "-", "WALL", 0);  // S0: L0 front (sector0)
    packSide(0, 0, "-", "-", "-", 0);      // S1: L1 front (sector0)
    packSide(0, 0, "-", "-", "-", 1);      // S2: L1 back  (sector1)
    packSide(0, 0, "-", "-", "WALL", 0);  // S3: L2 front
    packSide(0, 0, "-", "-", "WALL", 0);  // S4: L3 front
    packSide(0, 0, "-", "-", "WALL", 1);  // S5: L4 front (sector1)
    packSide(0, 0, "-", "-", "WALL", 1);  // S6: L5 front
    packSide(0, 0, "-", "-", "WALL", 1);  // S7: L6 front

    std::vector<uint8_t> linedefs;
    auto packLine = [&](uint16_t v1, uint16_t v2, uint16_t flags, uint16_t special, uint16_t tag,
                         uint16_t sideFront, uint16_t sideBack) {
        appendLE<uint16_t>(linedefs, v1); appendLE<uint16_t>(linedefs, v2);
        appendLE<uint16_t>(linedefs, flags); appendLE<uint16_t>(linedefs, special);
        appendLE<uint16_t>(linedefs, tag); appendLE<uint16_t>(linedefs, sideFront);
        appendLE<uint16_t>(linedefs, sideBack);
    };
    packLine(V0, V1, 0, 0, 0, 0, NO_SIDE);
    packLine(V1, V4, 0, 0, 0, 1, 2);
    packLine(V4, V5, 0, 0, 0, 3, NO_SIDE);
    packLine(V5, V0, 0, 0, 0, 4, NO_SIDE);
    packLine(V1, V2, 0, 0, 0, 5, NO_SIDE);
    packLine(V2, V3, 0, 0, 0, 6, NO_SIDE);
    packLine(V3, V4, 0, 0, 0, 7, NO_SIDE);

    std::vector<uint8_t> segs;
    auto packSeg = [&](uint16_t v1, uint16_t v2, int16_t angle, uint16_t lineIdx, int16_t side, int16_t off) {
        appendLE<uint16_t>(segs, v1); appendLE<uint16_t>(segs, v2);
        appendLE<int16_t>(segs, angle); appendLE<uint16_t>(segs, lineIdx);
        appendLE<int16_t>(segs, side); appendLE<int16_t>(segs, off);
    };
    packSeg(V0, V1, 0, 0, 0, 0);
    packSeg(V1, V4, 0, 1, 0, 0);
    packSeg(V4, V5, 0, 2, 0, 0);
    packSeg(V5, V0, 0, 3, 0, 0);
    packSeg(V1, V2, 0, 4, 0, 0);
    packSeg(V2, V3, 0, 5, 0, 0);
    packSeg(V3, V4, 0, 6, 0, 0);
    packSeg(V4, V1, 0, 1, 1, 0);

    std::vector<uint8_t> ssectors;
    auto packSSector = [&](uint16_t numsegs, uint16_t firstseg) {
        appendLE<uint16_t>(ssectors, numsegs); appendLE<uint16_t>(ssectors, firstseg);
    };
    packSSector(4, 0);
    packSSector(4, 4);

    std::vector<uint8_t> nodes;
    appendLE<int16_t>(nodes, 32); appendLE<int16_t>(nodes, 0);
    appendLE<int16_t>(nodes, 0); appendLE<int16_t>(nodes, 1);
    for (int16_t v : {64, 0, 0, 32}) appendLE<int16_t>(nodes, v);   // frontBoundingBox
    for (int16_t v : {64, 0, 32, 64}) appendLE<int16_t>(nodes, v);  // backBoundingBox
    appendLE<uint16_t>(nodes, uint16_t(0 | SUBSECTOR_BIT));
    appendLE<uint16_t>(nodes, uint16_t(1 | SUBSECTOR_BIT));

    std::vector<uint8_t> things;
    auto packThing = [&](int16_t x, int16_t y, int16_t angle, int16_t type, int16_t flags) {
        appendLE<int16_t>(things, x); appendLE<int16_t>(things, y);
        appendLE<int16_t>(things, angle); appendLE<int16_t>(things, type); appendLE<int16_t>(things, flags);
    };
    packThing(16, 32, 0, 1, 7);        // 플레이어 시작.
    packThing(48, 32, 180, 3004, 7);   // Zombieman.

    // DMX 사운드 lump 하나 (무기 발사음 재생 테스트용).
    std::vector<uint8_t> dspistol;
    appendLE<uint16_t>(dspistol, 3);
    appendLE<uint16_t>(dspistol, 11025);
    appendLE<uint32_t>(dspistol, 4);
    for (uint8_t b : {10, 20, 30, 40}) dspistol.push_back(b);

    return Doom::buildWadBytes({
        {MAP_NAME, {}},
        {"THINGS", things},
        {"LINEDEFS", linedefs},
        {"SIDEDEFS", sidedefs},
        {"VERTEXES", vertexes},
        {"SEGS", segs},
        {"SSECTORS", ssectors},
        {"NODES", nodes},
        {"SECTORS", sectors},
        {"DSPISTOL", dspistol},
    });
}

}  // namespace DoomFixtures
