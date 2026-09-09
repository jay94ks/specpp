"""examples/doom/savegame.md 의 # Domain(Doom.SaveGame) 참조 구현."""
import copy

from doom_game import Game


class SaveGame:
    def __init__(self, description, mapName, player, activeSpecials, activeSpecialsSectorIndex,
                 lightFlashes, lightFlashesSectorIndex, otherActors,
                 sectorFloorHeights, sectorCeilingHeights, sectorLightLevels,
                 killCount, itemCount, secretCount, levelTimeTics):
        self.description = description
        self.mapName = mapName
        self.player = player
        self.activeSpecials = activeSpecials
        self.activeSpecialsSectorIndex = activeSpecialsSectorIndex
        self.lightFlashes = lightFlashes
        self.lightFlashesSectorIndex = lightFlashesSectorIndex
        self.otherActors = otherActors
        self.sectorFloorHeights = sectorFloorHeights
        self.sectorCeilingHeights = sectorCeilingHeights
        self.sectorLightLevels = sectorLightLevels
        self.killCount = killCount
        self.itemCount = itemCount
        self.secretCount = secretCount
        self.levelTimeTics = levelTimeTics

    # spp-source: examples/doom/savegame.md#Domain.Class:Doom.SaveGame.Save
    @staticmethod
    def Save(game, description):
        def sectorIndex(sector):
            for i, s in enumerate(game.map.sectors):
                if s is sector:
                    return i
            return -1

        return SaveGame(
            description=description,
            mapName=game.map.name,
            player=copy.deepcopy(game.player),
            activeSpecials=copy.deepcopy(game.specials),
            activeSpecialsSectorIndex=[sectorIndex(mover.sector) for mover in game.specials],
            lightFlashes=copy.deepcopy(game.lightFlashes),
            lightFlashesSectorIndex=[sectorIndex(lf.sector) for lf in game.lightFlashes],
            otherActors=copy.deepcopy([a for a in game.actors if a is not game.player.actor]),
            sectorFloorHeights=[s.floorHeight for s in game.map.sectors],
            sectorCeilingHeights=[s.ceilingHeight for s in game.map.sectors],
            sectorLightLevels=[s.lightLevel for s in game.map.sectors],
            killCount=game.killCount,
            itemCount=game.itemCount,
            secretCount=game.secretCount,
            levelTimeTics=game.tic,
        )

    # spp-source: examples/doom/savegame.md#Domain.Class:Doom.SaveGame.restore
    def restore(self, wad):
        # savegame.md는 "mapName으로 맵을 다시 불러온다"고만 규정한다 — 이 wad는
        # 그 맵을 다시 불러오는 데 필요한 원본 WAD 참조를 넘겨주는 구현상의 필요다.
        game = Game.Start(wad, self.mapName, rng=None)

        # 문/바닥/천장 등 특수 효과가 진행 중이던 섹터의 실제 높이·조명도 맵 자체의
        # 상태이므로 함께 복원한다 — SectorMover만 복제해서는 부활하지 않는다.
        for i, sector in enumerate(game.map.sectors):
            if i < len(self.sectorFloorHeights):
                sector.floorHeight = self.sectorFloorHeights[i]
                sector.ceilingHeight = self.sectorCeilingHeights[i]
                sector.lightLevel = self.sectorLightLevels[i]

        game.player = copy.deepcopy(self.player)
        otherActors = copy.deepcopy(self.otherActors)
        game.actors = [game.player.actor] + otherActors

        game.specials = copy.deepcopy(self.activeSpecials)
        for mover, idx in zip(game.specials, self.activeSpecialsSectorIndex):
            if idx >= 0:
                mover.sector = game.map.sectors[idx]  # 복사본이 아닌 새로 불러온 맵의 실제 섹터로 다시 낀다.

        game.lightFlashes = copy.deepcopy(self.lightFlashes)
        for lf, idx in zip(game.lightFlashes, self.lightFlashesSectorIndex):
            if idx >= 0:
                lf.sector = game.map.sectors[idx]

        game.killCount = self.killCount
        game.itemCount = self.itemCount
        game.secretCount = self.secretCount
        game.tic = self.levelTimeTics
        return game
