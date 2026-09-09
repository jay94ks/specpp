// examples/doom/netplay.md 의 # Domain/# Behavior 참조 구현 (C++17).
#pragma once
#include <cstdint>
#include <cstring>
#include <map>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

namespace Doom {

struct TicCmd {
    int forwardMove = 0, sideMove = 0, angleTurn = 0, buttons = 0;

    bool operator==(const TicCmd& o) const {
        return forwardMove == o.forwardMove && sideMove == o.sideMove &&
               angleTurn == o.angleTurn && buttons == o.buttons;
    }
};

struct RawPlayerInput {
    int forwardMove = 0, sideMove = 0, angleTurn = 0, buttons = 0;
};

// spp-source: examples/doom/netplay.md#Domain.Class:Doom.TicCmd.FromInput
inline TicCmd ticCmdFromInput(const RawPlayerInput& raw) {
    return TicCmd{raw.forwardMove, raw.sideMove, raw.angleTurn, raw.buttons};
}

class NetGame {
public:
    int localPlayerIndex;
    int playerCount;
    std::map<int, std::vector<std::optional<TicCmd>>> pendingTicCmds;
    bool isServer;

    NetGame(int local, int players, bool server = true)
        : localPlayerIndex(local), playerCount(players), isServer(server) {}

    void broadcastLocalTicCmd(int tic, const TicCmd& cmd) { receiveRemoteTicCmd(tic, localPlayerIndex, cmd); }

    void receiveRemoteTicCmd(int tic, int playerIndex, const TicCmd& cmd) {
        auto& slot = pendingTicCmds[tic];
        if (slot.empty()) slot.assign(playerCount, std::nullopt);
        slot[playerIndex] = cmd;
    }

    // spp-source: examples/doom/netplay.md#Domain.Class:Doom.NetGame.isReadyToAdvance
    bool isReadyToAdvance(int tic) const {
        auto it = pendingTicCmds.find(tic);
        if (it == pendingTicCmds.end()) return false;
        for (auto& c : it->second)
            if (!c) return false;
        return true;
    }
};

struct Demo {
    std::string mapName;
    int difficulty;
    std::vector<TicCmd> recordedTicCmds;

    static Demo Load(const std::vector<uint8_t>& bytes) {
        size_t off = 0;
        uint8_t nameLen = bytes[off++];
        std::string mapName(bytes.begin() + off, bytes.begin() + off + nameLen);
        off += nameLen;
        uint8_t difficulty = bytes[off++];
        uint32_t count;
        std::memcpy(&count, bytes.data() + off, 4);
        off += 4;
        std::vector<TicCmd> cmds;
        for (uint32_t i = 0; i < count; i++) {
            int8_t fwd, side; int16_t turn; uint8_t btn;
            std::memcpy(&fwd, bytes.data() + off, 1);
            std::memcpy(&side, bytes.data() + off + 1, 1);
            std::memcpy(&turn, bytes.data() + off + 2, 2);
            std::memcpy(&btn, bytes.data() + off + 4, 1);
            off += 5;
            cmds.push_back(TicCmd{fwd, side, turn, btn});
        }
        return Demo{mapName, difficulty, cmds};
    }

    std::vector<uint8_t> toBytes() const {
        std::vector<uint8_t> out;
        out.push_back(static_cast<uint8_t>(mapName.size()));
        out.insert(out.end(), mapName.begin(), mapName.end());
        out.push_back(static_cast<uint8_t>(difficulty));
        uint32_t count = static_cast<uint32_t>(recordedTicCmds.size());
        auto p = reinterpret_cast<uint8_t*>(&count);
        out.insert(out.end(), p, p + 4);
        for (auto& cmd : recordedTicCmds) {
            int8_t fwd = static_cast<int8_t>(cmd.forwardMove), side = static_cast<int8_t>(cmd.sideMove);
            int16_t turn = static_cast<int16_t>(cmd.angleTurn);
            uint8_t btn = static_cast<uint8_t>(cmd.buttons);
            out.push_back(static_cast<uint8_t>(fwd));
            out.push_back(static_cast<uint8_t>(side));
            auto tp = reinterpret_cast<uint8_t*>(&turn);
            out.insert(out.end(), tp, tp + 2);
            out.push_back(btn);
        }
        return out;
    }
};

class TicCmdSource {
public:
    enum Mode { Local, Record, Playback, Net };

    Mode mode;
    Demo* demo = nullptr;
    NetGame* netGame = nullptr;
    size_t playbackIndex = 0;
    bool playbackFinished = false;

    explicit TicCmdSource(Mode m, Demo* d = nullptr, NetGame* n = nullptr) : mode(m), demo(d), netGame(n) {}

    // spp-source: examples/doom/netplay.md#Feature:_틱_명령_수집(네트워크/로컬_공통)
    std::optional<std::vector<TicCmd>> collectMulti(int tic, const RawPlayerInput& raw) {
        // 멀티플레이 모드에서는 모든 플레이어의 명령 벡터를 돌려준다.
        if (mode != Net) throw std::runtime_error("collectMulti is only for Net mode");
        TicCmd cmd = ticCmdFromInput(raw);
        netGame->broadcastLocalTicCmd(tic, cmd);
        if (!netGame->isReadyToAdvance(tic)) return std::nullopt;
        std::vector<TicCmd> result;
        for (auto& c : netGame->pendingTicCmds[tic]) result.push_back(*c);
        return result;
    }

    std::optional<TicCmd> collect(int tic, const RawPlayerInput& raw) {
        if (mode == Local) return ticCmdFromInput(raw);

        if (mode == Record) {
            TicCmd cmd = ticCmdFromInput(raw);
            demo->recordedTicCmds.push_back(cmd);
            return cmd;
        }

        if (mode == Playback) {
            if (playbackIndex >= demo->recordedTicCmds.size()) {
                playbackFinished = true;
                return std::nullopt;
            }
            return demo->recordedTicCmds[playbackIndex++];
        }

        throw std::runtime_error("use collectMulti() for Net mode");
    }
};

}  // namespace Doom
