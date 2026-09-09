import os
import posixpath
import tempfile
import unittest
from unittest import mock

from spp_std.appdirs_ import LinuxAppDirectories, MacAppDirectories


class LinuxAppDirectoriesTest(unittest.TestCase):
    def test_default_config_home_under_dot_config(self):
        with tempfile.TemporaryDirectory() as home:
            with mock.patch.dict(os.environ, {"HOME": home}, clear=False):
                os.environ.pop("XDG_CONFIG_HOME", None)
                path = LinuxAppDirectories().configHome("todo-cli")
                self.assertTrue(path.endswith(".config/todo-cli"))
                self.assertTrue(os.path.isdir(path))

    def test_xdg_env_var_overrides_default(self):
        with tempfile.TemporaryDirectory() as xdg_home:
            with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": xdg_home}, clear=False):
                path = LinuxAppDirectories().configHome("todo-cli")
                self.assertEqual(path, posixpath.join(xdg_home, "todo-cli"))


class MacAppDirectoriesTest(unittest.TestCase):
    def test_config_and_data_home_are_the_same(self):
        with tempfile.TemporaryDirectory() as home:
            with mock.patch.dict(os.environ, {"HOME": home}, clear=False):
                dirs = MacAppDirectories()
                self.assertEqual(dirs.configHome("todo-cli"), dirs.dataHome("todo-cli"))

    def test_cache_home_under_library_caches(self):
        with tempfile.TemporaryDirectory() as home:
            with mock.patch.dict(os.environ, {"HOME": home}, clear=False):
                path = MacAppDirectories().cacheHome("todo-cli")
                self.assertTrue(path.replace("\\", "/").endswith("Library/Caches/todo-cli"))


if __name__ == "__main__":
    unittest.main()
