import os
import tempfile
import unittest
from spp_std.io_ import File, Directory, Path


class FileTest(unittest.TestCase):
    def test_write_then_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "a.txt")
            File.writeAllText(path, "hi")
            self.assertEqual(File.readAllText(path), "hi")

    def test_read_missing_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(OSError):
                File.readAllText(os.path.join(tmp, "없는파일.txt"))


class DirectoryTest(unittest.TestCase):
    def test_create_and_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out")
            Directory.create(out)
            self.assertTrue(Directory.exists(out))

    def test_list_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out")
            Directory.create(out)
            File.writeAllText(os.path.join(out, "a.txt"), "")
            self.assertIn(os.path.join(out, "a.txt"), Directory.listFiles(out))


class PathTest(unittest.TestCase):
    def test_extension(self):
        self.assertEqual(Path.extension("a/b.txt"), "txt")

    def test_file_name(self):
        self.assertEqual(Path.fileName("a/b.txt"), "b.txt")


if __name__ == "__main__":
    unittest.main()
