"""examples/doom/specials.md 의 # Domain/# Behavior 참조 구현."""


class SectorMover:
    """Doom.SectorMover 인터페이스. tick() -> bool(계속 진행 중이면 True)."""

    def tick(self):
        raise NotImplementedError


class Door(SectorMover):
    def __init__(self, sector, kind, targetCeilingHeight, speed=4.0, requiredKey=None):
        self.sector = sector
        self.kind = kind
        self.targetCeilingHeight = targetCeilingHeight
        self.speed = speed
        self.waitTicsRemaining = 0
        self.requiredKey = requiredKey
        self._closing = kind in ("Close", "CloseThenOpen")
        self._openHeight = targetCeilingHeight
        self._closeHeight = sector.floorHeight

    def tick(self):
        if self._closing:
            self.sector.ceilingHeight = max(self._closeHeight,
                                             self.sector.ceilingHeight - self.speed)
            if self.sector.ceilingHeight <= self._closeHeight:
                if self.kind == "CloseThenOpen":
                    self._closing = False
                    return True
                return False
            return True
        else:
            self.sector.ceilingHeight = min(self._openHeight,
                                             self.sector.ceilingHeight + self.speed)
            if self.sector.ceilingHeight >= self._openHeight:
                if self.kind == "OpenThenClose":
                    if self.waitTicsRemaining > 0:
                        self.waitTicsRemaining -= 1
                        return True
                    self._closing = True
                    return True
                return False
            return True


class FloorMover(SectorMover):
    def __init__(self, sector, targetFloorHeight, speed=1.0, crush=False):
        self.sector = sector
        self.targetFloorHeight = targetFloorHeight
        self.speed = speed
        self.crush = crush

    def tick(self):
        if self.sector.floorHeight < self.targetFloorHeight:
            self.sector.floorHeight = min(self.targetFloorHeight,
                                           self.sector.floorHeight + self.speed)
        else:
            self.sector.floorHeight = max(self.targetFloorHeight,
                                           self.sector.floorHeight - self.speed)
        return self.sector.floorHeight != self.targetFloorHeight


class Ceiling(SectorMover):
    def __init__(self, sector, topHeight, bottomHeight, speed=1.0,
                 direction="Down", repeats=False, crush=False):
        self.sector = sector
        self.topHeight = topHeight
        self.bottomHeight = bottomHeight
        self.speed = speed
        self.direction = direction
        self.repeats = repeats
        self.crush = crush

    def tick(self):
        if self.direction == "Down":
            self.sector.ceilingHeight = max(self.bottomHeight,
                                             self.sector.ceilingHeight - self.speed)
            if self.sector.ceilingHeight <= self.bottomHeight:
                if self.repeats:
                    self.direction = "Up"
                    return True
                return False
        else:
            self.sector.ceilingHeight = min(self.topHeight,
                                             self.sector.ceilingHeight + self.speed)
            if self.sector.ceilingHeight >= self.topHeight:
                if self.repeats:
                    self.direction = "Down"
                    return True
                return False
        return True


class Platform(SectorMover):
    def __init__(self, sector, lowHeight, highHeight, speed=1.0,
                 direction="Down", repeatsForever=False):
        self.sector = sector
        self.lowHeight = lowHeight
        self.highHeight = highHeight
        self.speed = speed
        self.direction = direction
        self.waitTicsRemaining = 0
        self.repeatsForever = repeatsForever

    def tick(self):
        target = self.lowHeight if self.direction == "Down" else self.highHeight
        if self.sector.floorHeight != target:
            step = -self.speed if self.direction == "Down" else self.speed
            self.sector.floorHeight += step
            if (step < 0 and self.sector.floorHeight <= target) or \
               (step > 0 and self.sector.floorHeight >= target):
                self.sector.floorHeight = target
            return True
        if self.repeatsForever:
            self.direction = "Up" if self.direction == "Down" else "Down"
            return True
        return False


class LightFlash:
    def __init__(self, sector, maxLight, minLight, rng, ticsUntilNextChange=4):
        self.sector = sector
        self.maxLight = maxLight
        self.minLight = minLight
        self._rng = rng
        self.ticsUntilNextChange = ticsUntilNextChange

    def tick(self):
        self.ticsUntilNextChange -= 1
        if self.ticsUntilNextChange <= 0:
            self.sector.lightLevel = self.maxLight if self._rng() < 0.5 else self.minLight
            self.ticsUntilNextChange = 1 + int(self._rng() * 8)


# spp-source: examples/doom/specials.md#Behavior.Feature:_선을_밟아_특수_효과_발동
def trigger_line_special(lineDef, trigger, activator, active_movers, make_mover,
                          is_locked_check=None):
    """lineDef.special/trigger가 일치하면 make_mover(lineDef)로 만든 SectorMover를
    active_movers에 추가한다. make_mover가 Door이고 requiredKey가 있으면
    활성화한 Actor(플레이어)가 그 색 키를 갖고 있어야 한다."""
    if lineDef.special == 0:
        return None

    door_preview = None
    if is_locked_check is not None:
        door_preview = is_locked_check(lineDef)

    if door_preview is not None and door_preview.requiredKey is not None:
        if activator is None or door_preview.requiredKey not in getattr(activator, "keys", []):
            return None  # 잠긴 문: 필요한 키가 없으면 열지 않는다.

    mover = make_mover(lineDef)
    active_movers.append(mover)
    if trigger != "Walkover" or getattr(lineDef, "repeatable", False) is False:
        lineDef.special = 0
    return mover


# spp-source: examples/doom/specials.md#Behavior.Feature:_특수_효과_진행
def advance_specials(active_movers):
    still_active = []
    for mover in active_movers:
        if mover.tick():
            still_active.append(mover)
    return still_active
