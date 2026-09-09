// examples/doom/wad.md 의 # Domain(Doom.WadLump/Doom.WadFile/Doom.Palette) 참조 구현 (C++17).
#pragma once
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace Doom {

struct WadLump {
    std::string name;
    int32_t offset;
    int32_t size;
};

inline std::string upper(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(), ::toupper);
    return s;
}

class WadFile {
    std::vector<uint8_t> data_;

public:
    std::vector<WadLump> lumps;

    // spp-source: examples/doom/wad.md#Domain.Class:Doom.WadFile
    explicit WadFile(const std::string& path) {
        std::ifstream f(path, std::ios::binary);
        if (!f) throw std::runtime_error("cannot open wad: " + path);
        data_.assign(std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>());

        char magic[5] = {0};
        std::memcpy(magic, data_.data(), 4);
        int32_t numlumps, infotableofs;
        std::memcpy(&numlumps, data_.data() + 4, 4);
        std::memcpy(&infotableofs, data_.data() + 8, 4);
        std::string magicStr(magic);
        if (magicStr != "IWAD" && magicStr != "PWAD") {
            throw std::runtime_error("not a WAD file (magic=" + magicStr + ")");
        }

        for (int32_t i = 0; i < numlumps; i++) {
            size_t off = infotableofs + i * 16;
            int32_t offset, size;
            std::memcpy(&offset, data_.data() + off, 4);
            std::memcpy(&size, data_.data() + off + 4, 4);
            char nameBuf[9] = {0};
            std::memcpy(nameBuf, data_.data() + off + 8, 8);
            lumps.push_back({std::string(nameBuf), offset, size});
        }
    }

    int findLump(const std::string& name) const {
        std::string target = upper(name);
        int found = -1;
        for (size_t i = 0; i < lumps.size(); i++) {
            if (upper(lumps[i].name) == target) found = static_cast<int>(i);
        }
        return found;
    }

    std::vector<uint8_t> readLump(int index) const {
        const WadLump& l = lumps[index];
        return std::vector<uint8_t>(data_.begin() + l.offset, data_.begin() + l.offset + l.size);
    }
};

class Palette {
    std::array<std::array<uint8_t, 3>, 256> colors_{};

public:
    // spp-source: examples/doom/wad.md#Domain.Class:Doom.Palette
    explicit Palette(const std::vector<uint8_t>& playpalBytes) {
        for (int i = 0; i < 256; i++) {
            colors_[i] = {playpalBytes[i * 3], playpalBytes[i * 3 + 1], playpalBytes[i * 3 + 2]};
        }
    }

    std::array<uint8_t, 3> colorAt(int index) const { return colors_[index]; }
};

// 테스트용 헬퍼: [(name, bytes), ...] 로 WAD 파일 바이트를 만든다.
inline std::vector<uint8_t> buildWadBytes(const std::vector<std::pair<std::string, std::vector<uint8_t>>>& lumps) {
    std::vector<uint8_t> body;
    for (auto& [name, bytes] : lumps) body.insert(body.end(), bytes.begin(), bytes.end());

    std::vector<uint8_t> directory;
    int32_t offset = 12;
    for (auto& [name, bytes] : lumps) {
        auto appendI32 = [&](int32_t v) {
            auto p = reinterpret_cast<uint8_t*>(&v);
            directory.insert(directory.end(), p, p + 4);
        };
        appendI32(offset);
        appendI32(static_cast<int32_t>(bytes.size()));
        char nameBuf[8] = {0};
        std::memcpy(nameBuf, name.c_str(), std::min<size_t>(8, name.size()));
        directory.insert(directory.end(), nameBuf, nameBuf + 8);
        offset += static_cast<int32_t>(bytes.size());
    }

    std::vector<uint8_t> out;
    out.insert(out.end(), {'P', 'W', 'A', 'D'});
    int32_t numLumps = static_cast<int32_t>(lumps.size());
    int32_t dirOffset = 12 + static_cast<int32_t>(body.size());
    auto appendI32 = [&](int32_t v) {
        auto p = reinterpret_cast<uint8_t*>(&v);
        out.insert(out.end(), p, p + 4);
    };
    appendI32(numLumps);
    appendI32(dirOffset);
    out.insert(out.end(), body.begin(), body.end());
    out.insert(out.end(), directory.begin(), directory.end());
    return out;
}

}  // namespace Doom
