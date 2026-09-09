"""examples/doom/render.md 의 Doom.Renderer 알고리즘(원근에 맞는 벽 높이 계산,
BSP/가시성 판정)을 근사하는 아주 단순한 레이캐스팅 구현.

원본/render.md는 화면 열마다 "이 텍스처의 이 부분을 그려라"는 명령을 만들어
Doom.Renderer.Backend에 넘기는 구조다 — 이 파일은 그 화면 열 계산 부분만
순수 Python으로 구현한다(실제 텍스처 대신 섹터/텍스처 이름 기반 색으로
근사한다는 점만 render.md의 Constraints/Open Points에 적는 단순화다).
"""
import math


def build_wall_segments(map_data):
    """맵의 각 LineDef를 레이캐스팅용 세그먼트로 미리 변환한다.

    양면(두 섹터를 잇는) linedef 중 문/단차 없이 완전히 열려 있는 통로는
    레이를 막지 않는다(그래야 열린 문 너머가 보인다) — 매 프레임 문이
    움직이며 열림 상태가 바뀌므로 이 목록은 프레임마다 다시 만든다.
    """
    segments = []
    for line in map_data.lineDefs:
        x1, y1 = line.v1.x, line.v1.y
        x2, y2 = line.v2.x, line.v2.y
        if not line.isPassable:
            blocks = True
            colorSeed = hash(line.frontSide.middleTexture) if line.frontSide else 0
            baseSector = line.frontSide.sector if line.frontSide else None
        else:
            front, back = line.frontSide.sector, line.backSide.sector
            openBottom = max(front.floorHeight, back.floorHeight)
            openTop = min(front.ceilingHeight, back.ceilingHeight)
            opening = openTop - openBottom
            blocks = opening < 56.0  # 완전히 열리지 않은 통로(닫힌/여닫는 중인 문 등)만 막는다.
            colorSeed = hash((line.frontSide.topTexture, line.frontSide.bottomTexture))
            baseSector = front if front.ceilingHeight < back.ceilingHeight else back
        if blocks:
            segments.append((x1, y1, x2 - x1, y2 - y1, colorSeed, baseSector))
    return segments


def cast_ray(segments, ox, oy, angleRad, maxRange=4000.0):
    """레이 하나를 쏴서 가장 가까운 벽까지의 거리와 색 시드를 구한다."""
    dx, dy = math.cos(angleRad), math.sin(angleRad)
    bestT = None
    bestColorSeed = 0
    bestSector = None
    for x1, y1, ex, ey, colorSeed, sector in segments:
        denom = dx * ey - dy * ex
        if -1e-9 < denom < 1e-9:
            continue
        t = ((x1 - ox) * ey - (y1 - oy) * ex) / denom
        if t <= 1.0 or t > maxRange:
            continue
        u = ((x1 - ox) * dy - (y1 - oy) * dx) / denom
        if u < 0.0 or u > 1.0:
            continue
        if bestT is None or t < bestT:
            bestT = t
            bestColorSeed = colorSeed
            bestSector = sector
    return bestT, bestColorSeed, bestSector


def render_columns(segments, ox, oy, viewAngleDeg, fovDeg, numColumns):
    """화면 왼쪽부터 오른쪽까지 각 열의 (보정된 거리, colorSeed, sector)를 반환한다.

    피쉬아이 보정: 실제 거리 대신 시야 중심선에 대한 수직 거리(perp distance =
    distance * cos(offset))를 써야 벽이 화면 가장자리에서 휘어 보이지 않는다.
    """
    results = []
    halfFov = fovDeg / 2.0
    viewRad = math.radians(viewAngleDeg)
    for i in range(numColumns):
        offsetDeg = -halfFov + (fovDeg * i) / max(numColumns - 1, 1)
        rayAngle = viewRad + math.radians(offsetDeg)
        dist, colorSeed, sector = cast_ray(segments, ox, oy, rayAngle)
        if dist is not None:
            dist *= math.cos(math.radians(offsetDeg))  # 피쉬아이 보정.
        results.append((dist, colorSeed, sector))
    return results
