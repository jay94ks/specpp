"""examples/doom/ai.md 의 # Behavior(A_Look/A_Chase/A_FaceTarget 등) 참조 구현."""
import math

from doom_actors import MF_SOLID


def _segments_intersect(p1, p2, p3, p4):
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    d1 = cross(p3, p4, p1)
    d2 = cross(p3, p4, p2)
    d3 = cross(p1, p2, p3)
    d4 = cross(p1, p2, p4)
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    return False


# spp-source: examples/doom/ai.md#Constraints (시야 판정)
def has_line_of_sight(x1, y1, x2, y2, lineDefs):
    for line in lineDefs:
        if line.isPassable:
            continue  # 통과 가능한(양면) 벽은 시야를 막지 않는다.
        v1 = (line.v1.x, line.v1.y)
        v2 = (line.v2.x, line.v2.y)
        if _segments_intersect((x1, y1), (x2, y2), v1, v2):
            return False
    return True


# spp-source: examples/doom/ai.md#Feature:_대기_중_플레이어_탐지_(A_Look)
def look_for_players(actor, players, lineDefs):
    for player in players:
        if player.actor.isRemoved or player.health <= 0:
            continue
        if has_line_of_sight(actor.x, actor.y, player.actor.x, player.actor.y, lineDefs):
            actor.target = player.actor
            if actor.type.seeState is not None:
                actor.setState(actor.type.seeState)
            return True
    return False


def _distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


# spp-source: examples/doom/ai.md#Feature:_목표_바라보기_(A_FaceTarget)
def face_target(actor):
    if actor.target is None:
        return
    actor.angle = math.degrees(math.atan2(actor.target.y - actor.y, actor.target.x - actor.x))


def check_melee_range(actor):
    if actor.target is None or actor.type.meleeState is None:
        return False
    return _distance(actor, actor.target) <= actor.type.radius + actor.target.type.radius + 20


def check_missile_range(actor, rng, base_chance=0.2):
    if actor.target is None or actor.type.missileState is None:
        return False
    dist = _distance(actor, actor.target)
    chance = min(0.9, base_chance + 200.0 / max(dist, 1.0) * 0.1)
    return rng() < chance


# spp-source: examples/doom/ai.md#Feature:_추격_(A_Chase)
def chase(actor, players, lineDefs, rng):
    if actor.target is None or actor.target.isRemoved or actor.target.health <= 0:
        if not look_for_players(actor, players, lineDefs):
            return "idle"
    if check_melee_range(actor):
        actor.setState(actor.type.meleeState)
        return "melee"
    if check_missile_range(actor, rng):
        actor.setState(actor.type.missileState)
        return "missile"
    return "move"


# spp-source: examples/doom/ai.md#Feature:_근접_공격_판정
def melee_attack(actor, damage_fn, rng, deal_damage):
    face_target(actor)
    if actor.target is not None and check_melee_range(actor):
        deal_damage(actor.target, damage_fn(rng), actor)


# spp-source: examples/doom/ai.md#Feature:_원거리_공격_판정 (즉발 명중형)
def hitscan_attack(actor, damage_fn, rng, deal_damage, lineDefs, spread_deg=5.0):
    face_target(actor)
    target = actor.target
    if target is None:
        return
    spread = (rng() * 2 - 1) * spread_deg
    aimed_angle = math.radians(actor.angle) + math.radians(spread)
    reach = 2000.0
    endX = actor.x + math.cos(aimed_angle) * reach
    endY = actor.y + math.sin(aimed_angle) * reach
    if abs(spread) <= 0.001 and has_line_of_sight(actor.x, actor.y, target.x, target.y, lineDefs):
        deal_damage(target, damage_fn(rng), actor)


# spp-source: examples/doom/ai.md#Feature:_고통과_죽음_(A_Pain_/_A_Fall_계열)
def pain_and_death(actor, rng, deal_damage_dummy=None):
    if actor.health > 0:
        if actor.type.painState is not None and rng() < actor.type.painChance / 256.0:
            actor.setState(actor.type.painState)
        return "pain"
    actor.setState(actor.type.deathState)
    actor.flags &= ~MF_SOLID
    return "death"
