import unittest

from pokedex import ALL_REGIONS, REGIONS, region_options


class RegionOptionsTest(unittest.TestCase):
    def test_all_then_regions_in_order(self):
        # 이슈 #20 완료 기준: "전체" 다음에 관동 → 팔데아 순서로 10개
        self.assertEqual(
            region_options(),
            ["전체", "관동", "성도", "호연", "신오", "하나", "칼로스", "알로라", "가라르", "팔데아"],
        )

    def test_count_is_ten(self):
        self.assertEqual(len(region_options()), 10)

    def test_first_is_all(self):
        self.assertEqual(ALL_REGIONS, "전체")
        self.assertEqual(region_options()[0], ALL_REGIONS)

    def test_built_from_regions(self):
        self.assertEqual(region_options()[1:], [name for name, _, _ in REGIONS])

    def test_returns_new_list(self):
        # 돌려받은 목록을 고쳐도 다음 호출에는 영향이 없다
        region_options().append("없는지역")
        self.assertEqual(len(region_options()), 10)


if __name__ == "__main__":
    unittest.main()
