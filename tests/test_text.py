import unittest
from spp_std.text_ import String, Json, Regex


class StringTest(unittest.TestCase):
    def test_split_join_roundtrip(self):
        self.assertEqual(String.join(String.split("a,b,c", ","), "-"), "a-b-c")

    def test_index_of_missing_part(self):
        self.assertEqual(String.indexOf("hello", "z"), -1)

    def test_trim(self):
        self.assertEqual(String.trim("  hi  "), "hi")


class JsonTest(unittest.TestCase):
    def test_roundtrip(self):
        self.assertEqual(Json.parse(Json.stringify(42)), 42)

    def test_parse_object(self):
        self.assertEqual(Json.parse('{"a": 1}').get("a"), 1)


class RegexTest(unittest.TestCase):
    def test_existence_check(self):
        self.assertTrue(Regex("[0-9]+").test("room 42"))

    def test_replace_all(self):
        self.assertEqual(Regex("[0-9]+").replaceAll("a1b22c333", "#"), "a#b#c#")


if __name__ == "__main__":
    unittest.main()
