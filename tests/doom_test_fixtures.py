"""여러 doom_*.py 테스트가 공유하는, 손으로 만든 아주 작은 맵 WAD 조각.

실제 doom.wad 없이도 wad.md/map.md의 바이트 포맷이 맞는지, 그리고 그 위에서
BSP 순회·이동·충돌 로직이 동작하는지 검증하기 위한 최소 2개 방(섹터) 맵이다.

배치:
  서쪽 방(sector0, x: 0~32, y: 0~64) | 동쪽 방(sector1, x: 32~64, y: 0~64)
  가운데 세로선(V1-V4, x=32)이 두 방을 잇는 양면 통로다.
"""
import struct

from doom_wad import build_wad_bytes

MAP_NAME = "TESTMAP"


def _pack_vertex(x, y):
    return struct.pack("<hh", x, y)


def _pack_sector(floorH, ceilH, floorTex, ceilTex, light, special, tag):
    return struct.pack(
        "<hh8s8shhh", floorH, ceilH, floorTex.encode()[:8].ljust(8, b"\x00"),
        ceilTex.encode()[:8].ljust(8, b"\x00"), light, special, tag,
    )


def _pack_sidedef(offX, offY, top, bottom, mid, sectorIdx):
    return struct.pack(
        "<hh8s8s8sh", offX, offY, top.encode()[:8].ljust(8, b"\x00"),
        bottom.encode()[:8].ljust(8, b"\x00"), mid.encode()[:8].ljust(8, b"\x00"),
        sectorIdx,
    )


def _pack_linedef(v1, v2, flags, special, tag, sideFront, sideBack):
    return struct.pack("<HHHHHHH", v1, v2, flags, special, tag, sideFront, sideBack)


def _pack_thing(x, y, angle, type_, flags):
    return struct.pack("<hhhhh", x, y, angle, type_, flags)


def _pack_seg(v1, v2, angle, lineIdx, side, offset):
    return struct.pack("<HHhHhh", v1, v2, angle, lineIdx, side, offset)


def _pack_ssector(numsegs, firstseg):
    return struct.pack("<HH", numsegs, firstseg)


def _pack_node(x, y, dx, dy, frontBbox, backBbox, c0, c1):
    return struct.pack(
        "<hhhh" + "h" * 8 + "HH",
        x, y, dx, dy, *frontBbox, *backBbox, c0, c1,
    )


NO_SIDE = 0xFFFF
SUBSECTOR_BIT = 0x8000


def build_two_room_map_wad():
    # 정점: V0..V5.
    vertices = [(0, 0), (32, 0), (64, 0), (64, 64), (32, 64), (0, 64)]
    V0, V1, V2, V3, V4, V5 = range(6)
    vertexes_lump = b"".join(_pack_vertex(x, y) for x, y in vertices)

    sectors_lump = (
        _pack_sector(0, 128, "FLOOR0", "CEIL0", 160, 0, 0)  # sector 0: 서쪽 방.
        + _pack_sector(0, 96, "FLOOR1", "CEIL1", 120, 0, 0)  # sector 1: 동쪽 방.
    )

    sidedefs = [
        _pack_sidedef(0, 0, "-", "-", "WALL", 0),  # S0: L0 front (sector0)
        _pack_sidedef(0, 0, "-", "-", "-", 0),      # S1: L1 front (sector0, 두 방 사이 문)
        _pack_sidedef(0, 0, "-", "-", "-", 1),      # S2: L1 back  (sector1)
        _pack_sidedef(0, 0, "-", "-", "WALL", 0),  # S3: L2 front (sector0)
        _pack_sidedef(0, 0, "-", "-", "WALL", 0),  # S4: L3 front (sector0)
        _pack_sidedef(0, 0, "-", "-", "WALL", 1),  # S5: L4 front (sector1)
        _pack_sidedef(0, 0, "-", "-", "WALL", 1),  # S6: L5 front (sector1)
        _pack_sidedef(0, 0, "-", "-", "WALL", 1),  # S7: L6 front (sector1)
    ]
    sidedefs_lump = b"".join(sidedefs)

    linedefs = [
        (V0, V1, 0, 0, 0, 0, NO_SIDE),       # L0: 서쪽 방 남쪽 벽 (단면)
        (V1, V4, 0, 0, 0, 1, 2),             # L1: 두 방 사이 문 (양면)
        (V4, V5, 0, 0, 0, 3, NO_SIDE),       # L2: 서쪽 방 북쪽 벽 (단면)
        (V5, V0, 0, 0, 0, 4, NO_SIDE),       # L3: 서쪽 방 서쪽 벽 (단면)
        (V1, V2, 0, 0, 0, 5, NO_SIDE),       # L4: 동쪽 방 남쪽 벽 (단면)
        (V2, V3, 0, 0, 0, 6, NO_SIDE),       # L5: 동쪽 방 동쪽 벽 (단면)
        (V3, V4, 0, 0, 0, 7, NO_SIDE),       # L6: 동쪽 방 북쪽 벽 (단면)
    ]
    linedefs_lump = b"".join(_pack_linedef(*l) for l in linedefs)

    segs = [
        (V0, V1, 0, 0, 0, 0),  # seg0: L0 front
        (V1, V4, 0, 1, 0, 0),  # seg1: L1 front (sector0)
        (V4, V5, 0, 2, 0, 0),  # seg2: L2 front
        (V5, V0, 0, 3, 0, 0),  # seg3: L3 front
        (V1, V2, 0, 4, 0, 0),  # seg4: L4 front (sector1)
        (V2, V3, 0, 5, 0, 0),  # seg5: L5 front
        (V3, V4, 0, 6, 0, 0),  # seg6: L6 front
        (V4, V1, 0, 1, 1, 0),  # seg7: L1 back (sector1)
    ]
    segs_lump = b"".join(_pack_seg(*s) for s in segs)

    ssectors_lump = _pack_ssector(4, 0) + _pack_ssector(4, 4)

    # 분할선: x=32에서 수직(dx=0, dy=1). x<32면 앞(서쪽 방), x>32면 뒤(동쪽 방).
    node = _pack_node(
        32, 0, 0, 1,
        (64, 0, 0, 32),   # frontBoundingBox: top,bottom,left,right (서쪽 방)
        (64, 0, 32, 64),  # backBoundingBox (동쪽 방)
        0 | SUBSECTOR_BIT, 1 | SUBSECTOR_BIT,
    )
    nodes_lump = node

    things_lump = (
        _pack_thing(16, 32, 0, 1, 7)      # 플레이어 시작 (서쪽 방), doomednum 1.
        + _pack_thing(48, 32, 180, 3004, 7)  # Zombieman (동쪽 방).
    )

    # DMX 사운드 lump 하나(무기 발사음 재생 테스트용) — sound.md 포맷 그대로:
    # 포맷 3, 샘플레이트 11025, 샘플 4개.
    dspistol = struct.pack("<HHI", 3, 11025, 4) + bytes([10, 20, 30, 40])

    lumps = [
        (MAP_NAME, b""),
        ("THINGS", things_lump),
        ("LINEDEFS", linedefs_lump),
        ("SIDEDEFS", sidedefs_lump),
        ("VERTEXES", vertexes_lump),
        ("SEGS", segs_lump),
        ("SSECTORS", ssectors_lump),
        ("NODES", nodes_lump),
        ("SECTORS", sectors_lump),
        ("DSPISTOL", dspistol),
    ]
    return build_wad_bytes(lumps)
