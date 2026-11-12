import unittest

from pokedex import REGIONS, UNKNOWN_COLOR, contrast_ratio, region_range, text_color, type_color


class TypeColorTest(unittest.TestCase):
    def test_chart_values(self):
        # 이슈 #8 완료 기준: 불꽃·물·풀·전기가 색상표의 값과 같다
        self.assertEqual(type_color("불꽃"), "#F35806")
        self.assertEqual(type_color("물"), "#0467C5")
        self.assertEqual(type_color("풀"), "#399806")
        self.assertEqual(type_color("전기"), "#EFA802")

    def test_english_names(self):
        self.assertEqual(type_color("fire"), type_color("불꽃"))
        self.assertEqual(type_color("Water"), type_color("물"))

    def test_unknown_is_gray(self):
        self.assertEqual(UNKNOWN_COLOR, "#888888")
        self.assertEqual(type_color("없는속성"), UNKNOWN_COLOR)
        self.assertEqual(type_color(""), UNKNOWN_COLOR)
        self.assertEqual(type_color(None), UNKNOWN_COLOR)

    def test_grass_and_poison_differ(self):
        self.assertNotEqual(type_color("풀"), type_color("독"))

    def test_text_is_readable(self):
        for name in ["노말", "불꽃", "물", "풀", "전기", "얼음", "격투", "독", "땅", "비행",
                     "에스퍼", "벌레", "바위", "고스트", "드래곤", "악", "강철", "페어리", "?"]:
            bg = type_color(name)
            with self.subTest(name=name, bg=bg):
                self.assertGreaterEqual(contrast_ratio(bg, text_color(bg)), 4.5)


class RegionRangeTest(unittest.TestCase):
    def test_kanto(self):
        self.assertEqual(region_range("관동"), (1, 151))

    def test_johto(self):
        self.assertEqual(region_range("성도"), (152, 251))

    def test_unknown_region_raises(self):
        with self.assertRaises(ValueError):
            region_range("없는지역")

    def test_regions_are_continuous(self):
        for (_, _, end), (_, start, _) in zip(REGIONS, REGIONS[1:]):
            self.assertEqual(start, end + 1)


if __name__ == "__main__":
    unittest.main()
