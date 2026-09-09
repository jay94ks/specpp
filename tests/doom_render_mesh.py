"""examples/doom/render.md 의 'Feature: 레벨 지오메트리 만들기' 참조 구현.

GPU에 올릴 정점·인덱스 데이터를 순수 파이썬으로 만든다 — OpenGL 자체에는
의존하지 않는다(업로드는 app_doom_gl.py가 doom_render_gl_backend.py를 통해
한다). 그래서 실제 GPU/창 없이도 이 모듈만으로 지오메트리가 정확한지
헤드리스로 검증할 수 있다.

좌표계: DOOM의 (x, y, height)를 OpenGL의 y-up 좌표계로 옮길 때
(glX, glY, glZ) = (doomX, height, doomY)로 대응시킨다 — 높이가 y축이 된다.
"""
import colorsys

FLOATS_PER_VERTEX = 7  # x, y, z, r, g, b, light


def _texture_color(name, lightLevel):
    hue = (abs(hash(name)) % 360) / 360.0
    brightness = max(0.15, min(1.0, lightLevel / 255.0))
    r, g, b = colorsys.hsv_to_rgb(hue, 0.5, brightness)
    return (r, g, b)


class MeshData:
    """정적 지오메트리 하나(레벨 전체)를 담는 정점/인덱스 버퍼(업로드 전, CPU 쪽)."""

    def __init__(self):
        self.vertices = []  # FLOATS_PER_VERTEX개씩: x,y,z,r,g,b,light
        self.indices = []

    @property
    def vertexCount(self):
        return len(self.vertices) // FLOATS_PER_VERTEX

    @property
    def triangleCount(self):
        return len(self.indices) // 3

    def _add_vertex(self, x, y, z, color, light):
        self.vertices.extend([x, y, z, color[0], color[1], color[2], light])

    # spp-source: examples/doom/render.md#Feature:_레벨_지오메트리_만들기 (벽 사각형)
    def add_quad(self, p1, p2, p3, p4, color, light):
        base = self.vertexCount
        for p in (p1, p2, p3, p4):
            self._add_vertex(p[0], p[1], p[2], color, light)
        self.indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])

    # spp-source: examples/doom/render.md#Feature:_레벨_지오메트리_만들기 (바닥/천장 부채꼴)
    def add_fan(self, points, color, light):
        if len(points) < 3:
            return 0
        base = self.vertexCount
        for p in points:
            self._add_vertex(p[0], p[1], p[2], color, light)
        triangles = 0
        for i in range(1, len(points) - 1):
            self.indices.extend([base, base + i, base + i + 1])
            triangles += 1
        return triangles


def _wall_quads_for_linedef(line, mesh):
    x1, y1 = line.v1.x, line.v1.y
    x2, y2 = line.v2.x, line.v2.y

    if not line.isPassable:
        front = line.frontSide.sector
        color = _texture_color(line.frontSide.middleTexture, front.lightLevel)
        mesh.add_quad(
            (x1, front.floorHeight, y1), (x2, front.floorHeight, y2),
            (x2, front.ceilingHeight, y2), (x1, front.ceilingHeight, y1),
            color, front.lightLevel,
        )
        return

    front, back = line.frontSide.sector, line.backSide.sector
    # 위쪽 계단(천장 차이 — upper texture).
    if front.ceilingHeight > back.ceilingHeight:
        color = _texture_color(line.frontSide.topTexture, front.lightLevel)
        mesh.add_quad(
            (x1, back.ceilingHeight, y1), (x2, back.ceilingHeight, y2),
            (x2, front.ceilingHeight, y2), (x1, front.ceilingHeight, y1),
            color, front.lightLevel,
        )
    # 아래쪽 계단(바닥 차이 — lower texture).
    if back.floorHeight > front.floorHeight:
        color = _texture_color(line.frontSide.bottomTexture, front.lightLevel)
        mesh.add_quad(
            (x1, front.floorHeight, y1), (x2, front.floorHeight, y2),
            (x2, back.floorHeight, y2), (x1, back.floorHeight, y1),
            color, front.lightLevel,
        )


def _floor_ceiling_fans_for_subsector(subsector, mesh):
    if not subsector.segs:
        return 0
    boundary = [(seg.v1.x, seg.v1.y) for seg in subsector.segs]
    sector = subsector.sector
    floorColor = _texture_color(sector.floorTexture, sector.lightLevel)
    ceilColor = _texture_color(sector.ceilingTexture, sector.lightLevel)

    floorPoints = [(x, sector.floorHeight, y) for x, y in boundary]
    ceilPoints = [(x, sector.ceilingHeight, y) for x, y in reversed(boundary)]

    triangles = mesh.add_fan(floorPoints, floorColor, sector.lightLevel)
    triangles += mesh.add_fan(ceilPoints, ceilColor, sector.lightLevel)
    return triangles


# spp-source: examples/doom/render.md#Feature:_레벨_지오메트리_만들기
def build_level_mesh(map_data):
    """맵을 불러올 때 한 번 호출한다. 매 프레임 다시 만들지 않는다."""
    mesh = MeshData()
    for line in map_data.lineDefs:
        _wall_quads_for_linedef(line, mesh)
    for subsector in map_data.subsectors:
        _floor_ceiling_fans_for_subsector(subsector, mesh)
    return mesh
