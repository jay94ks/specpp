// examples/doom/hud.md 의 # Domain/# Behavior 참조 구현 (C++17).
#pragma once
#include "doom_actors.hpp"
#include <optional>
#include <string>

namespace Doom {

class Hud {
public:
    std::string faceFrame = "STFST01";

    // spp-source: examples/doom/hud.md#Feature:_얼굴_표정_갱신
    std::string updateFace(Player& player, std::optional<std::string> justDamagedFromDirection = std::nullopt,
                            bool justKilled = false) {
        double ratio = double(player.health) / std::max(player.maxHealth, 1);

        if (player.health <= 0) {
            faceFrame = "STFDEAD0";
            return faceFrame;
        }

        std::string base;
        if (ratio <= 0.20) base = "STFEVL";
        else if (ratio <= 0.40) base = "STFOUCH";
        else if (ratio <= 0.70) base = "STFKILL";
        else base = "STFST";

        if (justDamagedFromDirection) {
            faceFrame = base + "_HIT_" + *justDamagedFromDirection;
        } else if (justKilled && ratio > 0.20) {
            faceFrame = base + "_GRIN";
        } else {
            faceFrame = base;
        }
        return faceFrame;
    }
};

}  // namespace Doom
