import unittest

from doom_intermission import make_intermission


class StageClearTransitionTest(unittest.TestCase):
    """intermission.md의 '## Feature: 스테이지 클리어 전환' (퍼센트 계산) 검증."""

    def test_percentages_computed_from_counts(self):
        im = make_intermission(
            finishedMapName="E1M1", nextMapName="E1M2",
            killCount=5, totalKills=10,
            itemCount=3, totalItems=4,
            secretCount=1, totalSecrets=2,
            parTimeTics=1050, playerTimeTics=900,
        )
        self.assertEqual(im.killPercent, 50)
        self.assertEqual(im.itemPercent, 75)
        self.assertEqual(im.secretPercent, 50)
        self.assertEqual(im.nextMapName, "E1M2")

    def test_full_clear_is_100_percent(self):
        im = make_intermission("E1M1", "E1M2", 10, 10, 4, 4, 2, 2, 1050, 900)
        self.assertEqual((im.killPercent, im.itemPercent, im.secretPercent), (100, 100, 100))

    def test_zero_total_defaults_to_100_percent(self):
        # 원본 규칙: 그 종류가 애초에 맵에 없으면(총량 0) 100%로 친다.
        im = make_intermission("E1M1", None, 0, 0, 0, 0, 0, 0, 1050, 900)
        self.assertEqual((im.killPercent, im.itemPercent, im.secretPercent), (100, 100, 100))

    def test_last_map_has_no_next_map(self):
        im = make_intermission("E1M8", None, 8, 8, 4, 4, 1, 1, 1050, 900)
        self.assertIsNone(im.nextMapName)


if __name__ == "__main__":
    unittest.main()
