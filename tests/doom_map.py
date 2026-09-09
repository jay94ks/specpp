"""examples/doom/map.md 의 # Domain(Doom.Map 네임스페이스) 참조 구현.

원본 doomdata.h의 레코드 바이트 포맷(mapvertex_t/maplinedef_t/mapsidedef_t/
mapsector_t/mapthing_t/mapseg_t/mapsubsector_t/mapnode_t)을 그대로 따른다.
"""
import struct

SUBSECTOR_BIT = 0x8000


class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Sector:
    def __init__(self, floorHeight, ceilingHeight, floorTexture, ceilingTexture,
                 lightLevel, special, tag):
        self.floorHeight = floorHeight
        self.ceilingHeight = ceilingHeight
        self.floorTexture = floorTexture
        self.ceilingTexture = ceilingTexture
        self.lightLevel = lightLevel
        self.special = special
        self.tag = tag


class SideDef:
    def __init__(self, textureOffsetX, textureOffsetY, topTexture, bottomTexture,
                 middleTexture, sector):
        self.textureOffsetX = textureOffsetX
        self.textureOffsetY = textureOffsetY
        self.topTexture = topTexture
        self.bottomTexture = bottomTexture
        self.middleTexture = middleTexture
        self.sector = sector


class LineDef:
    SECRET_FLAG = 0x20  # 원본 ML_SECRET.

    def __init__(self, v1, v2, flags, special, tag, frontSide, backSide=None):
        self.v1 = v1
        self.v2 = v2
        self.flags = flags
        self.special = special
        self.tag = tag
        self.frontSide = frontSide
        self.backSide = backSide

    @property
    def isPassable(self):
        # 불변식: backSide가 없으면 통과할 수 없다.
        return self.backSide is not None

    @property
    def isSecret(self):
        return bool(self.flags & self.SECRET_FLAG)


class Thing:
    def __init__(self, x, y, angle, type_, flags):
        self.x = x
        self.y = y
        self.angle = angle
        self.type = type_
        self.flags = flags


class Seg:
    def __init__(self, v1, v2, angle, lineDef, side, offset):
        self.v1 = v1
        self.v2 = v2
        self.angle = angle
        self.lineDef = lineDef
        self.side = side
        self.offset = offset


class Subsector:
    def __init__(self, segs, sector):
        self.segs = segs
        self.sector = sector


class BspNode:
    def __init__(self, x, y, dx, dy, frontChild, backChild,
                 frontBoundingBox, backBoundingBox):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.frontChild = frontChild
        self.backChild = backChild
        self.frontBoundingBox = frontBoundingBox
        self.backBoundingBox = backBoundingBox

    # spp-source: examples/doom/map.md#Domain.Class:Doom.Map.BspNode.PointOnSide
    @staticmethod
    def PointOnSide(x, y, node):
        dx = x - node.x
        dy = y - node.y
        cross = node.dx * dy - node.dy * dx
        return 1 if cross <= 0 else 0

    # spp-source: examples/doom/map.md#Domain.Class:Doom.Map.BspNode.FindSubsector
    @staticmethod
    def FindSubsector(x, y, root):
        node = root
        while isinstance(node, BspNode):
            side = BspNode.PointOnSide(x, y, node)
            node = node.backChild if side == 1 else node.frontChild
        return node


def _decode_name(raw):
    return raw.split(b"\x00", 1)[0].decode("ascii", errors="replace")


class Map:
    def __init__(self, name):
        self.name = name
        self.vertices = []
        self.lineDefs = []
        self.sectors = []
        self.subsectors = []
        self.bspRoot = None
        self.things = []

    # spp-source: examples/doom/map.md#Domain.Class:Doom.Map.Load
    @staticmethod
    def Load(wad, mapName):
        m = Map(mapName)
        map_idx = wad.findLump(mapName)
        if map_idx < 0:
            raise ValueError(f"map not found: {mapName}")

        def lump_after(lump_name):
            idx = map_idx + 1
            # 맵 이름 바로 뒤 lump들은 순서가 고정되어 있다고 가정한다(원본 규칙).
            names = ["THINGS", "LINEDEFS", "SIDEDEFS", "VERTEXES", "SEGS",
                     "SSECTORS", "NODES", "SECTORS"]
            offset = names.index(lump_name)
            return wad.readLump(idx + offset)

        # VERTEXES: short x, short y (4바이트).
        vtx_data = lump_after("VERTEXES")
        for off in range(0, len(vtx_data), 4):
            x, y = struct.unpack_from("<hh", vtx_data, off)
            m.vertices.append(Vertex(float(x), float(y)))

        # SECTORS: 26바이트.
        sec_data = lump_after("SECTORS")
        for off in range(0, len(sec_data), 26):
            floorH, ceilH, floorTex, ceilTex, light, special, tag = struct.unpack_from(
                "<hh8s8shhh", sec_data, off
            )
            m.sectors.append(Sector(
                float(floorH), float(ceilH), _decode_name(floorTex),
                _decode_name(ceilTex), light, special, tag,
            ))

        # SIDEDEFS: 30바이트.
        side_data = lump_after("SIDEDEFS")
        sidedefs = []
        for off in range(0, len(side_data), 30):
            offX, offY, top, bottom, mid, secIdx = struct.unpack_from(
                "<hh8s8s8sh", side_data, off
            )
            sidedefs.append(SideDef(
                float(offX), float(offY), _decode_name(top), _decode_name(bottom),
                _decode_name(mid), m.sectors[secIdx],
            ))

        # LINEDEFS: 14바이트.
        line_data = lump_after("LINEDEFS")
        for off in range(0, len(line_data), 14):
            v1i, v2i, flags, special, tag, sideFront, sideBack = struct.unpack_from(
                "<HHHHHHH", line_data, off
            )
            front = sidedefs[sideFront] if sideFront != 0xFFFF else None
            back = sidedefs[sideBack] if sideBack != 0xFFFF else None
            m.lineDefs.append(LineDef(
                m.vertices[v1i], m.vertices[v2i], flags, special, tag, front, back,
            ))

        # THINGS: 10바이트.
        thing_data = lump_after("THINGS")
        for off in range(0, len(thing_data), 10):
            x, y, angle, type_, flags = struct.unpack_from("<hhhhh", thing_data, off)
            m.things.append(Thing(float(x), float(y), float(angle), type_, flags))

        # SEGS: 12바이트.
        seg_data = lump_after("SEGS")
        segs = []
        for off in range(0, len(seg_data), 12):
            v1i, v2i, angle, lineIdx, side, segOffset = struct.unpack_from(
                "<HHhHhh", seg_data, off
            )
            segs.append(Seg(
                m.vertices[v1i], m.vertices[v2i], float(angle),
                m.lineDefs[lineIdx], side, float(segOffset),
            ))

        # SSECTORS: 4바이트.
        ssector_data = lump_after("SSECTORS")
        for off in range(0, len(ssector_data), 4):
            numsegs, firstseg = struct.unpack_from("<HH", ssector_data, off)
            these = segs[firstseg : firstseg + numsegs]
            if these:
                first = these[0]
                side = first.lineDef.backSide if first.side == 1 else first.lineDef.frontSide
                sector = side.sector
            else:
                sector = m.sectors[0]
            m.subsectors.append(Subsector(these, sector))

        # NODES: 28바이트 (x,y,dx,dy: short*4, bbox: short*8, children: ushort*2).
        node_data = lump_after("NODES")
        raw_nodes = []
        for off in range(0, len(node_data), 28):
            x, y, dx, dy, *bbox, c0, c1 = struct.unpack_from("<hhhhhhhhhhhhHH", node_data, off)
            front_bbox = (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))
            back_bbox = (float(bbox[4]), float(bbox[5]), float(bbox[6]), float(bbox[7]))
            raw_nodes.append((float(x), float(y), float(dx), float(dy),
                               front_bbox, back_bbox, c0, c1))

        def resolve_child(child_id):
            if child_id & SUBSECTOR_BIT:
                return m.subsectors[child_id & ~SUBSECTOR_BIT]
            return build_node(child_id)

        built = {}

        def build_node(idx):
            if idx in built:
                return built[idx]
            x, y, dx, dy, fbb, bbb, c0, c1 = raw_nodes[idx]
            node = BspNode(x, y, dx, dy, None, None, fbb, bbb)
            built[idx] = node
            node.frontChild = resolve_child(c0)
            node.backChild = resolve_child(c1)
            return node

        if raw_nodes:
            m.bspRoot = build_node(len(raw_nodes) - 1)  # 원본은 마지막 노드가 루트다.

        return m
