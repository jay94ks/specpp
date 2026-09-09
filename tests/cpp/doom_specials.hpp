// examples/doom/specials.md 의 # Domain/# Behavior 참조 구현 (C++17).
#pragma once
#include "doom_map.hpp"
#include <algorithm>
#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace Doom {

struct SectorMover {
    virtual ~SectorMover() = default;
    virtual bool tick() = 0;  // 계속 진행 중이면 true.
    // savegame.md 저장/복원용: 같은 값을 갖되 newSector(새로 불러온 맵의 대응 섹터)를
    // 가리키는 복사본을 만든다.
    virtual std::shared_ptr<SectorMover> cloneOnto(Map::Sector* newSector) const = 0;
    virtual Map::Sector* getSector() const = 0;
};

class Door : public SectorMover {
public:
    Map::Sector* sector;
    std::string kind;  // "Open" | "Close" | "OpenThenClose" | "CloseThenOpen"
    float targetCeilingHeight;
    float speed;
    int waitTicsRemaining = 0;
    std::optional<std::string> requiredKey;

private:
    bool closing_;
    float openHeight_;
    float closeHeight_;

public:
    Door(Map::Sector* sec, std::string k, float target, float spd = 4.0f,
         std::optional<std::string> key = std::nullopt)
        : sector(sec), kind(std::move(k)), targetCeilingHeight(target), speed(spd), requiredKey(std::move(key)) {
        closing_ = (kind == "Close" || kind == "CloseThenOpen");
        openHeight_ = targetCeilingHeight;
        closeHeight_ = sector->floorHeight;
    }

    bool tick() override {
        if (closing_) {
            sector->ceilingHeight = std::max(closeHeight_, sector->ceilingHeight - speed);
            if (sector->ceilingHeight <= closeHeight_) {
                if (kind == "CloseThenOpen") { closing_ = false; return true; }
                return false;
            }
            return true;
        } else {
            sector->ceilingHeight = std::min(openHeight_, sector->ceilingHeight + speed);
            if (sector->ceilingHeight >= openHeight_) {
                if (kind == "OpenThenClose") {
                    if (waitTicsRemaining > 0) { waitTicsRemaining--; return true; }
                    closing_ = true;
                    return true;
                }
                return false;
            }
            return true;
        }
    }

    std::shared_ptr<SectorMover> cloneOnto(Map::Sector* newSector) const override {
        auto d = std::make_shared<Door>(newSector, kind, targetCeilingHeight, speed, requiredKey);
        d->waitTicsRemaining = waitTicsRemaining;
        d->closing_ = closing_;
        return d;
    }

    Map::Sector* getSector() const override { return sector; }
};

class FloorMover : public SectorMover {
public:
    Map::Sector* sector;
    float targetFloorHeight, speed;
    bool crush;

    FloorMover(Map::Sector* sec, float target, float spd = 1.0f, bool cr = false)
        : sector(sec), targetFloorHeight(target), speed(spd), crush(cr) {}

    bool tick() override {
        if (sector->floorHeight < targetFloorHeight) {
            sector->floorHeight = std::min(targetFloorHeight, sector->floorHeight + speed);
        } else {
            sector->floorHeight = std::max(targetFloorHeight, sector->floorHeight - speed);
        }
        return sector->floorHeight != targetFloorHeight;
    }

    std::shared_ptr<SectorMover> cloneOnto(Map::Sector* newSector) const override {
        return std::make_shared<FloorMover>(newSector, targetFloorHeight, speed, crush);
    }

    Map::Sector* getSector() const override { return sector; }
};

class Ceiling : public SectorMover {
public:
    Map::Sector* sector;
    float topHeight, bottomHeight, speed;
    std::string direction;  // "Up" | "Down"
    bool repeats, crush;

    Ceiling(Map::Sector* sec, float top, float bottom, float spd = 1.0f,
            std::string dir = "Down", bool rep = false, bool cr = false)
        : sector(sec), topHeight(top), bottomHeight(bottom), speed(spd), direction(std::move(dir)),
          repeats(rep), crush(cr) {}

    bool tick() override {
        if (direction == "Down") {
            sector->ceilingHeight = std::max(bottomHeight, sector->ceilingHeight - speed);
            if (sector->ceilingHeight <= bottomHeight) {
                if (repeats) { direction = "Up"; return true; }
                return false;
            }
        } else {
            sector->ceilingHeight = std::min(topHeight, sector->ceilingHeight + speed);
            if (sector->ceilingHeight >= topHeight) {
                if (repeats) { direction = "Down"; return true; }
                return false;
            }
        }
        return true;
    }

    std::shared_ptr<SectorMover> cloneOnto(Map::Sector* newSector) const override {
        auto c = std::make_shared<Ceiling>(newSector, topHeight, bottomHeight, speed, direction, repeats, crush);
        return c;
    }

    Map::Sector* getSector() const override { return sector; }
};

class Platform : public SectorMover {
public:
    Map::Sector* sector;
    float lowHeight, highHeight, speed;
    std::string direction;
    int waitTicsRemaining = 0;
    bool repeatsForever;

    Platform(Map::Sector* sec, float low, float high, float spd = 1.0f,
             std::string dir = "Down", bool repeat = false)
        : sector(sec), lowHeight(low), highHeight(high), speed(spd), direction(std::move(dir)),
          repeatsForever(repeat) {}

    bool tick() override {
        float target = (direction == "Down") ? lowHeight : highHeight;
        if (sector->floorHeight != target) {
            float step = (direction == "Down") ? -speed : speed;
            sector->floorHeight += step;
            if ((step < 0 && sector->floorHeight <= target) || (step > 0 && sector->floorHeight >= target)) {
                sector->floorHeight = target;
            }
            return true;
        }
        if (repeatsForever) {
            direction = (direction == "Down") ? "Up" : "Down";
            return true;
        }
        return false;
    }

    std::shared_ptr<SectorMover> cloneOnto(Map::Sector* newSector) const override {
        auto p = std::make_shared<Platform>(newSector, lowHeight, highHeight, speed, direction, repeatsForever);
        p->waitTicsRemaining = waitTicsRemaining;
        return p;
    }

    Map::Sector* getSector() const override { return sector; }
};

class LightFlash {
public:
    Map::Sector* sector;
    int maxLight, minLight;
    std::function<double()> rng;
    int ticsUntilNextChange;

    LightFlash(Map::Sector* sec, int maxL, int minL, std::function<double()> r, int startTics = 4)
        : sector(sec), maxLight(maxL), minLight(minL), rng(std::move(r)), ticsUntilNextChange(startTics) {}

    bool tick() {
        ticsUntilNextChange--;
        if (ticsUntilNextChange <= 0) {
            sector->lightLevel = (rng() < 0.5) ? maxLight : minLight;
            ticsUntilNextChange = 1 + int(rng() * 8);
        }
        return true;
    }

    std::shared_ptr<LightFlash> cloneOnto(Map::Sector* newSector) const {
        auto f = std::make_shared<LightFlash>(newSector, maxLight, minLight, rng, ticsUntilNextChange);
        return f;
    }
};

// spp-source: examples/doom/specials.md#Behavior.Feature:_선을_밟아_특수_효과_발동
template <typename Actor, typename MakeMover, typename IsLockedCheck>
inline std::shared_ptr<SectorMover> triggerLineSpecial(Map::LineDef* lineDef, const std::string& trigger,
                                                         Actor* activator,
                                                         std::vector<std::shared_ptr<SectorMover>>& activeMovers,
                                                         MakeMover makeMover, IsLockedCheck isLockedCheck) {
    if (lineDef->special == 0) return nullptr;

    auto doorPreview = isLockedCheck(lineDef);
    if (doorPreview && doorPreview->requiredKey) {
        bool hasKey = activator != nullptr &&
                      std::find(activator->keys.begin(), activator->keys.end(), *doorPreview->requiredKey) !=
                          activator->keys.end();
        if (!hasKey) return nullptr;
    }

    auto mover = makeMover(lineDef);
    activeMovers.push_back(mover);
    if (trigger != "Walkover") lineDef->special = 0;
    return mover;
}

// spp-source: examples/doom/specials.md#Behavior.Feature:_특수_효과_진행
inline std::vector<std::shared_ptr<SectorMover>> advanceSpecials(
    const std::vector<std::shared_ptr<SectorMover>>& activeMovers) {
    std::vector<std::shared_ptr<SectorMover>> stillActive;
    for (auto& mover : activeMovers) {
        if (mover->tick()) stillActive.push_back(mover);
    }
    return stillActive;
}

}  // namespace Doom
