import tempfile
import unittest
from pathlib import Path

from doom_wad import WadFile
from doom_map import BspNode, Map, Sector, Subsector, Vertex
from doom_test_fixtures import MAP_NAME, build_two_room_map_wad


class BspNodeUnitTest(unittest.TestCase):
    """map.md의 test_required Doom.Map.BspNode 를, 손으로 만든 트리로 직접 검증한다."""

    def setUp(self):
        self.sectorWest = Sector(0, 128, "F0", "C0", 160, 0, 0)
        self.sectorEast = Sector(0, 96, "F1", "C1", 120, 0, 0)
        self.subWest = Subsector(segs=[], sector=self.sectorWest)
        self.subEast = Subsector(segs=[], sector=self.sectorEast)
        # 분할선: x=32 에서 수직(dx=0, dy=1).
        self.root = BspNode(
            x=32, y=0, dx=0, dy=1,
            frontChild=self.subWest, backChild=self.subEast,
            frontBoundingBox=(64, 0, 0, 32), backBoundingBox=(64, 0, 32, 64),
        )

    def test_point_on_side_always_zero_or_one(self):
        for x, y in [(-100, -100), (0, 0), (32, 32), (1000, 1000)]:
            side = BspNode.PointOnSide(x, y, self.root)
            self.assertIn(side, (0, 1))

    def test_find_subsector_west_of_split(self):
        found = BspNode.FindSubsector(10, 30, self.root)
        self.assertIs(found, self.subWest)

    def test_find_subsector_east_of_split(self):
        found = BspNode.FindSubsector(50, 30, self.root)
        self.assertIs(found, self.subEast)


class MapLoadTest(unittest.TestCase):
    """wad.md/map.md의 실제 바이트 포맷으로 Doom.Map.Load가 맞게 파싱하는지 검증한다."""

    def setUp(self):
        f = tempfile.NamedTemporaryFile(suffix=".wad", delete=False)
        f.write(build_two_room_map_wad())
        f.close()
        self.wad = WadFile(f.name)
        self.map = Map.Load(self.wad, MAP_NAME)

    def test_vertices_parsed(self):
        self.assertEqual(len(self.map.vertices), 6)
        self.assertEqual((self.map.vertices[0].x, self.map.vertices[0].y), (0.0, 0.0))
        self.assertEqual((self.map.vertices[2].x, self.map.vertices[2].y), (64.0, 0.0))

    def test_sectors_parsed(self):
        self.assertEqual(len(self.map.sectors), 2)
        self.assertEqual(self.map.sectors[0].ceilingHeight, 128)
        self.assertEqual(self.map.sectors[1].ceilingHeight, 96)
        self.assertEqual(self.map.sectors[0].floorTexture, "FLOOR0")

    def test_linedefs_two_sided_middle_wall(self):
        middle = self.map.lineDefs[1]
        self.assertTrue(middle.isPassable)
        self.assertIs(middle.frontSide.sector, self.map.sectors[0])
        self.assertIs(middle.backSide.sector, self.map.sectors[1])

    def test_linedefs_single_sided_are_not_passable(self):
        wall = self.map.lineDefs[0]
        self.assertFalse(wall.isPassable)

    def test_things_parsed(self):
        self.assertEqual(len(self.map.things), 2)
        self.assertEqual(self.map.things[1].type, 3004)

    # spp-source: examples/doom/map.md#Examples.예제:_점이_속한_섹터_찾기
    def test_find_subsector_matches_expected_sector(self):
        west = BspNode.FindSubsector(16, 32, self.map.bspRoot)
        east = BspNode.FindSubsector(48, 32, self.map.bspRoot)
        self.assertIs(west.sector, self.map.sectors[0])
        self.assertIs(east.sector, self.map.sectors[1])

    def test_find_subsector_segs_reference_same_sector(self):
        # test_required: 반환된 Subsector의 segs 중 적어도 하나는 그 sector와 같다.
        found = BspNode.FindSubsector(16, 32, self.map.bspRoot)
        matching = [
            seg for seg in found.segs
            if (seg.lineDef.backSide.sector if seg.side == 1 else seg.lineDef.frontSide.sector)
            is found.sector
        ]
        self.assertTrue(matching)


if __name__ == "__main__":
    unittest.main()
