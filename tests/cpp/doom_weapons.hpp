// examples/doom/weapons.md 의 # Domain과 전체 무기 로스터 참조 구현 (C++17).
#pragma once
#include "doom_actors.hpp"
#include <functional>
#include <map>
#include <string>

namespace Doom {

struct WeaponType {
    std::string name;
    std::string ammoType;  // 빈 문자열이면 탄약 없음(fist/chainsaw).
    int ammoPerShot = 0;
    State* upState = nullptr;
    State* downState = nullptr;
    State* readyState = nullptr;
    State* attackState = nullptr;
    State* flashState = nullptr;
    std::function<int(std::function<int()>)> damage;  // rng() -> 0..7
    std::vector<std::unique_ptr<State>> states;

    State* addState(std::string sprite, int frame, int duration, State* nextState = nullptr) {
        states.push_back(std::make_unique<State>(State{std::move(sprite), frame, duration, nullptr, nextState}));
        return states.back().get();
    }
};

struct PlayerWeapon {
    std::shared_ptr<WeaponType> type;
    State* state;
    int ticsRemaining;

    explicit PlayerWeapon(std::shared_ptr<WeaponType> t) : type(std::move(t)) {
        state = type->readyState;
        ticsRemaining = state->duration;
    }

    // spp-source: examples/doom/weapons.md#Domain.Class:Doom.PlayerWeapon.setState
    // 무기 State의 action은 이 참조 구현에서 쓰지 않는다 — 발사 판정은
    // game.md의 Feature.발사_입력_처리가 절차적으로 직접 수행한다.
    void setState(State* newState) {
        state = newState;
        ticsRemaining = newState->duration;
    }

    void tick() {
        if (state->duration == -1) return;
        ticsRemaining--;
        if (ticsRemaining <= 0) setState(state->nextState);
    }
};

inline std::shared_ptr<WeaponType> makeWeapon(const std::string& name, const std::string& ammoType,
                                               int ammoPerShot,
                                               std::function<int(std::function<int()>)> damage,
                                               bool meleeLike = false) {
    auto w = std::make_shared<WeaponType>();
    w->name = name;
    w->ammoType = ammoType;
    w->ammoPerShot = ammoPerShot;
    w->damage = std::move(damage);

    std::string spr = name.substr(0, 4);
    State* ready = w->addState(spr, 0, -1);
    ready->nextState = ready;
    State* flash = meleeLike ? nullptr : w->addState(spr, 5, 4, ready);
    State* attack = w->addState(spr, 1, 4, flash ? flash : ready);
    State* up = w->addState(spr, 2, 6, ready);
    State* down = w->addState(spr, 3, 6, nullptr);

    w->readyState = ready;
    w->attackState = attack;
    w->flashState = flash;
    w->upState = up;
    w->downState = down;
    return w;
}

inline int bulletDamage(std::function<int()> rng) { return (rng() % 3 + 1) * 5; }
inline int fistDamage(std::function<int()> rng) { return (rng() % 10 + 1) * 2; }
inline int rocketDirectDamage(std::function<int()> rng) { return 20 + rng() % 133; }
inline int plasmaDamage(std::function<int()> rng) { return (5 + rng() % 8) + (5 + rng() % 8); }
inline int bfgDamage(std::function<int()> rng) { return 100 + rng() % 701; }

inline const std::map<std::string, std::shared_ptr<WeaponType>>& weaponTypes() {
    static const std::map<std::string, std::shared_ptr<WeaponType>> registry = [] {
        std::map<std::string, std::shared_ptr<WeaponType>> reg;
        reg["fist"] = makeWeapon("fist", "", 0, fistDamage, true);
        reg["chainsaw"] = makeWeapon("chainsaw", "", 0, fistDamage, true);
        reg["pistol"] = makeWeapon("pistol", "bullets", 1, bulletDamage);
        reg["shotgun"] = makeWeapon("shotgun", "shells", 1, [](std::function<int()> rng) {
            int total = 0;
            for (int i = 0; i < 7; i++) total += bulletDamage(rng);
            return total;
        });
        reg["chaingun"] = makeWeapon("chaingun", "bullets", 1, bulletDamage);
        reg["rocketLauncher"] = makeWeapon("rocketLauncher", "rockets", 1, rocketDirectDamage);
        reg["plasmaRifle"] = makeWeapon("plasmaRifle", "cells", 1, plasmaDamage);
        reg["bfg9000"] = makeWeapon("bfg9000", "cells", 40, bfgDamage);
        return reg;
    }();
    return registry;
}

}  // namespace Doom
