// examples/doom/savegame.md 의 # Domain(Doom.SaveGame) 참조 구현 (C++17).
#pragma once
#include "doom_game.hpp"
#include <algorithm>
#include <map>
#include <memory>
#include <vector>

namespace Doom {

// Actor 하나를 복제한다 — type/state는 MobjType이 소유하는 불변 청사진이라 그대로
// 공유 참조하고, sector는 remap(새로 불러온 맵의 대응 섹터)로 바꿔 낀다. target은
// 이후 restore()에서 old->new 맵으로 다시 연결한다.
inline std::shared_ptr<Actor> cloneActor(const Actor& src, Map::Sector* remappedSector) {
    auto a = std::make_shared<Actor>();
    a->type = src.type;
    a->x = src.x; a->y = src.y; a->z = src.z; a->angle = src.angle;
    a->momX = src.momX; a->momY = src.momY; a->momZ = src.momZ;
    a->state = src.state;
    a->ticsRemaining = src.ticsRemaining;
    a->health = src.health;
    a->flags = src.flags;
    a->target = nullptr;  // restore()에서 채운다.
    a->sector = remappedSector;
    a->removed = src.removed;
    return a;
}

inline int sectorIndexOf(const Map::MapData& map, Map::Sector* sector) {
    for (size_t i = 0; i < map.sectors.size(); i++)
        if (map.sectors[i] == sector) return static_cast<int>(i);
    return -1;
}

struct SaveGame {
    std::string description;
    std::string mapName;

    // 플레이어 상태(값 스냅샷).
    int playerHealth, playerArmor, playerArmorClass;
    std::map<std::string, int> playerAmmo;
    std::vector<std::string> playerKeys;
    std::string playerCurrentWeapon;
    float playerActorX, playerActorY, playerActorZ, playerActorAngle;
    int playerActorHealth;

    std::vector<std::shared_ptr<Actor>> otherActors;  // 저장 시점 맵 섹터를 그대로 가리킨다.
    std::vector<std::shared_ptr<SectorMover>> activeSpecials;
    std::vector<int> activeSpecialsSectorIndex;  // 새 맵으로 복원할 때 다시 찾을 섹터 인덱스.
    std::vector<std::shared_ptr<LightFlash>> lightFlashes;
    std::vector<int> lightFlashesSectorIndex;
    // 문/바닥/천장 등 특수 효과가 진행 중이던 섹터의 실제 높이·조명도 맵 자체의
    // 상태이므로 함께 저장한다 — SectorMover를 복제하는 것만으로는 부활하지 않는다.
    std::vector<float> sectorFloorHeights, sectorCeilingHeights;
    std::vector<int> sectorLightLevels;
    int killCount, itemCount, secretCount, levelTimeTics;

    // spp-source: examples/doom/savegame.md#Domain.Class:Doom.SaveGame.Save
    static SaveGame Save(Game& game, const std::string& description) {
        SaveGame s;
        s.description = description;
        s.mapName = game.map.name;
        s.playerHealth = game.player->health;
        s.playerArmor = game.player->armor;
        s.playerArmorClass = game.player->armorClass;
        s.playerAmmo = game.player->ammo;
        s.playerKeys = game.player->keys;
        s.playerCurrentWeapon = game.player->currentWeapon;
        s.playerActorX = game.player->actor->x;
        s.playerActorY = game.player->actor->y;
        s.playerActorZ = game.player->actor->z;
        s.playerActorAngle = game.player->actor->angle;
        s.playerActorHealth = game.player->actor->health;

        for (auto& a : game.actors) {
            if (a.get() == game.player->actor.get()) continue;
            s.otherActors.push_back(cloneActor(*a, a->sector));
        }
        for (auto& mover : game.specials) {
            s.activeSpecials.push_back(mover);
            s.activeSpecialsSectorIndex.push_back(sectorIndexOf(game.map, mover->getSector()));
        }
        for (auto& lf : game.lightFlashes) {
            s.lightFlashes.push_back(lf);
            s.lightFlashesSectorIndex.push_back(sectorIndexOf(game.map, lf->sector));
        }
        for (auto* sector : game.map.sectors) {
            s.sectorFloorHeights.push_back(sector->floorHeight);
            s.sectorCeilingHeights.push_back(sector->ceilingHeight);
            s.sectorLightLevels.push_back(sector->lightLevel);
        }

        s.killCount = game.killCount;
        s.itemCount = game.itemCount;
        s.secretCount = game.secretCount;
        s.levelTimeTics = game.tic;
        return s;
    }

    // spp-source: examples/doom/savegame.md#Domain.Class:Doom.SaveGame.restore
    // savegame.md는 "mapName으로 맵을 다시 불러온다"고만 규정한다 — 이 wad는 그 맵을
    // 다시 불러오는 데 필요한 원본 WAD 참조를 넘겨주는 구현상의 필요다.
    std::shared_ptr<Game> restore(const WadFile& wad) const {
        auto game = Game::Start(wad, mapName, [] { return 0.0; });

        for (size_t i = 0; i < game->map.sectors.size() && i < sectorFloorHeights.size(); i++) {
            game->map.sectors[i]->floorHeight = sectorFloorHeights[i];
            game->map.sectors[i]->ceilingHeight = sectorCeilingHeights[i];
            game->map.sectors[i]->lightLevel = sectorLightLevels[i];
        }

        game->player->health = playerHealth;
        game->player->armor = playerArmor;
        game->player->armorClass = playerArmorClass;
        game->player->ammo = playerAmmo;
        game->player->keys = playerKeys;
        game->player->currentWeapon = playerCurrentWeapon;
        game->player->actor->x = playerActorX;
        game->player->actor->y = playerActorY;
        game->player->actor->z = playerActorZ;
        game->player->actor->angle = playerActorAngle;
        game->player->actor->health = playerActorHealth;

        std::vector<std::shared_ptr<Actor>> restoredActors = {game->player->actor};
        std::map<const Actor*, Actor*> oldToNew;
        for (auto& old : otherActors) {
            auto* subsector = Map::BspNode::FindSubsector(old->x, old->y, game->map.bspRoot);
            auto fresh = cloneActor(*old, subsector->sector);
            oldToNew[old.get()] = fresh.get();
            restoredActors.push_back(fresh);
        }
        for (size_t i = 0; i < otherActors.size(); i++) {
            if (otherActors[i]->target && oldToNew.count(otherActors[i]->target)) {
                restoredActors[i + 1]->target = oldToNew[otherActors[i]->target];
            }
        }
        game->actors = restoredActors;

        for (size_t i = 0; i < activeSpecials.size(); i++) {
            int idx = activeSpecialsSectorIndex[i];
            Map::Sector* newSector = (idx >= 0) ? game->map.sectors[idx] : activeSpecials[i]->getSector();
            game->specials.push_back(activeSpecials[i]->cloneOnto(newSector));
        }
        for (size_t i = 0; i < lightFlashes.size(); i++) {
            int idx = lightFlashesSectorIndex[i];
            Map::Sector* newSector = (idx >= 0) ? game->map.sectors[idx] : lightFlashes[i]->sector;
            game->lightFlashes.push_back(lightFlashes[i]->cloneOnto(newSector));
        }

        game->killCount = killCount;
        game->itemCount = itemCount;
        game->secretCount = secretCount;
        game->tic = levelTimeTics;
        return game;
    }
};

}  // namespace Doom
