// examples/doom/game.md 의 # Domain(Doom.Game)/# Behavior 참조 구현 (C++17).
#pragma once
#include "doom_ai.hpp"
#include "doom_automap.hpp"
#include "doom_hud.hpp"
#include "doom_map.hpp"
#include "doom_menu.hpp"
#include "doom_netplay.hpp"
#include "doom_sound.hpp"
#include "doom_specials.hpp"
#include "doom_weapons.hpp"
#include <cmath>
#include <map>
#include <memory>
#include <random>
#include <vector>

namespace Doom {

constexpr float STEP_LIMIT = 24.0f;
constexpr int EXIT_SPECIAL = 11;

inline std::shared_ptr<MobjType> playerMobjType() {
    static std::shared_ptr<MobjType> t = [] {
        auto mt = std::make_shared<MobjType>();
        mt->name = "Player";
        mt->spawnHealth = 100;
        mt->radius = 16;
        mt->height = 56;
        mt->speed = 0;
        mt->flags = MF_SOLID | MF_SHOOTABLE;
        mt->spawnState = mt->addState("PLAY", 0, -1);
        return mt;
    }();
    return t;
}

inline const std::map<int, std::shared_ptr<MobjType>>& doomednumToMonster() {
    static const std::map<int, std::shared_ptr<MobjType>> reg = [] {
        std::map<int, std::shared_ptr<MobjType>> m;
        for (auto& [name, type] : monsterTypes()) m[type->doomednum] = type;
        return m;
    }();
    return reg;
}

inline bool circleIntersectsSegment(float cx, float cy, float radius, float x1, float y1, float x2, float y2) {
    float dx = x2 - x1, dy = y2 - y1;
    float lengthSq = dx * dx + dy * dy;
    float t = 0.0f;
    if (lengthSq > 0) t = std::max(0.0f, std::min(1.0f, ((cx - x1) * dx + (cy - y1) * dy) / lengthSq));
    float px = x1 + t * dx, py = y1 + t * dy;
    return (cx - px) * (cx - px) + (cy - py) * (cy - py) < radius * radius;
}

inline bool lineBlocks(Map::LineDef* line, Actor* actor) {
    if (!line->isPassable()) return true;
    auto* front = line->frontSide->sector;
    auto* back = line->backSide->sector;
    if (std::abs(front->floorHeight - back->floorHeight) > STEP_LIMIT) return true;
    float openBottom = std::max(front->floorHeight, back->floorHeight);
    float openTop = std::min(front->ceilingHeight, back->ceilingHeight);
    return (openTop - openBottom) < actor->type->height;
}

struct Game {
    Map::MapData map;
    std::function<double()> rng;
    std::function<int()> rngByte;  // P_Random()%8 에 대응하는 0~7 정수.

    std::vector<std::shared_ptr<Actor>> actors;
    std::vector<std::shared_ptr<SectorMover>> specials;
    std::vector<std::shared_ptr<LightFlash>> lightFlashes;
    std::unique_ptr<SoundSystem> soundSystem;
    Hud hud;
    AutoMap automap;
    MenuStack menuStack;
    int tic = 0;
    int killCount = 0, itemCount = 0, secretCount = 0;
    int totalKills = 0, totalItems = 0;
    bool exited = false;

    std::shared_ptr<Player> player;
    std::shared_ptr<PlayerWeapon> playerWeapon;
    std::unique_ptr<TicCmdSource> ticCmdSource;
    const WadFile* wad = nullptr;

    std::vector<Actor*> monsters() {
        std::vector<Actor*> out;
        for (auto& a : actors)
            if (a.get() != player->actor.get()) out.push_back(a.get());
        return out;
    }

    bool canMove(Actor* actor, float newX, float newY) {
        for (auto* line : map.lineDefs) {
            if (lineBlocks(line, actor) &&
                circleIntersectsSegment(newX, newY, actor->type->radius, line->v1->x, line->v1->y,
                                         line->v2->x, line->v2->y)) {
                return false;
            }
        }
        for (auto& other : actors) {
            if (other.get() == actor || other->removed || !(other->flags & MF_SOLID)) continue;
            if ((actor->flags & MF_MISSILE) && (other->flags & MF_MISSILE)) continue;
            float distSq = (newX - other->x) * (newX - other->x) + (newY - other->y) * (newY - other->y);
            float minDist = actor->type->radius + other->type->radius;
            if (distSq < minDist * minDist) return false;
        }
        return true;
    }

    // spp-source: examples/doom/game.md#Behavior.Feature:_이동과_충돌
    bool moveAndCollide(Actor* actor, float deltaX, float deltaY) {
        bool moved = false;
        if (canMove(actor, actor->x + deltaX, actor->y + deltaY)) {
            actor->x += deltaX;
            actor->y += deltaY;
            moved = true;
        } else {
            if (deltaX != 0 && canMove(actor, actor->x + deltaX, actor->y)) { actor->x += deltaX; moved = true; }
            if (deltaY != 0 && canMove(actor, actor->x, actor->y + deltaY)) { actor->y += deltaY; moved = true; }
        }
        auto* newSubsector = Map::BspNode::FindSubsector(actor->x, actor->y, map.bspRoot);
        if (newSubsector->sector != actor->sector) {
            actor->sector = newSubsector->sector;
            if (!(actor->flags & MF_NOGRAVITY)) actor->z = newSubsector->sector->floorHeight;
        }
        return moved;
    }

    // spp-source: examples/doom/game.md#Behavior.Feature:_전투_판정
    std::string dealDamage(Actor* target, int damage, Actor* inflictor = nullptr) {
        if (!(target->flags & MF_SHOOTABLE)) return "";

        if (player && target == player->actor.get()) {
            if (player->armor > 0) {
                double ratio = (player->armorClass == 1) ? (1.0 / 3.0) : 0.5;
                int absorbed = std::min(player->armor, int(damage * ratio));
                player->armor -= absorbed;
                damage -= absorbed;
            }
            player->health = std::max(0, player->health - damage);
            target->health = player->health;
        } else {
            target->health = std::max(0, target->health - damage);
        }

        if (inflictor && !target->target) target->target = inflictor;

        std::string result = painAndDeath(target, rng);
        if (result == "death" && (target->type->flags & MF_COUNTKILL)) killCount++;
        return result;
    }

    Actor* firstActorInCrosshair(float coneDeg = 10.0f, float maxRange = 1024.0f) {
        Actor* actor = player->actor.get();
        Actor* best = nullptr;
        float bestDist = 0;
        for (auto& other : actors) {
            if (other.get() == actor || other->removed || !(other->flags & MF_SHOOTABLE)) continue;
            float dx = other->x - actor->x, dy = other->y - actor->y;
            float dist = std::hypot(dx, dy);
            if (dist == 0 || dist > maxRange) continue;
            float angleTo = std::atan2(dy, dx) * 180.0f / 3.14159265f;
            float diff = std::abs(std::fmod(angleTo - actor->angle + 180.0f + 360.0f, 360.0f) - 180.0f);
            if (diff > coneDeg) continue;
            if (!hasLineOfSight(actor->x, actor->y, other->x, other->y, map.lineDefs)) continue;
            if (!best || dist < bestDist) { best = other.get(); bestDist = dist; }
        }
        return best;
    }

    // spp-source: examples/doom/game.md#Behavior.Feature:_발사_입력_처리
    bool fireWeaponInput() {
        auto weaponType = weaponTypes().at(player->currentWeapon);
        if (!weaponType->ammoType.empty() && player->ammo[weaponType->ammoType] < weaponType->ammoPerShot) {
            return false;
        }
        playerWeapon->setState(weaponType->attackState);
        std::string lumpName = "DS" + weaponType->name.substr(0, std::min<size_t>(6, weaponType->name.size()));
        std::transform(lumpName.begin(), lumpName.end(), lumpName.begin(), ::toupper);
        soundSystem->playEffect(lumpName, player->actor.get(), player.get());

        if (!weaponType->ammoType.empty()) player->ammo[weaponType->ammoType] -= weaponType->ammoPerShot;

        Actor* target = firstActorInCrosshair();
        if (target) dealDamage(target, weaponType->damage(rngByte), player->actor.get());
        return true;
    }

    // spp-source: examples/doom/game.md#Behavior.Feature:_사용_키_처리
    std::shared_ptr<SectorMover> useKey(
        std::function<std::shared_ptr<SectorMover>(Map::LineDef*)> makeMover,
        std::function<std::shared_ptr<Door>(Map::LineDef*)> isLockedCheck) {
        Actor* actor = player->actor.get();
        constexpr float reach = 64.0f;
        float rad = actor->angle * 3.14159265f / 180.0f;
        float fx = actor->x + std::cos(rad) * reach, fy = actor->y + std::sin(rad) * reach;

        Map::LineDef* nearest = nullptr;
        float nearestDist = 0;
        for (auto* line : map.lineDefs) {
            if (line->special == 0) continue;
            if (segmentsIntersect({actor->x, actor->y}, {fx, fy}, {line->v1->x, line->v1->y},
                                   {line->v2->x, line->v2->y})) {
                float midX = (line->v1->x + line->v2->x) / 2, midY = (line->v1->y + line->v2->y) / 2;
                float dist = std::hypot(midX - actor->x, midY - actor->y);
                if (!nearest || dist < nearestDist) { nearest = line; nearestDist = dist; }
            }
        }
        if (!nearest) return nullptr;
        return triggerLineSpecial(nearest, "Use", player.get(), specials, makeMover, isLockedCheck);
    }

    // spp-source: examples/doom/game.md#Behavior.Feature:_맵_종료_조건
    bool checkMapExit(Map::LineDef* crossedLine) {
        if (crossedLine->special == EXIT_SPECIAL) {
            exited = true;
            return true;
        }
        return false;
    }

    void aiStep(Actor* actor) {
        std::vector<Player*> players = {player.get()};
        if (!actor->target || actor->target->removed || actor->target->health <= 0) {
            lookForPlayers(actor, players, map.lineDefs);
        } else if (checkMeleeRange(actor)) {
            meleeAttack(actor, [](std::function<int()> r) { return (r() + 1) * 3; }, rngByte,
                        [&](Actor* t, int d, Actor* i) { dealDamage(t, d, i); });
        } else if (checkMissileRange(actor, rng)) {
            hitscanAttack(actor, [](std::function<int()> r) { return (r() % 3 + 1) * 5; }, rngByte,
                          [&](Actor* t, int d, Actor* i) { dealDamage(t, d, i); }, map.lineDefs);
        } else if (actor->target) {
            float dx = actor->target->x - actor->x, dy = actor->target->y - actor->y;
            float dist = std::hypot(dx, dy);
            if (dist > 1e-6f) {
                float step = actor->type->speed;
                moveAndCollide(actor, dx / dist * step, dy / dist * step);
            }
        }
        actor->tick();
    }

    // spp-source: examples/doom/game.md#Behavior.Feature:_틱_진행
    void tickOnce(const RawPlayerInput& raw) {
        if (menuStack.isOpen()) return;

        auto cmd = ticCmdSource->collect(tic, raw);
        if (!cmd) return;

        Actor* actor = player->actor.get();
        actor->angle += float(cmd->angleTurn);
        player->viewAngle = actor->angle;
        float forward = actor->angle * 3.14159265f / 180.0f;
        float right = forward + 3.14159265f / 2.0f;
        float dx = std::cos(forward) * cmd->forwardMove * 0.01f + std::cos(right) * cmd->sideMove * 0.01f;
        float dy = std::sin(forward) * cmd->forwardMove * 0.01f + std::sin(right) * cmd->sideMove * 0.01f;
        if (dx != 0 || dy != 0) moveAndCollide(actor, dx, dy);

        if (cmd->buttons & 0x1) fireWeaponInput();

        for (auto* a : monsters()) {
            if (a->removed) continue;
            aiStep(a);
        }

        playerWeapon->tick();
        specials = advanceSpecials(specials);
        for (auto& lf : lightFlashes) lf->tick();

        auto* subsector = Map::BspNode::FindSubsector(actor->x, actor->y, map.bspRoot);
        automap.revealFromSubsector(subsector);

        soundSystem->updateListenerPosition(player.get());
        tic++;
    }

    // spp-source: examples/doom/game.md#Domain.Class:Doom.Game.Start
    static std::shared_ptr<Game> Start(const WadFile& wad, const std::string& mapName,
                                        std::function<double()> customRng = nullptr) {
        auto game = std::make_shared<Game>();
        game->map = Map::MapData::Load(wad, mapName);
        game->wad = &wad;
        game->rng = customRng ? customRng : [] {
            static std::mt19937 gen{12345};
            static std::uniform_real_distribution<double> dist(0.0, 1.0);
            return dist(gen);
        };
        game->rngByte = [g = game.get()] { return int(g->rng() * 8); };
        game->soundSystem = std::make_unique<SoundSystem>(&wad);

        std::shared_ptr<Actor> playerActor;
        for (auto* thing : game->map.things) {
            auto* subsector = Map::BspNode::FindSubsector(thing->x, thing->y, game->map.bspRoot);
            Map::Sector* sector = subsector->sector;
            if (thing->type == 1) {
                playerActor = Actor::Spawn(playerMobjType(), thing->x, thing->y, thing->angle, sector);
                game->actors.push_back(playerActor);
            } else if (doomednumToMonster().count(thing->type)) {
                auto mtype = doomednumToMonster().at(thing->type);
                auto a = Actor::Spawn(mtype, thing->x, thing->y, thing->angle, sector);
                game->actors.push_back(a);
                if (mtype->flags & MF_COUNTKILL) game->totalKills++;
            }
        }
        if (!playerActor) throw std::runtime_error("map has no player start (Thing.type == 1)");

        game->player = std::make_shared<Player>(playerActor);
        game->playerWeapon = std::make_shared<PlayerWeapon>(weaponTypes().at("pistol"));
        game->ticCmdSource = std::make_unique<TicCmdSource>(TicCmdSource::Local);
        return game;
    }
};

}  // namespace Doom
