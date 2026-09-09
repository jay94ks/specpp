// examples/doom/ai.md 의 # Behavior(A_Look/A_Chase/A_FaceTarget 등) 참조 구현 (C++17).
#pragma once
#include "doom_actors.hpp"
#include <cmath>
#include <functional>
#include <vector>

namespace Doom {

inline float crossProduct(std::pair<float, float> o, std::pair<float, float> a, std::pair<float, float> b) {
    return (a.first - o.first) * (b.second - o.second) - (a.second - o.second) * (b.first - o.first);
}

inline bool segmentsIntersect(std::pair<float, float> p1, std::pair<float, float> p2,
                               std::pair<float, float> p3, std::pair<float, float> p4) {
    float d1 = crossProduct(p3, p4, p1);
    float d2 = crossProduct(p3, p4, p2);
    float d3 = crossProduct(p1, p2, p3);
    float d4 = crossProduct(p1, p2, p4);
    bool cond1 = (d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0);
    bool cond2 = (d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0);
    return cond1 && cond2;
}

// spp-source: examples/doom/ai.md#Constraints (시야 판정)
inline bool hasLineOfSight(float x1, float y1, float x2, float y2, const std::vector<Map::LineDef*>& lineDefs) {
    for (auto* line : lineDefs) {
        if (line->isPassable()) continue;
        if (segmentsIntersect({x1, y1}, {x2, y2}, {line->v1->x, line->v1->y}, {line->v2->x, line->v2->y})) {
            return false;
        }
    }
    return true;
}

// spp-source: examples/doom/ai.md#Feature:_대기_중_플레이어_탐지_(A_Look)
inline bool lookForPlayers(Actor* actor, const std::vector<Player*>& players,
                            const std::vector<Map::LineDef*>& lineDefs) {
    for (auto* player : players) {
        if (player->actor->removed || player->health <= 0) continue;
        if (hasLineOfSight(actor->x, actor->y, player->actor->x, player->actor->y, lineDefs)) {
            actor->target = player->actor.get();
            if (actor->type->seeState) actor->setState(actor->type->seeState);
            return true;
        }
    }
    return false;
}

inline float distanceBetween(const Actor* a, const Actor* b) {
    return std::hypot(a->x - b->x, a->y - b->y);
}

// spp-source: examples/doom/ai.md#Feature:_목표_바라보기_(A_FaceTarget)
inline void faceTarget(Actor* actor) {
    if (!actor->target) return;
    actor->angle = std::atan2(actor->target->y - actor->y, actor->target->x - actor->x) * 180.0f / 3.14159265f;
}

inline bool checkMeleeRange(Actor* actor) {
    if (!actor->target || !actor->type->meleeState) return false;
    return distanceBetween(actor, actor->target) <= actor->type->radius + actor->target->type->radius + 20;
}

inline bool checkMissileRange(Actor* actor, std::function<double()> rng, double baseChance = 0.2) {
    if (!actor->target || !actor->type->missileState) return false;
    float dist = distanceBetween(actor, actor->target);
    double chance = std::min(0.9, baseChance + 200.0 / std::max(dist, 1.0f) * 0.1);
    return rng() < chance;
}

// spp-source: examples/doom/ai.md#Feature:_근접_공격_판정
inline void meleeAttack(Actor* actor, std::function<int(std::function<int()>)> damageFn,
                         std::function<int()> rng,
                         std::function<void(Actor*, int, Actor*)> dealDamage) {
    faceTarget(actor);
    if (actor->target && checkMeleeRange(actor)) {
        dealDamage(actor->target, damageFn(rng), actor);
    }
}

// spp-source: examples/doom/ai.md#Feature:_원거리_공격_판정 (즉발 명중형)
inline void hitscanAttack(Actor* actor, std::function<int(std::function<int()>)> damageFn,
                           std::function<int()> rng,
                           std::function<void(Actor*, int, Actor*)> dealDamage,
                           const std::vector<Map::LineDef*>& lineDefs) {
    faceTarget(actor);
    Actor* target = actor->target;
    if (!target) return;
    if (hasLineOfSight(actor->x, actor->y, target->x, target->y, lineDefs)) {
        dealDamage(target, damageFn(rng), actor);
    }
}

// spp-source: examples/doom/ai.md#Feature:_고통과_죽음_(A_Pain_/_A_Fall_계열)
inline std::string painAndDeath(Actor* actor, std::function<double()> rng) {
    if (actor->health > 0) {
        if (actor->type->painState && rng() < actor->type->painChance / 256.0) {
            actor->setState(actor->type->painState);
        }
        return "pain";
    }
    actor->setState(actor->type->deathState);
    actor->flags &= ~MF_SOLID;
    return "death";
}

}  // namespace Doom
