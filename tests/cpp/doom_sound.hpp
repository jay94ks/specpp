// examples/doom/sound.md 의 # Domain/# Behavior 참조 구현 (C++17).
#pragma once
#include "doom_actors.hpp"
#include "doom_wad.hpp"
#include <algorithm>
#include <cmath>
#include <cstring>
#include <map>
#include <memory>
#include <stdexcept>
#include <vector>

namespace Doom {

constexpr int MAX_CHANNELS = 8;

struct SoundEffect {
    std::string name;
    int sampleRate;
    std::vector<uint8_t> pcmSamples;

    // spp-source: examples/doom/sound.md#Domain.Class:Doom.SoundEffect.Load
    static SoundEffect Load(const WadFile& wad, const std::string& lumpName) {
        int idx = wad.findLump(lumpName);
        if (idx < 0) throw std::runtime_error("sound lump not found: " + lumpName);
        auto data = wad.readLump(idx);
        uint16_t fmt, sampleRate;
        uint32_t sampleCount;
        std::memcpy(&fmt, data.data(), 2);
        std::memcpy(&sampleRate, data.data() + 2, 2);
        std::memcpy(&sampleCount, data.data() + 4, 4);
        if (fmt != 3) throw std::runtime_error("unexpected DMX format id");
        std::vector<uint8_t> pcm(data.begin() + 8, data.begin() + 8 + sampleCount);
        return SoundEffect{lumpName, sampleRate, pcm};
    }
};

struct PlayingSound {
    std::shared_ptr<SoundEffect> effect;
    float x, y;
    bool positional;
};

class SoundSystem {
    const WadFile* wad_;

public:
    std::map<std::string, std::shared_ptr<SoundEffect>> effectCache;
    std::vector<std::shared_ptr<PlayingSound>> playing;
    int maxChannels = MAX_CHANNELS;

    explicit SoundSystem(const WadFile* wad) : wad_(wad) {}

    void init() { playing.clear(); }

    // spp-source: examples/doom/sound.md#Feature:_효과음_재생
    std::shared_ptr<PlayingSound> playEffect(const std::string& effectName, Actor* source, Player* listener) {
        if (!effectCache.count(effectName)) {
            effectCache[effectName] = std::make_shared<SoundEffect>(SoundEffect::Load(*wad_, effectName));
        }
        auto effect = effectCache[effectName];

        if (static_cast<int>(playing.size()) >= maxChannels) {
            auto farthest = farthestFrom(listener);
            if (farthest) playing.erase(std::find(playing.begin(), playing.end(), farthest));
        }

        std::shared_ptr<PlayingSound> p;
        if (source) {
            p = std::make_shared<PlayingSound>(PlayingSound{effect, source->x, source->y, true});
        } else {
            p = std::make_shared<PlayingSound>(PlayingSound{effect, listener->actor->x, listener->actor->y, false});
        }
        playing.push_back(p);
        return p;
    }

    std::shared_ptr<PlayingSound> farthestFrom(Player* listener) {
        if (playing.empty()) return nullptr;
        float lx = listener->actor->x, ly = listener->actor->y;
        auto it = std::max_element(playing.begin(), playing.end(), [&](auto& a, auto& b) {
            return (a->x - lx) * (a->x - lx) + (a->y - ly) * (a->y - ly) <
                   (b->x - lx) * (b->x - lx) + (b->y - ly) * (b->y - ly);
        });
        return *it;
    }

    void updateListenerPosition(Player*) {}

    float panFor(const std::shared_ptr<PlayingSound>& p, Player* listener) {
        if (!p->positional) return 0.0f;
        float rad = listener->viewAngle * 3.14159265f / 180.0f;
        float fx = std::cos(rad), fy = std::sin(rad);
        float rx = -fy, ry = fx;
        float dx = p->x - listener->actor->x, dy = p->y - listener->actor->y;
        float pan = dx * rx + dy * ry;
        return std::max(-1.0f, std::min(1.0f, pan / 200.0f));
    }
};

}  // namespace Doom
