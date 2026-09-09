import struct
import tempfile
import unittest
from pathlib import Path

from doom_wad import WadFile, Palette, build_wad_bytes


class WadFileExampleTest(unittest.TestCase):
    """examples/doom/wad.md 의 # Examples 를 그대로 옮긴 테스트."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tmpdir.name) / "doom1.wad"
        data = build_wad_bytes([
            ("E1M1", b"map-data-goes-here"),
            ("PLAYPAL", bytes(range(256)) * 3),
        ])
        self.path.write_bytes(data)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_find_and_read_known_lump(self):
        wad = WadFile(str(self.path))
        idx = wad.findLump("E1M1")
        data = wad.readLump(idx)
        self.assertNotEqual(idx, -1)
        self.assertEqual(len(data), wad.lumps[idx].size)
        self.assertEqual(data, b"map-data-goes-here")


class WadFileRequiredTest(unittest.TestCase):
    """wad.md의 test_required Doom.WadFile 블록을 그대로 옮긴 테스트."""

    def test_read_lump_length_matches_size(self):
        data = build_wad_bytes([("A", b"1234567"), ("B", b"xy")])
        f = tempfile.NamedTemporaryFile(suffix=".wad", delete=False)
        f.write(data)
        f.close()
        wad = WadFile(f.name)
        for i, lump in enumerate(wad.lumps):
            self.assertEqual(len(wad.readLump(i)), lump.size)

    def test_missing_name_returns_minus_one(self):
        data = build_wad_bytes([("A", b"x")])
        f = tempfile.NamedTemporaryFile(suffix=".wad", delete=False)
        f.write(data)
        f.close()
        wad = WadFile(f.name)
        self.assertEqual(wad.findLump("NOPE"), -1)

    def test_duplicate_name_returns_latest(self):
        data = build_wad_bytes([("DUP", b"old"), ("DUP", b"newer")])
        f = tempfile.NamedTemporaryFile(suffix=".wad", delete=False)
        f.write(data)
        f.close()
        wad = WadFile(f.name)
        idx = wad.findLump("DUP")
        self.assertEqual(wad.readLump(idx), b"newer")

    def test_case_insensitive_lookup(self):
        data = build_wad_bytes([("E1M1", b"x")])
        f = tempfile.NamedTemporaryFile(suffix=".wad", delete=False)
        f.write(data)
        f.close()
        wad = WadFile(f.name)
        self.assertEqual(wad.findLump("e1m1"), 0)


class WadFileMagicTest(unittest.TestCase):
    def test_rejects_non_wad_file(self):
        f = tempfile.NamedTemporaryFile(suffix=".wad", delete=False)
        f.write(b"NOTAWADFILE" + b"\x00" * 20)
        f.close()
        with self.assertRaises(ValueError):
            WadFile(f.name)


class PaletteTest(unittest.TestCase):
    def test_color_at_reads_rgb_triplet(self):
        playpal = bytes([10, 20, 30, 40, 50, 60]) + bytes(768 - 6)
        pal = Palette(playpal)
        self.assertEqual(pal.colorAt(0), (10, 20, 30))
        self.assertEqual(pal.colorAt(1), (40, 50, 60))


if __name__ == "__main__":
    unittest.main()
