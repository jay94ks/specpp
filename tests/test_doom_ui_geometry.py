import unittest

from doom_ui_geometry import (
    circle_fan, face_triangles, health_bar_color, hud_bar_geometry, key_icon_geometry, rect, thick_line,
)


class RectTest(unittest.TestCase):
    def test_rect_produces_two_triangles_six_vertices(self):
        verts = rect(0, 0, 10, 10, (1, 0, 0))
        self.assertEqual(len(verts), 6 * 5)  # 6 vertices * (x,y,r,g,b)


class CircleFanTest(unittest.TestCase):
    def test_segment_count_controls_triangle_count(self):
        verts = circle_fan(0, 0, 5, (1, 1, 1), segments=16)
        self.assertEqual(len(verts), 16 * 3 * 5)  # segments개 삼각형 * 3정점 * 5float

    def test_points_lie_on_circle(self):
        import math
        verts = circle_fan(10, 20, 5, (1, 1, 1), segments=8)
        # 두 번째 정점(각 삼각형의 첫 번째 테두리 점)이 반지름 5 위에 있는지 확인.
        x, y = verts[5], verts[6]
        dist = math.hypot(x - 10, y - 20)
        self.assertAlmostEqual(dist, 5.0, places=4)


class ThickLineTest(unittest.TestCase):
    def test_zero_length_line_is_empty(self):
        self.assertEqual(thick_line(1, 1, 1, 1, 2, (1, 0, 0)), [])

    def test_produces_two_triangles(self):
        verts = thick_line(0, 0, 10, 0, 2, (1, 0, 0))
        self.assertEqual(len(verts), 6 * 5)


class FaceTrianglesTest(unittest.TestCase):
    def test_all_known_categories_produce_geometry(self):
        for category in ["STFST", "STFKILL", "STFOUCH", "STFEVL", "STFDEAD0",
                          "STFST_GRIN", "STFKILL_HIT_front", "STFEVL_HIT_front"]:
            verts = face_triangles(50, 50, 24, category)
            self.assertGreater(len(verts), 0)
            self.assertEqual(len(verts) % 5, 0)  # 항상 (x,y,r,g,b) 묶음이어야 한다.

    def test_dead_face_uses_gray_skin(self):
        verts = face_triangles(0, 0, 24, "STFDEAD0")
        # circle_fan의 첫 삼각형 첫 정점 색이 곧 피부색이다.
        r, g, b = verts[2], verts[3], verts[4]
        self.assertAlmostEqual(r, 0.48, places=2)
        self.assertAlmostEqual(g, 0.48, places=2)

    def test_calm_face_uses_warm_skin_tone(self):
        verts = face_triangles(0, 0, 24, "STFST")
        r, g, b = verts[2], verts[3], verts[4]
        self.assertGreater(r, g)  # 살구색 계열은 빨강이 초록보다 크다.


class HudBarGeometryTest(unittest.TestCase):
    def test_health_bar_color_thresholds(self):
        self.assertEqual(health_bar_color(1.0), health_bar_color(0.7))
        self.assertNotEqual(health_bar_color(0.9), health_bar_color(0.1))

    def test_full_bar_fill_matches_width(self):
        verts = hud_bar_geometry(0, 0, 100, 10, 1.0, (0, 1, 0))
        # 두 번째 사각형(채움)의 오른쪽 x좌표들을 확인 — 6정점 * 5float 뒤부터가 채움.
        fillXs = [verts[i] for i in range(30, 60, 5)]
        self.assertAlmostEqual(max(fillXs), 98.0)  # x+2 ~ x+2+(w-4)*1.0 = 98.

    def test_half_bar_fill_is_half_width(self):
        verts = hud_bar_geometry(0, 0, 100, 10, 0.5, (0, 1, 0))
        fillXs = [verts[i] for i in range(30, 60, 5)]
        self.assertAlmostEqual(max(fillXs), 2 + 96 * 0.5)


class KeyIconTest(unittest.TestCase):
    def test_owned_key_uses_its_color(self):
        verts = key_icon_geometry(0, 0, 10, "blue", owned=True)
        r, g, b = verts[2], verts[3], verts[4]
        self.assertAlmostEqual(b, 0.82, places=2)

    def test_unowned_key_is_gray(self):
        verts = key_icon_geometry(0, 0, 10, "blue", owned=False)
        r, g, b = verts[2], verts[3], verts[4]
        self.assertAlmostEqual(r, g)
        self.assertAlmostEqual(g, b)


if __name__ == "__main__":
    unittest.main()
