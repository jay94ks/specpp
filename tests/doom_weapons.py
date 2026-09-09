"""examples/doom/weapons.md 의 # Domain(Doom.WeaponType/Doom.PlayerWeapon)과
전체 무기 로스터 참조 구현."""
from doom_actors import State


class WeaponType:
    def __init__(self, name, ammoType, ammoPerShot, upState, downState,
                 readyState, attackState, flashState=None, damage=None):
        self.name = name
        self.ammoType = ammoType
        self.ammoPerShot = ammoPerShot
        self.upState = upState
        self.downState = downState
        self.readyState = readyState
        self.attackState = attackState
        self.flashState = flashState
        self.damage = damage  # (rng) -> int, 위 전체 무기 로스터 표의 공식.


class PlayerWeapon:
    def __init__(self, type_):
        self.type = type_
        self.state = type_.readyState
        self.ticsRemaining = self.state.duration

    # spp-source: examples/doom/weapons.md#Domain.Class:Doom.PlayerWeapon.setState
    def setState(self, newState):
        self.state = newState
        self.ticsRemaining = newState.duration
        if newState.action is not None:
            newState.action(self)

    def tick(self):
        if self.state.duration == -1:
            return
        self.ticsRemaining -= 1
        if self.ticsRemaining <= 0:
            self.setState(self.state.nextState)


def _bullet_damage(rng):
    # ((P_Random()%3)+1)*5 = 5/10/15.
    return (rng() % 3 + 1) * 5


def _fist_damage(rng):
    # ((P_Random()%10)+1)*2 = 2..20.
    return (rng() % 10 + 1) * 2


def _rocket_direct_damage(rng):
    return 20 + rng() % 133  # 20..152.


def _plasma_damage(rng):
    return (5 + rng() % 8) + (5 + rng() % 8)  # 두 번 더함: 10..40 근방.


def _bfg_damage(rng):
    return 100 + rng() % 701  # 100..800.


def _make_weapon(name, ammoType, ammoPerShot, damage, meleeLike=False):
    ready = State(name.upper()[:4], 0, -1)
    ready.nextState = ready
    flash = State(name.upper()[:4], 5, 4, nextState=ready) if not meleeLike else None
    attack = State(name.upper()[:4], 1, 4, nextState=flash if flash is not None else ready)
    up = State(name.upper()[:4], 2, 6, nextState=ready)
    down = State(name.upper()[:4], 3, 6, nextState=None)
    return WeaponType(
        name=name, ammoType=ammoType, ammoPerShot=ammoPerShot,
        upState=up, downState=down, readyState=ready, attackState=attack,
        flashState=flash, damage=damage,
    )


WEAPON_TYPES = {
    "fist": _make_weapon("fist", None, 0, _fist_damage, meleeLike=True),
    "chainsaw": _make_weapon("chainsaw", None, 0, _fist_damage, meleeLike=True),
    "pistol": _make_weapon("pistol", "bullets", 1, _bullet_damage),
    "shotgun": _make_weapon("shotgun", "shells", 1, lambda rng: sum(_bullet_damage(rng) for _ in range(7))),
    "chaingun": _make_weapon("chaingun", "bullets", 1, _bullet_damage),
    "rocketLauncher": _make_weapon("rocketLauncher", "rockets", 1, _rocket_direct_damage),
    "plasmaRifle": _make_weapon("plasmaRifle", "cells", 1, _plasma_damage),
    "bfg9000": _make_weapon("bfg9000", "cells", 40, _bfg_damage),
}
