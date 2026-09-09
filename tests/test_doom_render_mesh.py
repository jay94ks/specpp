import unittest

from doom_map import LineDef, Map, Sector, SideDef, Subsector, Seg, Vertex
from doom_render_mesh import MeshData, build_level_mesh
from doom_test_fixtures import MAP_NAME, build_two_room_map_wad
from doom_wad import WadFile


class MeshDataTest(unittest.TestCase):
    """render.md의 '## Class: Doom.Sprite'/버텍스 버퍼 근본 규칙 검증."""

    def test_add_quad_makes_two_triangles(self):
        mesh = MeshData()
        mesh.add_quad((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (1, 0, 0), 160)
        self.assertEqual(mesh.vertexCount, 4)
        self.assertEqual(mesh.triangleCount, 2)

    def test_add_fan_n_minus_2_triangles(self):
        # render.md test_required: N개 정점의 볼록 다각형은 N-2개의 삼각형.
        mesh = MeshData()
        pentagon = [(0, 0, 0), (1, 0, 0), (1.5, 0, 1), (0.5, 0, 2), (-0.5, 0, 1)]
        triangles = mesh.add_fan(pentagon, (0, 1, 0), 160)
        self.assertEqual(triangles, len(pentagon) - 2)
        self.assertEqual(mesh.triangleCount, len(pentagon) - 2)

    def test_multiple_adds_accumulate(self):
        mesh = MeshData()
        mesh.add_quad((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (1, 0, 0), 160)
        mesh.add_quad((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (1, 0, 0), 160)
        self.assertEqual(mesh.vertexCount, 8)
        self.assertEqual(mesh.triangleCount, 4)
        self.assertEqual(mesh.indices[6], 4)  # 두 번째 사각형은 4번 정점부터 시작한다.


class BuildLevelMeshFixtureTest(unittest.TestCase):
    """doom_test_fixtures의 손으로 만든 2방 맵으로 레벨 메시를 검증한다."""

    def setUp(self):
        import tempfile
        f = tempfile.NamedTemporaryFile(suffix=".wad", delete=False)
        f.write(build_two_room_map_wad())
        f.close()
        wad = WadFile(f.name)
        self.map = Map.Load(wad, MAP_NAME)

    def test_single_sided_wall_makes_one_quad(self):
        mesh = MeshData()
        from doom_render_mesh import _wall_quads_for_linedef
        wall = self.map.lineDefs[0]  # L0: 단면 벽.
        self.assertFalse(wall.isPassable)
        _wall_quads_for_linedef(wall, mesh)
        self.assertEqual(mesh.triangleCount, 2)  # 사각형 하나 = 삼각형 둘.

    def test_two_sided_wall_with_ceiling_step_makes_one_quad(self):
        mesh = MeshData()
        from doom_render_mesh import _wall_quads_for_linedef
        door = self.map.lineDefs[1]  # L1: 서쪽(ceil128)-동쪽(ceil96) 사이 문, floor 차이 없음.
        self.assertTrue(door.isPassable)
        _wall_quads_for_linedef(door, mesh)
        self.assertEqual(mesh.triangleCount, 2)  # 천장 차이로 인한 위쪽 계단 하나만.

    def test_full_level_mesh_has_walls_and_floors_and_ceilings(self):
        mesh = build_level_mesh(self.map)
        self.assertGreater(mesh.triangleCount, 0)
        self.assertEqual(mesh.vertexCount * 7, len(mesh.vertices))

    def test_subsector_fan_triangle_count_matches_seg_count_minus_two(self):
        # render.md test_required를 실제 서브섹터에 대해 검증한다.
        for subsector in self.map.subsectors:
            mesh = MeshData()
            from doom_render_mesh import _floor_ceiling_fans_for_subsector
            triangles = _floor_ceiling_fans_for_subsector(subsector, mesh)
            expected = 2 * (len(subsector.segs) - 2)  # 바닥 + 천장 두 부채꼴.
            self.assertEqual(triangles, expected)


class BuildLevelMeshRealE1M1Test(unittest.TestCase):
    """실제 셰어웨어 doom1.wad의 E1M1로 레벨 메시를 검증한다."""

    @classmethod
    def setUpClass(cls):
        import os
        wadPath = os.path.join(os.path.dirname(__file__), "..", "examples", "doom", "assets", "doom1.wad")
        wad = WadFile(wadPath)
        cls.map = Map.Load(wad, "E1M1")
        cls.mesh = build_level_mesh(cls.map)

    def test_mesh_is_non_trivial(self):
        self.assertGreater(self.mesh.triangleCount, 500)
        self.assertGreater(self.mesh.vertexCount, 500)

    def test_every_subsector_contributes_a_convex_fan(self):
        total_expected = 0
        for subsector in self.map.subsectors:
            if len(subsector.segs) >= 3:
                total_expected += 2 * (len(subsector.segs) - 2)

        floorCeilMesh = MeshData()
        from doom_render_mesh import _floor_ceiling_fans_for_subsector
        total_actual = 0
        for subsector in self.map.subsectors:
            total_actual += _floor_ceiling_fans_for_subsector(subsector, floorCeilMesh)
        self.assertEqual(total_actual, total_expected)

    def test_indices_stay_within_vertex_bounds(self):
        for idx in self.mesh.indices:
            self.assertGreaterEqual(idx, 0)
            self.assertLess(idx, self.mesh.vertexCount)


if __name__ == "__main__":
    unittest.main()
