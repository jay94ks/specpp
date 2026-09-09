// examples/doom/intermission.md 의 # Domain/# Behavior 참조 구현 (C++17).
#pragma once
#include <cmath>
#include <optional>
#include <string>

namespace Doom {

struct Intermission {
    std::string finishedMapName;
    std::optional<std::string> nextMapName;
    int killPercent, itemPercent, secretPercent;
    int parTimeTics, playerTimeTics;
};

inline int percentOf(int count, int total) {
    if (total <= 0) return 100;
    return int(std::lround(100.0 * count / total));
}

// spp-source: examples/doom/intermission.md#Feature:_스테이지_클리어_전환
inline Intermission makeIntermission(const std::string& finishedMapName, std::optional<std::string> nextMapName,
                                      int killCount, int totalKills, int itemCount, int totalItems,
                                      int secretCount, int totalSecrets, int parTimeTics, int playerTimeTics) {
    return Intermission{
        finishedMapName, nextMapName,
        percentOf(killCount, totalKills), percentOf(itemCount, totalItems), percentOf(secretCount, totalSecrets),
        parTimeTics, playerTimeTics,
    };
}

}  // namespace Doom
