import sys
import unittest

TEST_SUBKEY = r"Software\SppSpecTest"


@unittest.skipUnless(sys.platform == "win32", "std/windows/*.md 는 platform: windows 이므로 Windows에서만 검증한다")
class RegistryKeyTest(unittest.TestCase):
    def setUp(self):
        from spp_std.windows_ import RegistryKey
        self.RegistryKey = RegistryKey

    def tearDown(self):
        try:
            root = self.RegistryKey(self.RegistryKey.HKEY_CURRENT_USER, "Software")
            root.deleteSubKey("SppSpecTest")
            root.close()
        except OSError:
            pass

    def test_write_then_read(self):
        key = self.RegistryKey.create(self.RegistryKey.HKEY_CURRENT_USER, TEST_SUBKEY)
        key.setValue("Theme", "dark")
        self.assertEqual(key.getValue("Theme"), "dark")
        key.close()

    def test_missing_value_returns_none(self):
        key = self.RegistryKey.create(self.RegistryKey.HKEY_CURRENT_USER, TEST_SUBKEY)
        self.assertIsNone(key.getValue("존재하지않는값"))
        key.close()


if __name__ == "__main__":
    unittest.main()
