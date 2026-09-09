import math
import unittest

from doom_gl_math import identity, look_at, multiply, ortho, perspective, right_and_up_from_view, view_from_player


class IdentityAndMultiplyTest(unittest.TestCase):
    def test_identity_times_identity_is_identity(self):
        self.assertEqual(multiply(identity(), identity()), identity())

    def test_multiply_matches_translation_composition(self):
        def translation(x, y, z):
            m = identity()
            m[12], m[13], m[14] = x, y, z
            return m

        combined = multiply(translation(1, 0, 0), translation(0, 2, 0))
        # combined는 두 이동을 합친 것과 같아야 한다: (1,2,0) 만큼 이동.
        self.assertAlmostEqual(combined[12], 1.0)
        self.assertAlmostEqual(combined[13], 2.0)


class PerspectiveTest(unittest.TestCase):
    def test_center_point_maps_near_zero_ndc(self):
        proj = perspective(90.0, 1.0, 0.1, 100.0)
        # 카메라 정면(0,0,-5,1)을 투영하면 x/y는 0 근처(클립 공간)여야 한다.
        x, y, z, w = 0.0, 0.0, -5.0, 1.0
        clipX = proj[0] * x + proj[4] * y + proj[8] * z + proj[12] * w
        clipW = proj[3] * x + proj[7] * y + proj[11] * z + proj[15] * w
        self.assertAlmostEqual(clipX, 0.0)
        self.assertGreater(clipW, 0.0)


class OrthoTest(unittest.TestCase):
    def test_maps_corners_to_minus1_plus1(self):
        m = ortho(0, 640, 400, 0, -1, 1)
        # 왼쪽 위 (0,0)는 NDC (-1, 1)이어야 한다(y가 뒤집힌 화면 좌표계).
        x = m[0] * 0 + m[12]
        y = m[5] * 0 + m[13]
        self.assertAlmostEqual(x, -1.0)
        self.assertAlmostEqual(y, 1.0)


class LookAtTest(unittest.TestCase):
    def test_looking_down_positive_x_axis(self):
        view = look_at((0, 0, 0), (1, 0, 0), (0, 1, 0))
        # 카메라가 +x를 보고 있으면, 카메라 공간에서 +x 방향의 점은 -z(카메라 앞)에 있어야 한다.
        wx, wy, wz = 5.0, 0.0, 0.0
        camZ = view[2] * wx + view[6] * wy + view[10] * wz + view[14]
        self.assertLess(camZ, 0.0)


class ViewFromPlayerTest(unittest.TestCase):
    def test_right_and_up_are_orthogonal_and_unit_length(self):
        view = view_from_player(0, 41, 0, 45.0)
        right, up = right_and_up_from_view(view)

        def length(v):
            return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)

        def dot(a, b):
            return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

        self.assertAlmostEqual(length(right), 1.0, places=5)
        self.assertAlmostEqual(length(up), 1.0, places=5)
        self.assertAlmostEqual(dot(right, up), 0.0, places=5)

    def test_yaw_zero_faces_positive_x(self):
        view = view_from_player(0, 0, 0, 0.0)
        camZ = view[2] * 10 + view[14]  # 카메라 공간에서 (10,0,0)의 z.
        self.assertLess(camZ, 0.0)  # 카메라 앞쪽(-z)에 있어야 한다.


if __name__ == "__main__":
    unittest.main()
