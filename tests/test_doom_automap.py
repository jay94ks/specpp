import unittest

from doom_automap import AutoMap
from doom_map import LineDef, Seg, Sector, SideDef, Subsector, Vertex


def _seg_with_secret(secret):
    sector = Sector(0, 0, "F", "C", 160, 0, 0)
    side = SideDef(0, 0, "-", "-", "-", sector)
    flags = LineDef.SECRET_FLAG if secret else 0
    line = LineDef(Vertex(0, 0), Vertex(10, 0), flags=flags, special=0, tag=0, frontSide=side)
    return Seg(line.v1, line.v2, 0, line, 0, 0)


class AutoMapToggleTest(unittest.TestCase):
    def test_toggle_flips_open_state(self):
        m = AutoMap()
        self.assertFalse(m.isOpen)
        m.toggle()
        self.assertTrue(m.isOpen)
        m.toggle()
        self.assertFalse(m.isOpen)


class RevealLinesTest(unittest.TestCase):
    """automap.md의 '## Feature: 지도에 선 드러내기'를 옮긴 테스트."""

    def test_reveals_lines_from_current_subsector(self):
        seg = _seg_with_secret(secret=False)
        subsector = Subsector(segs=[seg], sector=seg.lineDef.frontSide.sector)
        m = AutoMap()
        m.revealFromSubsector(subsector)
        self.assertIn(seg.lineDef, m.revealedLines)

    def test_secret_lines_are_not_revealed(self):
        seg = _seg_with_secret(secret=True)
        subsector = Subsector(segs=[seg], sector=seg.lineDef.frontSide.sector)
        m = AutoMap()
        m.revealFromSubsector(subsector)
        self.assertNotIn(seg.lineDef, m.revealedLines)

    def test_revealing_same_line_twice_does_not_duplicate(self):
        seg = _seg_with_secret(secret=False)
        subsector = Subsector(segs=[seg], sector=seg.lineDef.frontSide.sector)
        m = AutoMap()
        m.revealFromSubsector(subsector)
        m.revealFromSubsector(subsector)
        self.assertEqual(m.revealedLines.count(seg.lineDef), 1)


class PanZoomTest(unittest.TestCase):
    def test_zoom_is_clamped_to_min_max(self):
        m = AutoMap()
        m.pan_and_zoom(0, 0, zoomDelta=-100)
        self.assertGreaterEqual(m.zoom, 0.25)
        m.pan_and_zoom(0, 0, zoomDelta=100)
        self.assertLessEqual(m.zoom, 4.0)

    def test_pan_moves_center(self):
        m = AutoMap()
        m.pan_and_zoom(10, -5, zoomDelta=0)
        self.assertEqual((m.centerX, m.centerY), (10, -5))


if __name__ == "__main__":
    unittest.main()
