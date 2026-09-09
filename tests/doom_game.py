"""examples/doom/game.md 의 # Domain(Doom.Game)/# Behavior 참조 구현.

여러 doom_*.py 모듈(actors/weapons/specials/ai/sound/netplay/hud/automap/menu/
intermission)을 하나의 틱 루프로 엮는다.
"""
import math
import random

from doom_actors import (
    Actor, MobjType, Player, State, MF_SOLID, MF_SHOOTABLE, MF_NOGRAVITY,
    MF_MISSILE, MF_COUNTKILL, MF_SPECIAL, MONSTER_TYPES, ITEM_PICKUPS,
    ITEM_TYPES, DOOMEDNUM_TO_ITEM_NAME,
)
from doom_ai import (
    look_for_players, check_melee_range, check_missile_range, melee_attack,
    hitscan_attack, pain_and_death, has_line_of_sight,
)
from doom_automap import AutoMap
from doom_hud import Hud
from doom_map import BspNode, Map
from doom_menu import MenuStack
from doom_netplay import TicCmd, TicCmdSource
from doom_sound import SoundSystem
from doom_specials import advance_specials
from doom_weapons import PlayerWeapon, WEAPON_TYPES

STEP_LIMIT = 24.0
EXIT_SPECIAL = 11  # 원본 S1 Exit Level과 같은 번호.

PLAYER_MOBJ_TYPE = MobjType(
    name="Player", spawnHealth=100, radius=16, height=56, speed=0,
    flags=MF_SOLID | MF_SHOOTABLE, spawnState=State("PLAY", 0, -1),
)

DOOMEDNUM_TO_MONSTER = {t.doomednum: t for t in MONSTER_TYPES.values()}


def _circle_intersects_segment(cx, cy, radius, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        t = 0.0
    else:
        t = max(0.0, min(1.0, ((cx - x1) * dx + (cy - y1) * dy) / length_sq))
    px, py = x1 + t * dx, y1 + t * dy
    return (cx - px) ** 2 + (cy - py) ** 2 < radius * radius


def _line_blocks(line, actor):
    if not line.isPassable:
        return True
    front, back = line.frontSide.sector, line.backSide.sector
    if abs(front.floorHeight - back.floorHeight) > STEP_LIMIT:
        return True
    openBottom = max(front.floorHeight, back.floorHeight)
    openTop = min(front.ceilingHeight, back.ceilingHeight)
    if openTop - openBottom < actor.type.height:
        return True
    return False


def _can_move(actor, newX, newY, lineDefs, actors):
    for line in lineDefs:
        if _line_blocks(line, actor) and _circle_intersects_segment(
            newX, newY, actor.type.radius, line.v1.x, line.v1.y, line.v2.x, line.v2.y
        ):
            return False
    for other in actors:
        if other is actor or other.isRemoved or not (other.flags & MF_SOLID):
            continue
        if (actor.flags & MF_MISSILE) and (other.flags & MF_MISSILE):
            continue
        distSq = (newX - other.x) ** 2 + (newY - other.y) ** 2
        if distSq < (actor.type.radius + other.type.radius) ** 2:
            return False
    return True


# spp-source: examples/doom/game.md#Behavior.Feature:_이동과_충돌
def move_and_collide(game, actor, deltaX, deltaY):
    lineDefs = game.map.lineDefs
    moved = False
    if _can_move(actor, actor.x + deltaX, actor.y + deltaY, lineDefs, game.actors):
        actor.x += deltaX
        actor.y += deltaY
        moved = True
    else:
        if deltaX != 0 and _can_move(actor, actor.x + deltaX, actor.y, lineDefs, game.actors):
            actor.x += deltaX
            moved = True
        if deltaY != 0 and _can_move(actor, actor.x, actor.y + deltaY, lineDefs, game.actors):
            actor.y += deltaY
            moved = True

    newSubsector = BspNode.FindSubsector(actor.x, actor.y, game.map.bspRoot)
    if newSubsector.sector is not actor.sector:
        actor.sector = newSubsector.sector
        if not (actor.flags & MF_NOGRAVITY):
            actor.z = newSubsector.sector.floorHeight

    if game.player is not None and actor is game.player.actor:
        _touch_items(game, actor)

    return moved


# spp-source: examples/doom/game.md#Behavior.Feature:_아이템_획득
def _touch_items(game, actor):
    radius = actor.type.radius
    for item in game.actors:
        if item.isRemoved or not (item.flags & MF_SPECIAL):
            continue
        distSq = (actor.x - item.x) ** 2 + (actor.y - item.y) ** 2
        if distSq >= (radius + item.type.radius) ** 2:
            continue
        ITEM_PICKUPS[item.itemName]["apply"](game.player)
        game.itemCount += 1
        item.setState(None)


# spp-source: examples/doom/game.md#Behavior.Feature:_전투_판정
def deal_damage(game, target, damage, inflictor=None):
    if not (target.flags & MF_SHOOTABLE):
        return None

    if game.player is not None and target is game.player.actor:
        player = game.player
        if player.armor > 0:
            ratio = 1 / 3 if player.armorClass == 1 else 1 / 2
            absorbed = min(player.armor, int(damage * ratio))
            player.armor -= absorbed
            damage -= absorbed
        player.health = max(0, player.health - damage)
        target.health = player.health
    else:
        target.health = max(0, target.health - damage)

    if inflictor is not None and target.target is None:
        target.target = inflictor

    result = pain_and_death(target, game.rng)

    if result == "death" and (target.type.flags & MF_COUNTKILL):
        game.killCount += 1

    return result


def _first_actor_in_crosshair(game, cone_deg=10.0, max_range=1024.0):
    actor = game.player.actor
    best, best_dist = None, None
    for other in game.actors:
        if other is actor or other.isRemoved or not (other.flags & MF_SHOOTABLE):
            continue
        dx, dy = other.x - actor.x, other.y - actor.y
        dist = math.hypot(dx, dy)
        if dist == 0 or dist > max_range:
            continue
        angleTo = math.degrees(math.atan2(dy, dx))
        diff = abs((angleTo - actor.angle + 180) % 360 - 180)
        if diff > cone_deg:
            continue
        if not has_line_of_sight(actor.x, actor.y, other.x, other.y, game.map.lineDefs):
            continue
        if best is None or dist < best_dist:
            best, best_dist = other, dist
    return best


# spp-source: examples/doom/game.md#Behavior.Feature:_발사_입력_처리
def fire_weapon_input(game):
    weaponType = WEAPON_TYPES[game.player.currentWeapon]
    if weaponType.ammoType is not None:
        if game.player.ammo.get(weaponType.ammoType, 0) < weaponType.ammoPerShot:
            return False

    game.playerWeapon.setState(weaponType.attackState)
    game.soundSystem.playEffect(
        f"DS{game.player.currentWeapon.upper()[:6]}", game.player.actor, game.player
    )

    if weaponType.ammoType is not None:
        game.player.ammo[weaponType.ammoType] -= weaponType.ammoPerShot

    target = _first_actor_in_crosshair(game)
    if target is not None:
        deal_damage(game, target, weaponType.damage(game.rngByte), game.player.actor)
    return True


# spp-source: examples/doom/game.md#Behavior.Feature:_사용_키_처리
def use_key(game, make_mover=None, is_locked_check=None):
    from doom_specials import trigger_line_special

    actor = game.player.actor
    from doom_ai import _segments_intersect

    reach = 64.0
    forward = math.radians(actor.angle)
    fx, fy = actor.x + math.cos(forward) * reach, actor.y + math.sin(forward) * reach
    nearest, nearestDist = None, None
    for line in game.map.lineDefs:
        if line.special == 0:
            continue
        v1, v2 = (line.v1.x, line.v1.y), (line.v2.x, line.v2.y)
        if _segments_intersect((actor.x, actor.y), (fx, fy), v1, v2):
            dist = math.hypot((line.v1.x + line.v2.x) / 2 - actor.x,
                               (line.v1.y + line.v2.y) / 2 - actor.y)
            if nearest is None or dist < nearestDist:
                nearest, nearestDist = line, dist
    if nearest is None or make_mover is None:
        return None
    return trigger_line_special(nearest, "Use", actor, game.specials, make_mover, is_locked_check)


# spp-source: examples/doom/game.md#Behavior.Feature:_맵_종료_조건
def check_map_exit(game, crossedLine):
    if crossedLine.special == EXIT_SPECIAL:
        game.exited = True
        return True
    return False


def _pickup_items(game):
    for actor in list(game.actors):
        pass  # 아이템은 이 참조 구현에서 별도 Actor로 스폰하지 않는다(Open Points).


class Game:
    # spp-source: examples/doom/game.md#Domain.Class:Doom.Game.Start
    @staticmethod
    def Start(wad, mapName, rng=None):
        game = Game()
        game.map = Map.Load(wad, mapName)
        game.rng = rng or random.random
        game.rngByte = lambda: int(game.rng() * 8)  # P_Random()%8 에 대응하는 0~7 정수.

        game.actors = []
        game.specials = []
        game.lightFlashes = []
        game.renderer = None
        game.soundSystem = SoundSystem(wad)
        game.netGame = None
        game.demo = None
        game.hud = Hud()
        game.automap = AutoMap()
        game.menuStack = MenuStack()
        game.tic = 0
        game.killCount = 0
        game.itemCount = 0
        game.secretCount = 0
        game.totalKills = 0
        game.totalItems = 0
        game.exited = False
        game.player = None

        playerActor = None
        for thing in game.map.things:
            sector = BspNode.FindSubsector(thing.x, thing.y, game.map.bspRoot).sector
            if thing.type == 1:
                playerActor = Actor.Spawn(PLAYER_MOBJ_TYPE, thing.x, thing.y, thing.angle, sector)
                game.actors.append(playerActor)
            elif thing.type in DOOMEDNUM_TO_MONSTER:
                mtype = DOOMEDNUM_TO_MONSTER[thing.type]
                a = Actor.Spawn(mtype, thing.x, thing.y, thing.angle, sector)
                game.actors.append(a)
                if mtype.flags & MF_COUNTKILL:
                    game.totalKills += 1
            elif thing.type in DOOMEDNUM_TO_ITEM_NAME:
                name = DOOMEDNUM_TO_ITEM_NAME[thing.type]
                a = Actor.Spawn(ITEM_TYPES[name], thing.x, thing.y, thing.angle, sector)
                a.itemName = name
                game.actors.append(a)
                game.totalItems += 1

        if playerActor is None:
            raise ValueError("map has no player start (Thing.type == 1)")

        game.player = Player(playerActor)
        game.playerWeapon = PlayerWeapon(WEAPON_TYPES["pistol"])
        game.ticCmdSource = TicCmdSource(TicCmdSource.MODE_LOCAL)
        return game

    def monsters(self):
        return [a for a in self.actors if a is not self.player.actor]

    def _ai_step(self, actor):
        if actor.target is None or actor.target.isRemoved or actor.target.health <= 0:
            look_for_players(actor, [self.player], self.map.lineDefs)
        elif check_melee_range(actor):
            melee_attack(actor, lambda rng: (rng() + 1) * 3, self.rngByte,
                         lambda t, d, i: deal_damage(self, t, d, i))
        elif check_missile_range(actor, self.rng):
            hitscan_attack(actor, lambda rng: (rng() % 3 + 1) * 5, self.rngByte,
                           lambda t, d, i: deal_damage(self, t, d, i), self.map.lineDefs)
        else:
            target = actor.target
            dx, dy = target.x - actor.x, target.y - actor.y
            dist = math.hypot(dx, dy)
            if dist > 1e-6:
                step = actor.type.speed
                move_and_collide(self, actor, dx / dist * step, dy / dist * step)
        actor.tick()

    # spp-source: examples/doom/game.md#Behavior.Feature:_틱_진행
    def tick(self, rawInput=None):
        if self.menuStack.isOpen:
            return  # 메뉴가 열려 있으면 시뮬레이션을 멈춘다.

        cmd = self.ticCmdSource.collect(self.tic, rawInput or {})
        if cmd is None:
            return  # 멀티플레이 대기 중이거나 데모 재생이 끝났다.

        actor = self.player.actor
        turn = math.radians(cmd.angleTurn)
        actor.angle += math.degrees(turn)
        self.player.viewAngle = actor.angle
        forward = math.radians(actor.angle)
        right = forward + math.pi / 2
        dx = math.cos(forward) * cmd.forwardMove * 0.01 + math.cos(right) * cmd.sideMove * 0.01
        dy = math.sin(forward) * cmd.forwardMove * 0.01 + math.sin(right) * cmd.sideMove * 0.01
        if dx != 0 or dy != 0:
            move_and_collide(self, actor, dx, dy)

        if cmd.buttons & 0x1:
            fire_weapon_input(self)
        if cmd.buttons & 0x2:
            use_key(self)

        for a in self.monsters():
            if a.isRemoved:
                continue
            self._ai_step(a)

        self.playerWeapon.tick()
        self.specials = advance_specials(self.specials)
        self.lightFlashes = advance_specials(self.lightFlashes)

        subsector = BspNode.FindSubsector(actor.x, actor.y, self.map.bspRoot)
        self.automap.revealFromSubsector(subsector)

        self.soundSystem.updateListenerPosition(self.player)
        self.tic += 1
