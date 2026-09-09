// examples/doom/map.md 의 # Domain(Doom.Map 네임스페이스) 참조 구현 (C++17).
#pragma once
#include "doom_wad.hpp"
#include <cstring>
#include <memory>
#include <stdexcept>
#include <variant>
#include <vector>

namespace Doom::Map {

constexpr uint16_t SUBSECTOR_BIT = 0x8000;

struct Vertex {
    float x, y;
};

struct Sector {
    float floorHeight, ceilingHeight;
    std::string floorTexture, ceilingTexture;
    int lightLevel, special, tag;
};

struct SideDef {
    float textureOffsetX, textureOffsetY;
    std::string topTexture, bottomTexture, middleTexture;
    Sector* sector;
};

struct LineDef {
    static constexpr uint16_t SECRET_FLAG = 0x20;

    Vertex* v1;
    Vertex* v2;
    int flags, special, tag;
    SideDef* frontSide;
    SideDef* backSide = nullptr;  // null이면 통과할 수 없다(불변식).

    bool isPassable() const { return backSide != nullptr; }
    bool isSecret() const { return (flags & SECRET_FLAG) != 0; }
};

struct Thing {
    float x, y, angle;
    int type, flags;
};

struct Seg {
    Vertex* v1;
    Vertex* v2;
    float angle;
    LineDef* lineDef;
    int side;
    float offset;
};

struct Subsector {
    std::vector<Seg*> segs;
    Sector* sector;
};

struct BspNode {
    float x, y, dx, dy;
    std::variant<BspNode*, Subsector*> frontChild;
    std::variant<BspNode*, Subsector*> backChild;
    std::array<float, 4> frontBoundingBox;  // top, bottom, left, right
    std::array<float, 4> backBoundingBox;

    // spp-source: examples/doom/map.md#Domain.Class:Doom.Map.BspNode.PointOnSide
    static int PointOnSide(float x, float y, const BspNode& node) {
        float dx = x - node.x;
        float dy = y - node.y;
        float cross = node.dx * dy - node.dy * dx;
        return cross <= 0 ? 1 : 0;
    }

    // spp-source: examples/doom/map.md#Domain.Class:Doom.Map.BspNode.FindSubsector
    static Subsector* FindSubsector(float x, float y, std::variant<BspNode*, Subsector*> root) {
        while (std::holds_alternative<BspNode*>(root)) {
            BspNode* node = std::get<BspNode*>(root);
            int side = PointOnSide(x, y, *node);
            root = (side == 1) ? node->backChild : node->frontChild;
        }
        return std::get<Subsector*>(root);
    }
};

class MapData {
public:
    std::string name;
    std::vector<std::unique_ptr<Vertex>> vertexStorage;
    std::vector<std::unique_ptr<Sector>> sectorStorage;
    std::vector<std::unique_ptr<SideDef>> sideDefStorage;
    std::vector<std::unique_ptr<LineDef>> lineDefStorage;
    std::vector<std::unique_ptr<Thing>> thingStorage;
    std::vector<std::unique_ptr<Seg>> segStorage;
    std::vector<std::unique_ptr<Subsector>> subsectorStorage;
    std::vector<std::unique_ptr<BspNode>> nodeStorage;

    std::vector<Vertex*> vertices;
    std::vector<LineDef*> lineDefs;
    std::vector<Sector*> sectors;
    std::vector<Subsector*> subsectors;
    std::variant<BspNode*, Subsector*> bspRoot;
    std::vector<Thing*> things;

    static std::string decodeName(const char* raw, size_t n) {
        std::string s(raw, n);
        auto pos = s.find('\0');
        if (pos != std::string::npos) s.resize(pos);
        return s;
    }

    // spp-source: examples/doom/map.md#Domain.Class:Doom.Map.Load
    static MapData Load(const Doom::WadFile& wad, const std::string& mapName) {
        MapData m;
        m.name = mapName;
        int mapIdx = wad.findLump(mapName);
        if (mapIdx < 0) throw std::runtime_error("map not found: " + mapName);

        static const char* order[] = {"THINGS", "LINEDEFS", "SIDEDEFS", "VERTEXES",
                                       "SEGS", "SSECTORS", "NODES", "SECTORS"};
        auto lumpAfter = [&](const char* name) {
            for (int i = 0; i < 8; i++) {
                if (std::string(order[i]) == name) return wad.readLump(mapIdx + 1 + i);
            }
            throw std::runtime_error("unknown lump order name");
        };

        auto vtxData = lumpAfter("VERTEXES");
        for (size_t off = 0; off + 4 <= vtxData.size(); off += 4) {
            int16_t x, y;
            std::memcpy(&x, vtxData.data() + off, 2);
            std::memcpy(&y, vtxData.data() + off + 2, 2);
            m.vertexStorage.push_back(std::make_unique<Vertex>(Vertex{float(x), float(y)}));
            m.vertices.push_back(m.vertexStorage.back().get());
        }

        auto secData = lumpAfter("SECTORS");
        for (size_t off = 0; off + 26 <= secData.size(); off += 26) {
            int16_t floorH, ceilH, light, special, tag;
            std::memcpy(&floorH, secData.data() + off, 2);
            std::memcpy(&ceilH, secData.data() + off + 2, 2);
            std::string floorTex = decodeName(reinterpret_cast<const char*>(secData.data() + off + 4), 8);
            std::string ceilTex = decodeName(reinterpret_cast<const char*>(secData.data() + off + 12), 8);
            std::memcpy(&light, secData.data() + off + 20, 2);
            std::memcpy(&special, secData.data() + off + 22, 2);
            std::memcpy(&tag, secData.data() + off + 24, 2);
            m.sectorStorage.push_back(std::make_unique<Sector>(
                Sector{float(floorH), float(ceilH), floorTex, ceilTex, light, special, tag}));
            m.sectors.push_back(m.sectorStorage.back().get());
        }

        auto sideData = lumpAfter("SIDEDEFS");
        std::vector<SideDef*> sidedefs;
        for (size_t off = 0; off + 30 <= sideData.size(); off += 30) {
            int16_t offX, offY, secIdx;
            std::memcpy(&offX, sideData.data() + off, 2);
            std::memcpy(&offY, sideData.data() + off + 2, 2);
            std::string top = decodeName(reinterpret_cast<const char*>(sideData.data() + off + 4), 8);
            std::string bottom = decodeName(reinterpret_cast<const char*>(sideData.data() + off + 12), 8);
            std::string mid = decodeName(reinterpret_cast<const char*>(sideData.data() + off + 20), 8);
            std::memcpy(&secIdx, sideData.data() + off + 28, 2);
            m.sideDefStorage.push_back(std::make_unique<SideDef>(
                SideDef{float(offX), float(offY), top, bottom, mid, m.sectors[secIdx]}));
            sidedefs.push_back(m.sideDefStorage.back().get());
        }

        auto lineData = lumpAfter("LINEDEFS");
        for (size_t off = 0; off + 14 <= lineData.size(); off += 14) {
            uint16_t v1i, v2i, flags, special, tag, sideFront, sideBack;
            std::memcpy(&v1i, lineData.data() + off, 2);
            std::memcpy(&v2i, lineData.data() + off + 2, 2);
            std::memcpy(&flags, lineData.data() + off + 4, 2);
            std::memcpy(&special, lineData.data() + off + 6, 2);
            std::memcpy(&tag, lineData.data() + off + 8, 2);
            std::memcpy(&sideFront, lineData.data() + off + 10, 2);
            std::memcpy(&sideBack, lineData.data() + off + 12, 2);
            SideDef* front = (sideFront != 0xFFFF) ? sidedefs[sideFront] : nullptr;
            SideDef* back = (sideBack != 0xFFFF) ? sidedefs[sideBack] : nullptr;
            m.lineDefStorage.push_back(std::make_unique<LineDef>(
                LineDef{m.vertices[v1i], m.vertices[v2i], flags, special, tag, front, back}));
            m.lineDefs.push_back(m.lineDefStorage.back().get());
        }

        auto thingData = lumpAfter("THINGS");
        for (size_t off = 0; off + 10 <= thingData.size(); off += 10) {
            int16_t x, y, angle, type, flags;
            std::memcpy(&x, thingData.data() + off, 2);
            std::memcpy(&y, thingData.data() + off + 2, 2);
            std::memcpy(&angle, thingData.data() + off + 4, 2);
            std::memcpy(&type, thingData.data() + off + 6, 2);
            std::memcpy(&flags, thingData.data() + off + 8, 2);
            m.thingStorage.push_back(std::make_unique<Thing>(
                Thing{float(x), float(y), float(angle), type, flags}));
            m.things.push_back(m.thingStorage.back().get());
        }

        auto segData = lumpAfter("SEGS");
        std::vector<Seg*> segs;
        for (size_t off = 0; off + 12 <= segData.size(); off += 12) {
            uint16_t v1i, v2i, lineIdx;
            int16_t angle, side, segOffset;
            std::memcpy(&v1i, segData.data() + off, 2);
            std::memcpy(&v2i, segData.data() + off + 2, 2);
            std::memcpy(&angle, segData.data() + off + 4, 2);
            std::memcpy(&lineIdx, segData.data() + off + 6, 2);
            std::memcpy(&side, segData.data() + off + 8, 2);
            std::memcpy(&segOffset, segData.data() + off + 10, 2);
            m.segStorage.push_back(std::make_unique<Seg>(Seg{
                m.vertices[v1i], m.vertices[v2i], float(angle), m.lineDefs[lineIdx], side, float(segOffset)}));
            segs.push_back(m.segStorage.back().get());
        }

        auto ssectorData = lumpAfter("SSECTORS");
        for (size_t off = 0; off + 4 <= ssectorData.size(); off += 4) {
            uint16_t numsegs, firstseg;
            std::memcpy(&numsegs, ssectorData.data() + off, 2);
            std::memcpy(&firstseg, ssectorData.data() + off + 2, 2);
            std::vector<Seg*> these(segs.begin() + firstseg, segs.begin() + firstseg + numsegs);
            Sector* sector = m.sectors.empty() ? nullptr : m.sectors[0];
            if (!these.empty()) {
                Seg* first = these[0];
                sector = (first->side == 1) ? first->lineDef->backSide->sector
                                             : first->lineDef->frontSide->sector;
            }
            m.subsectorStorage.push_back(std::make_unique<Subsector>(Subsector{these, sector}));
            m.subsectors.push_back(m.subsectorStorage.back().get());
        }

        auto nodeData = lumpAfter("NODES");
        struct RawNode {
            float x, y, dx, dy;
            std::array<float, 4> frontBbox, backBbox;
            uint16_t c0, c1;
        };
        std::vector<RawNode> rawNodes;
        for (size_t off = 0; off + 28 <= nodeData.size(); off += 28) {
            int16_t x, y, dx, dy, bbox[8];
            uint16_t c0, c1;
            std::memcpy(&x, nodeData.data() + off, 2);
            std::memcpy(&y, nodeData.data() + off + 2, 2);
            std::memcpy(&dx, nodeData.data() + off + 4, 2);
            std::memcpy(&dy, nodeData.data() + off + 6, 2);
            for (int i = 0; i < 8; i++) std::memcpy(&bbox[i], nodeData.data() + off + 8 + i * 2, 2);
            std::memcpy(&c0, nodeData.data() + off + 24, 2);
            std::memcpy(&c1, nodeData.data() + off + 26, 2);
            rawNodes.push_back(RawNode{
                float(x), float(y), float(dx), float(dy),
                {float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])},
                {float(bbox[4]), float(bbox[5]), float(bbox[6]), float(bbox[7])},
                c0, c1});
        }

        m.nodeStorage.resize(rawNodes.size());
        for (size_t i = 0; i < rawNodes.size(); i++) {
            m.nodeStorage[i] = std::make_unique<BspNode>();
        }
        auto resolveChild = [&](uint16_t childId) -> std::variant<BspNode*, Subsector*> {
            if (childId & SUBSECTOR_BIT) return m.subsectors[childId & ~SUBSECTOR_BIT];
            return m.nodeStorage[childId].get();
        };
        for (size_t i = 0; i < rawNodes.size(); i++) {
            auto& rn = rawNodes[i];
            BspNode* node = m.nodeStorage[i].get();
            node->x = rn.x; node->y = rn.y; node->dx = rn.dx; node->dy = rn.dy;
            node->frontBoundingBox = rn.frontBbox;
            node->backBoundingBox = rn.backBbox;
            node->frontChild = resolveChild(rn.c0);
            node->backChild = resolveChild(rn.c1);
        }
        if (!rawNodes.empty()) {
            m.bspRoot = m.nodeStorage.back().get();
        } else if (!m.subsectors.empty()) {
            m.bspRoot = m.subsectors[0];
        }

        return m;
    }
};

}  // namespace Doom::Map
