// examples/doom/actors.md 의 # Domain 참조 구현 (C++17): State/MobjType/Actor/Player와
// 전체 몬스터·아이템·발사체 로스터.
#pragma once
#include "doom_map.hpp"
#include <algorithm>
#include <functional>
#include <map>
#include <memory>
#include <string>
#include <vector>

namespace Doom {

constexpr uint32_t MF_SOLID = 1u << 0;
constexpr uint32_t MF_SHOOTABLE = 1u << 1;
constexpr uint32_t MF_NOGRAVITY = 1u << 2;
constexpr uint32_t MF_MISSILE = 1u << 3;
constexpr uint32_t MF_COUNTKILL = 1u << 4;
constexpr uint32_t MF_SPECIAL = 1u << 5;
constexpr uint32_t MF_FLOAT = 1u << 6;
constexpr uint32_t MF_SHADOW = 1u << 7;

struct Actor;

struct State {
    std::string sprite;
    int frame;
    int duration;
    std::function<void(Actor&)> action;
    State* nextState = nullptr;
};

struct MobjType {
    std::string name;
    int spawnHealth = 0;
    float radius = 0, height = 0, speed = 0;
    uint32_t flags = 0;
    State* spawnState = nullptr;
    State* seeState = nullptr;
    State* painState = nullptr;
    State* meleeState = nullptr;
    State* missileState = nullptr;
    State* deathState = nullptr;
    int doomednum = -1;
    int painChance = 256;
    int mass = 100;
    std::vector<std::unique_ptr<State>> states;  // 이 MobjType이 소유하는 모든 State.

    State* addState(std::string sprite, int frame, int duration, State* nextState = nullptr,
                     std::function<void(Actor&)> action = nullptr) {
        states.push_back(std::make_unique<State>(State{std::move(sprite), frame, duration, std::move(action), nextState}));
        return states.back().get();
    }
};

struct Actor {
    std::shared_ptr<MobjType> type;
    float x = 0, y = 0, z = 0, angle = 0;
    float momX = 0, momY = 0, momZ = 0;
    State* state = nullptr;
    int ticsRemaining = 0;
    int health = 0;
    uint32_t flags = 0;
    Actor* target = nullptr;
    Map::Sector* sector = nullptr;
    bool removed = false;

    // spp-source: examples/doom/actors.md#Domain.Class:Doom.Actor.Spawn
    static std::shared_ptr<Actor> Spawn(std::shared_ptr<MobjType> type, float x, float y,
                                         float angle = 0, Map::Sector* sector = nullptr) {
        auto a = std::make_shared<Actor>();
        a->type = type;
        a->x = x;
        a->y = y;
        a->z = sector ? sector->floorHeight : 0.0f;
        a->angle = angle;
        a->health = type->spawnHealth;
        a->flags = type->flags;
        a->sector = sector;
        a->setState(type->spawnState);
        return a;
    }

    void setState(State* newState) {
        state = newState;
        if (!newState) {
            removed = true;
            return;
        }
        ticsRemaining = newState->duration;
        if (newState->action) newState->action(*this);
    }

    void tick() {
        x += momX;
        y += momY;
        z += momZ;
        if (!state) return;
        if (state->duration == -1) return;
        ticsRemaining--;
        if (ticsRemaining <= 0) setState(state->nextState);
    }
};

struct Player {
    std::shared_ptr<Actor> actor;
    int armor = 0;
    int armorClass = 0;
    std::map<std::string, int> ammo = {{"bullets", 50}, {"shells", 0}, {"rockets", 0}, {"cells", 0}};
    std::vector<std::string> keys;
    std::map<std::string, int> powerups;
    std::string currentWeapon = "pistol";
    float viewAngle = 0;
    int health = 100;
    int maxHealth = 100;
    bool hasBackpack = false;

    explicit Player(std::shared_ptr<Actor> a) : actor(std::move(a)) {
        if (actor) health = actor->health;
    }
};

// ---------------------------------------------------------------------------
// 전체 몬스터 로스터 (실제 mobjinfo[] 수치).
// ---------------------------------------------------------------------------
struct MonsterStat {
    std::string name, sprite, attack;
    int doomednum, health, painChance, mass;
    float radius, height, speed;
    uint32_t extraFlags = 0;
};

inline const std::vector<MonsterStat>& monsterStats() {
    static const std::vector<MonsterStat> table = {
        {"Zombieman", "POSS", "missile", 3004, 20, 200, 100, 20, 56, 8},
        {"Shotgun Guy", "SPOS", "missile", 9, 30, 170, 100, 20, 56, 8},
        {"Chaingunner", "CPOS", "missile", 65, 70, 170, 100, 20, 56, 8},
        {"Wolfenstein SS", "SSWV", "missile", 84, 50, 170, 100, 20, 56, 8},
        {"Imp", "TROO", "both", 3001, 60, 200, 100, 20, 56, 8},
        {"Demon", "SARG", "melee", 3002, 150, 180, 400, 30, 56, 10},
        {"Spectre", "SARG", "melee", 58, 150, 180, 400, 30, 56, 10, MF_SHADOW},
        {"Lost Soul", "SKUL", "missile", 3006, 100, 256, 50, 16, 56, 8, MF_FLOAT | MF_NOGRAVITY},
        {"Cacodemon", "HEAD", "missile", 3005, 400, 128, 400, 31, 56, 8, MF_FLOAT | MF_NOGRAVITY},
        {"Hell Knight", "BOS2", "both", 69, 500, 50, 1000, 24, 64, 8},
        {"Baron of Hell", "BOSS", "both", 3003, 1000, 50, 1000, 24, 64, 8},
        {"Arachnotron", "BSPI", "missile", 68, 500, 128, 600, 64, 64, 12},
        {"Pain Elemental", "PAIN", "missile", 71, 400, 128, 400, 31, 56, 8, MF_FLOAT | MF_NOGRAVITY},
        {"Revenant", "SKEL", "both", 66, 300, 100, 500, 20, 56, 10},
        {"Mancubus", "FATT", "missile", 67, 600, 80, 1000, 48, 64, 8},
        {"Arch-vile", "VILE", "missile", 64, 700, 10, 500, 20, 56, 15},
        {"Spider Mastermind", "SPID", "missile", 7, 3000, 40, 1000, 128, 100, 12},
        {"Cyberdemon", "CYBR", "missile", 16, 4000, 20, 1000, 40, 110, 16},
    };
    return table;
}

inline std::shared_ptr<MobjType> makeMonsterType(const MonsterStat& s) {
    auto t = std::make_shared<MobjType>();
    t->name = s.name;
    t->spawnHealth = s.health;
    t->radius = s.radius;
    t->height = s.height;
    t->speed = s.speed;
    t->doomednum = s.doomednum;
    t->painChance = s.painChance;
    t->mass = s.mass;
    t->flags = MF_SOLID | MF_SHOOTABLE | MF_COUNTKILL | s.extraFlags;

    State* spawn = t->addState(s.sprite, 0, 10);
    spawn->nextState = spawn;
    State* see = t->addState(s.sprite, 1, 4);
    see->nextState = see;
    t->spawnState = spawn;
    t->seeState = see;
    if (s.painChance > 0) t->painState = t->addState(s.sprite, 6, 3, see);
    State* deathFinal = t->addState(s.sprite, 9, -1, nullptr);
    t->deathState = t->addState(s.sprite, 8, 5, deathFinal);
    if (s.attack == "melee" || s.attack == "both") t->meleeState = t->addState(s.sprite, 5, 8, see);
    if (s.attack == "missile" || s.attack == "both") t->missileState = t->addState(s.sprite, 4, 10, see);
    return t;
}

inline const std::map<std::string, std::shared_ptr<MobjType>>& monsterTypes() {
    static const std::map<std::string, std::shared_ptr<MobjType>> registry = [] {
        std::map<std::string, std::shared_ptr<MobjType>> reg;
        for (auto& s : monsterStats()) reg[s.name] = makeMonsterType(s);
        return reg;
    }();
    return registry;
}

// ---------------------------------------------------------------------------
// 아이템 로스터 (픽업).
// ---------------------------------------------------------------------------
struct ItemPickup {
    std::string name, kind;
    int doomednum;
    std::function<void(Player&)> apply;
};

constexpr int TICS_PER_SECOND = 35;

inline const std::vector<ItemPickup>& itemPickups() {
    static const std::vector<ItemPickup> table = [] {
        std::vector<ItemPickup> v;
        auto heal = [](int amount, int cap) {
            return [amount, cap](Player& p) { p.health = std::min(cap, p.health + amount); };
        };
        auto armor = [](int amount, int cls, int cap = 200) {
            return [amount, cls, cap](Player& p) { p.armor = std::min(cap, p.armor + amount); p.armorClass = cls; };
        };
        auto armorBonus = [](int amount, int cap = 200) {
            return [amount, cap](Player& p) { p.armor = std::min(cap, p.armor + amount); };
        };
        auto ammo = [](std::string kind, int amount) {
            return [kind, amount](Player& p) { p.ammo[kind] += amount; };
        };
        auto weapon = [](std::string name) {
            return [name](Player& p) { p.currentWeapon = name; };
        };
        auto key = [](std::string color) {
            return [color](Player& p) {
                if (std::find(p.keys.begin(), p.keys.end(), color) == p.keys.end()) p.keys.push_back(color);
            };
        };
        auto backpack = [](Player& p) {
            p.ammo["bullets"] += 10; p.ammo["shells"] += 4; p.ammo["rockets"] += 1; p.ammo["cells"] += 20;
            p.hasBackpack = true;
        };
        auto berserk = [](Player& p) {
            if (p.health < 100) p.health = 100;
            p.powerups["berserk"] = -1;
        };
        auto timedPowerup = [](std::string name, int seconds) {
            return [name, seconds](Player& p) { p.powerups[name] = seconds * TICS_PER_SECOND; };
        };

        v.push_back({"Stimpack", "health", 2011, heal(10, 100)});
        v.push_back({"Medikit", "health", 2012, heal(25, 100)});
        v.push_back({"Health Bonus", "health", 2014, heal(1, 200)});
        v.push_back({"Soulsphere", "health", 2013, heal(100, 200)});
        v.push_back({"Green Armor", "armor", 2018, armor(100, 1)});
        v.push_back({"Blue Armor", "armor", 2019, armor(200, 2)});
        v.push_back({"Armor Bonus", "armor", 2015, armorBonus(1)});
        v.push_back({"Clip", "ammo", 2007, ammo("bullets", 10)});
        v.push_back({"Box of Bullets", "ammo", 2048, ammo("bullets", 50)});
        v.push_back({"Shells", "ammo", 2008, ammo("shells", 4)});
        v.push_back({"Box of Shells", "ammo", 2049, ammo("shells", 20)});
        v.push_back({"Rocket", "ammo", 2010, ammo("rockets", 1)});
        v.push_back({"Box of Rockets", "ammo", 2046, ammo("rockets", 5)});
        v.push_back({"Cell", "ammo", 2047, ammo("cells", 20)});
        v.push_back({"Cell Pack", "ammo", 17, ammo("cells", 100)});
        v.push_back({"Backpack", "ammo", 8, backpack});
        v.push_back({"Chainsaw", "weapon", 2005, weapon("chainsaw")});
        v.push_back({"Shotgun", "weapon", 2001, weapon("shotgun")});
        v.push_back({"Chaingun", "weapon", 2002, weapon("chaingun")});
        v.push_back({"Rocket Launcher", "weapon", 2003, weapon("rocketLauncher")});
        v.push_back({"Plasma Rifle", "weapon", 2004, weapon("plasmaRifle")});
        v.push_back({"BFG9000", "weapon", 2006, weapon("bfg9000")});
        v.push_back({"Blue Keycard", "key", 5, key("blue")});
        v.push_back({"Yellow Keycard", "key", 6, key("yellow")});
        v.push_back({"Red Keycard", "key", 13, key("red")});
        v.push_back({"Blue Skull Key", "key", 40, key("blue")});
        v.push_back({"Yellow Skull Key", "key", 39, key("yellow")});
        v.push_back({"Red Skull Key", "key", 38, key("red")});
        v.push_back({"Berserk", "powerup", 2023, berserk});
        v.push_back({"Invulnerability", "powerup", 2022, timedPowerup("invulnerability", 30)});
        v.push_back({"Partial Invisibility", "powerup", 2024, timedPowerup("partialInvisibility", 60)});
        v.push_back({"Radiation Suit", "powerup", 2025, timedPowerup("radiationSuit", 60)});
        v.push_back({"Computer Area Map", "powerup", 2026, timedPowerup("computerAreaMap", 0)});
        v.push_back({"Light Amplification Visor", "powerup", 2045, timedPowerup("lightAmpVisor", 120)});
        return v;
    }();
    return table;
}

inline const ItemPickup* findItemByName(const std::string& name) {
    for (auto& item : itemPickups())
        if (item.name == name) return &item;
    return nullptr;
}

// ---------------------------------------------------------------------------
// 몬스터 발사체 로스터.
// ---------------------------------------------------------------------------
struct ProjectileType {
    std::string name, sprite;
    float speed, radius, height;
    std::function<int(std::function<int()>)> damage;  // rng() -> 0..7
};

inline const std::vector<ProjectileType>& projectileTypes() {
    static const std::vector<ProjectileType> table = {
        {"Imp Fireball", "BAL1", 10, 6, 8, [](auto rng) { return (rng() + 1) * 3; }},
        {"Cacodemon Fireball", "BAL2", 10, 6, 8, [](auto rng) { return (rng() + 1) * 5; }},
        {"Baron Fireball", "BAL7", 15, 6, 8, [](auto rng) { return (rng() + 1) * 8; }},
        {"Mancubus Fireball", "MANF", 20, 6, 8, [](auto rng) { return (rng() + 1) * 8; }},
        {"Arachnotron Plasma", "APLS", 25, 13, 8, [](auto) { return 5; }},
    };
    return table;
}

inline const ProjectileType* findProjectileByName(const std::string& name) {
    for (auto& p : projectileTypes())
        if (p.name == name) return &p;
    return nullptr;
}

// ---------------------------------------------------------------------------
// Feature: 되살리기 (Arch-vile 전용)
// ---------------------------------------------------------------------------
inline Actor* findResurrectable(Actor* archvile, const std::vector<std::shared_ptr<Actor>>& actors) {
    Actor* best = nullptr;
    float bestDistSq = 0;
    for (auto& a : actors) {
        if (a.get() == archvile || a->removed) continue;
        if (!a->type->deathState || a->state != a->type->deathState->nextState) continue;
        if (a->health > 0) continue;
        float dx = a->x - archvile->x, dy = a->y - archvile->y;
        float distSq = dx * dx + dy * dy;
        if (!best || distSq < bestDistSq) { best = a.get(); bestDistSq = distSq; }
    }
    return best;
}

// spp-source: examples/doom/actors.md#Feature:_되살리기_(Arch-vile_전용)
inline void resurrect(Actor* target) {
    target->health = target->type->spawnHealth;
    target->flags |= MF_SOLID;
    target->setState(target->type->seeState ? target->type->seeState : target->type->spawnState);
}

}  // namespace Doom
