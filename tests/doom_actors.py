"""examples/doom/actors.md 의 # Domain 참조 구현: State/MobjType/Actor/Player와
전체 몬스터·아이템·발사체 로스터."""

MF_SOLID = 1 << 0
MF_SHOOTABLE = 1 << 1
MF_NOGRAVITY = 1 << 2
MF_MISSILE = 1 << 3
MF_COUNTKILL = 1 << 4
MF_SPECIAL = 1 << 5
MF_FLOAT = 1 << 6
MF_SHADOW = 1 << 7


class State:
    def __init__(self, sprite, frame, duration, action=None, nextState=None):
        self.sprite = sprite
        self.frame = frame
        self.duration = duration
        self.action = action
        self.nextState = nextState


class MobjType:
    def __init__(self, name, spawnHealth, radius, height, speed, flags,
                 spawnState, seeState=None, painState=None, meleeState=None,
                 missileState=None, deathState=None, doomednum=None,
                 painChance=256, mass=100):
        self.name = name
        self.spawnHealth = spawnHealth
        self.radius = radius
        self.height = height
        self.speed = speed
        self.flags = flags
        self.spawnState = spawnState
        self.seeState = seeState
        self.painState = painState
        self.meleeState = meleeState
        self.missileState = missileState
        self.deathState = deathState
        self.doomednum = doomednum
        self.painChance = painChance
        self.mass = mass


class Actor:
    _nextId = 1

    # spp-source: examples/doom/actors.md#Domain.Class:Doom.Actor.Spawn
    @staticmethod
    def Spawn(type_, x, y, angle=0.0, sector=None):
        a = Actor()
        a.type = type_
        a.x = x
        a.y = y
        a.z = sector.floorHeight if sector is not None else 0.0
        a.angle = angle
        a.momX = a.momY = a.momZ = 0.0
        a.health = type_.spawnHealth
        a.flags = type_.flags
        a.target = None
        a.sector = sector
        a.state = None
        a.ticsRemaining = 0
        a.setState(type_.spawnState)
        return a

    def setState(self, newState):
        self.state = newState
        if newState is None:
            self._removed = True
            return
        self.ticsRemaining = newState.duration
        if newState.action is not None:
            newState.action(self)

    def tick(self):
        self.x += self.momX
        self.y += self.momY
        self.z += self.momZ
        if self.state is None:
            return
        if self.state.duration == -1:
            return
        self.ticsRemaining -= 1
        if self.ticsRemaining <= 0:
            self.setState(self.state.nextState)

    @property
    def isRemoved(self):
        return getattr(self, "_removed", False)

    def __deepcopy__(self, memo):
        import copy
        new = Actor.__new__(Actor)
        memo[id(self)] = new
        for k, v in self.__dict__.items():
            if k in ("type", "state"):
                new.__dict__[k] = v  # MobjType/State는 몬스터 종류의 불변 청사진이라 공유 참조로 둔다.
            else:
                new.__dict__[k] = copy.deepcopy(v, memo)
        return new


class Player:
    def __init__(self, actor):
        self.actor = actor
        self.armor = 0
        self.armorClass = 0
        self.ammo = {"bullets": 50, "shells": 0, "rockets": 0, "cells": 0}
        self.keys = []
        self.powerups = {}
        self.currentWeapon = "pistol"
        self.viewAngle = 0.0
        self.health = actor.health if actor else 100
        self.maxHealth = 100


# ---------------------------------------------------------------------------
# 전체 몬스터 로스터 (실제 mobjinfo[] 수치). 각 항목은 (spawnHealth, radius,
# height, speed, painChance, mass, attack, doomednum) 이다. 애니메이션
# 프레임/지속 tic은 actors.md의 Open Points대로 옮기지 않았으므로, 여기서는
# 대표로 하나의 spawnState만 만들어 상태 기계가 실제로 동작함을 보인다
# (Zombieman 예제와 같은 방식 — 나머지 몬스터도 같은 틀로 채우면 된다).
# ---------------------------------------------------------------------------
MONSTER_STATS = {
    "Zombieman":         dict(doomednum=3004, health=20,   radius=20,  height=56,  speed=8,  painChance=200, mass=100,  attack="missile"),
    "Shotgun Guy":       dict(doomednum=9,    health=30,   radius=20,  height=56,  speed=8,  painChance=170, mass=100,  attack="missile"),
    "Chaingunner":       dict(doomednum=65,   health=70,   radius=20,  height=56,  speed=8,  painChance=170, mass=100,  attack="missile"),
    "Wolfenstein SS":    dict(doomednum=84,   health=50,   radius=20,  height=56,  speed=8,  painChance=170, mass=100,  attack="missile"),
    "Imp":               dict(doomednum=3001, health=60,   radius=20,  height=56,  speed=8,  painChance=200, mass=100,  attack="both"),
    "Demon":             dict(doomednum=3002, health=150,  radius=30,  height=56,  speed=10, painChance=180, mass=400,  attack="melee"),
    "Spectre":           dict(doomednum=58,   health=150,  radius=30,  height=56,  speed=10, painChance=180, mass=400,  attack="melee", extraFlags=MF_SHADOW),
    "Lost Soul":         dict(doomednum=3006, health=100,  radius=16,  height=56,  speed=8,  painChance=256, mass=50,   attack="missile", extraFlags=MF_FLOAT | MF_NOGRAVITY),
    "Cacodemon":         dict(doomednum=3005, health=400,  radius=31,  height=56,  speed=8,  painChance=128, mass=400,  attack="missile", extraFlags=MF_FLOAT | MF_NOGRAVITY),
    "Hell Knight":       dict(doomednum=69,   health=500,  radius=24,  height=64,  speed=8,  painChance=50,  mass=1000, attack="both"),
    "Baron of Hell":     dict(doomednum=3003, health=1000, radius=24,  height=64,  speed=8,  painChance=50,  mass=1000, attack="both"),
    "Arachnotron":       dict(doomednum=68,   health=500,  radius=64,  height=64,  speed=12, painChance=128, mass=600,  attack="missile"),
    "Pain Elemental":    dict(doomednum=71,   health=400,  radius=31,  height=56,  speed=8,  painChance=128, mass=400,  attack="missile", extraFlags=MF_FLOAT | MF_NOGRAVITY),
    "Revenant":          dict(doomednum=66,   health=300,  radius=20,  height=56,  speed=10, painChance=100, mass=500,  attack="both"),
    "Mancubus":          dict(doomednum=67,   health=600,  radius=48,  height=64,  speed=8,  painChance=80,  mass=1000, attack="missile"),
    "Arch-vile":         dict(doomednum=64,   health=700,  radius=20,  height=56,  speed=15, painChance=10,  mass=500,  attack="missile"),
    "Spider Mastermind": dict(doomednum=7,    health=3000, radius=128, height=100, speed=12, painChance=40,  mass=1000, attack="missile"),
    "Cyberdemon":        dict(doomednum=16,   health=4000, radius=40,  height=110, speed=16, painChance=20,  mass=1000, attack="missile"),
}

MONSTER_SPRITES = {
    "Zombieman": "POSS", "Shotgun Guy": "SPOS", "Chaingunner": "CPOS",
    "Wolfenstein SS": "SSWV", "Imp": "TROO", "Demon": "SARG", "Spectre": "SARG",
    "Lost Soul": "SKUL", "Cacodemon": "HEAD", "Hell Knight": "BOS2",
    "Baron of Hell": "BOSS", "Arachnotron": "BSPI", "Pain Elemental": "PAIN",
    "Revenant": "SKEL", "Mancubus": "FATT", "Arch-vile": "VILE",
    "Spider Mastermind": "SPID", "Cyberdemon": "CYBR",
}


def _make_monster_type(name):
    s = MONSTER_STATS[name]
    sprite = MONSTER_SPRITES[name]
    spawnState = State(sprite, 0, 10, nextState=None)
    spawnState.nextState = spawnState  # 제자리 대기 애니메이션(순환).
    seeState = State(sprite, 1, 4, nextState=None)
    seeState.nextState = seeState
    painState = State(sprite, 6, 3, nextState=seeState) if s["painChance"] > 0 else None
    deathFinal = State(sprite, 9, -1, nextState=None)
    deathState = State(sprite, 8, 5, nextState=deathFinal)
    meleeState = State(sprite, 5, 8, nextState=seeState) if s["attack"] in ("melee", "both") else None
    missileState = State(sprite, 4, 10, nextState=seeState) if s["attack"] in ("missile", "both") else None

    flags = MF_SOLID | MF_SHOOTABLE | MF_COUNTKILL | s.get("extraFlags", 0)
    return MobjType(
        name=name, spawnHealth=s["health"], radius=s["radius"], height=s["height"],
        speed=s["speed"], flags=flags, spawnState=spawnState, seeState=seeState,
        painState=painState, meleeState=meleeState, missileState=missileState,
        deathState=deathState, doomednum=s["doomednum"], painChance=s["painChance"],
        mass=s["mass"],
    )


MONSTER_TYPES = {name: _make_monster_type(name) for name in MONSTER_STATS}


# ---------------------------------------------------------------------------
# 아이템 로스터 (픽업). 각 값은 (doomednum, kind, apply(player) -> None).
# ---------------------------------------------------------------------------
def _heal(amount, cap):
    def apply(player):
        player.health = min(cap, player.health + amount)
    return apply


def _armor(amount, armorClass, cap=200):
    def apply(player):
        player.armor = min(cap, player.armor + amount)
        player.armorClass = armorClass
    return apply


def _armor_bonus(amount, cap=200):
    def apply(player):
        player.armor = min(cap, player.armor + amount)
    return apply


def _ammo(kind, amount):
    def apply(player):
        player.ammo[kind] = player.ammo.get(kind, 0) + amount
    return apply


def _weapon(name):
    def apply(player):
        player.currentWeapon = name
    return apply


def _key(color):
    def apply(player):
        if color not in player.keys:
            player.keys.append(color)
    return apply


TICS_PER_SECOND = 35


def _timed_powerup(name, seconds):
    def apply(player):
        player.powerups[name] = seconds * TICS_PER_SECOND
    return apply


def _berserk(player):
    if player.health < 100:
        player.health = 100
    player.powerups["berserk"] = -1  # 타이머 없이 영구.


def _backpack(player):
    # 모든 탄약의 최대치를 2배로 늘리고(maxAmmo 딕셔너리가 있다면 갱신), 소량 채워준다.
    for kind, amount in (("bullets", 10), ("shells", 4), ("rockets", 1), ("cells", 20)):
        player.ammo[kind] = player.ammo.get(kind, 0) + amount
    player.hasBackpack = True


ITEM_PICKUPS = {
    "Stimpack":                    dict(doomednum=2011, kind="health", apply=_heal(10, 100)),
    "Medikit":                     dict(doomednum=2012, kind="health", apply=_heal(25, 100)),
    "Health Bonus":                dict(doomednum=2014, kind="health", apply=_heal(1, 200)),
    "Soulsphere":                  dict(doomednum=2013, kind="health", apply=_heal(100, 200)),
    "Green Armor":                 dict(doomednum=2018, kind="armor", apply=_armor(100, 1)),
    "Blue Armor":                  dict(doomednum=2019, kind="armor", apply=_armor(200, 2)),
    "Armor Bonus":                 dict(doomednum=2015, kind="armor", apply=_armor_bonus(1)),
    "Clip":                        dict(doomednum=2007, kind="ammo", apply=_ammo("bullets", 10)),
    "Box of Bullets":              dict(doomednum=2048, kind="ammo", apply=_ammo("bullets", 50)),
    "Shells":                      dict(doomednum=2008, kind="ammo", apply=_ammo("shells", 4)),
    "Box of Shells":                dict(doomednum=2049, kind="ammo", apply=_ammo("shells", 20)),
    "Rocket":                      dict(doomednum=2010, kind="ammo", apply=_ammo("rockets", 1)),
    "Box of Rockets":              dict(doomednum=2046, kind="ammo", apply=_ammo("rockets", 5)),
    "Cell":                        dict(doomednum=2047, kind="ammo", apply=_ammo("cells", 20)),
    "Cell Pack":                   dict(doomednum=17,   kind="ammo", apply=_ammo("cells", 100)),
    "Backpack":                    dict(doomednum=8,    kind="ammo", apply=_backpack),
    "Chainsaw":                    dict(doomednum=2005, kind="weapon", apply=_weapon("chainsaw")),
    "Shotgun":                     dict(doomednum=2001, kind="weapon", apply=_weapon("shotgun")),
    "Chaingun":                    dict(doomednum=2002, kind="weapon", apply=_weapon("chaingun")),
    "Rocket Launcher":             dict(doomednum=2003, kind="weapon", apply=_weapon("rocketLauncher")),
    "Plasma Rifle":                dict(doomednum=2004, kind="weapon", apply=_weapon("plasmaRifle")),
    "BFG9000":                     dict(doomednum=2006, kind="weapon", apply=_weapon("bfg9000")),
    "Blue Keycard":                dict(doomednum=5,    kind="key", apply=_key("blue")),
    "Yellow Keycard":              dict(doomednum=6,    kind="key", apply=_key("yellow")),
    "Red Keycard":                 dict(doomednum=13,   kind="key", apply=_key("red")),
    "Blue Skull Key":              dict(doomednum=40,   kind="key", apply=_key("blue")),
    "Yellow Skull Key":            dict(doomednum=39,   kind="key", apply=_key("yellow")),
    "Red Skull Key":               dict(doomednum=38,   kind="key", apply=_key("red")),
    "Berserk":                     dict(doomednum=2023, kind="powerup", apply=_berserk),
    "Invulnerability":             dict(doomednum=2022, kind="powerup", apply=_timed_powerup("invulnerability", 30)),
    "Partial Invisibility":        dict(doomednum=2024, kind="powerup", apply=_timed_powerup("partialInvisibility", 60)),
    "Radiation Suit":              dict(doomednum=2025, kind="powerup", apply=_timed_powerup("radiationSuit", 60)),
    "Computer Area Map":           dict(doomednum=2026, kind="powerup", apply=_timed_powerup("computerAreaMap", 0)),
    "Light Amplification Visor":   dict(doomednum=2045, kind="powerup", apply=_timed_powerup("lightAmpVisor", 120)),
}

DOOMEDNUM_TO_ITEM_NAME = {v["doomednum"]: name for name, v in ITEM_PICKUPS.items()}


def _make_item_type(name):
    info = ITEM_PICKUPS[name]
    spawnState = State("ITEM", 0, -1)
    return MobjType(
        name=name, spawnHealth=1000, radius=20, height=16, speed=0,
        flags=MF_SPECIAL, spawnState=spawnState, doomednum=info["doomednum"],
    )


# 아이템도 몬스터와 같은 MobjType/Actor 틀로 스폰한다(actors.md Constraints 참조).
ITEM_TYPES = {name: _make_item_type(name) for name in ITEM_PICKUPS}


# ---------------------------------------------------------------------------
# 몬스터 발사체 로스터. damage(rng) -> int 형태로 무작위 피해 공식을 담는다.
# rng는 0~7 사이 정수를 뽑는 콜러블(P_Random()%8에 대응)이다.
# ---------------------------------------------------------------------------
PROJECTILE_TYPES = {
    "Imp Fireball":          dict(sprite="BAL1", speed=10, radius=6, height=8, damage=lambda rng: (rng() + 1) * 3),
    "Cacodemon Fireball":    dict(sprite="BAL2", speed=10, radius=6, height=8, damage=lambda rng: (rng() + 1) * 5),
    "Baron Fireball":        dict(sprite="BAL7", speed=15, radius=6, height=8, damage=lambda rng: (rng() + 1) * 8),
    "Mancubus Fireball":     dict(sprite="MANF", speed=20, radius=6, height=8, damage=lambda rng: (rng() + 1) * 8),
    "Arachnotron Plasma":    dict(sprite="APLS", speed=25, radius=13, height=8, damage=lambda rng: 5),
}


# ---------------------------------------------------------------------------
# Feature: 되살리기 (Arch-vile 전용)
# ---------------------------------------------------------------------------
def find_resurrectable(archvile, actors, sight_range=None):
    """시야 안(단순화: 거리 기준)에서 deathState에 멈춰 있는 되살릴 수 있는 Actor를 찾는다."""
    best = None
    best_dist_sq = None
    for a in actors:
        if a is archvile or a.isRemoved:
            continue
        if a.type.deathState is None or a.state is not a.type.deathState.nextState:
            continue
        if a.health > 0:
            continue
        dx = a.x - archvile.x
        dy = a.y - archvile.y
        dist_sq = dx * dx + dy * dy
        if sight_range is not None and dist_sq > sight_range * sight_range:
            continue
        if best is None or dist_sq < best_dist_sq:
            best, best_dist_sq = a, dist_sq
    return best


# spp-source: examples/doom/actors.md#Feature:_되살리기_(Arch-vile_전용)
def resurrect(target):
    target.health = target.type.spawnHealth
    target.flags |= MF_SOLID
    target.setState(target.type.seeState or target.type.spawnState)
