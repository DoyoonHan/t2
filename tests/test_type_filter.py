import unittest

from pokedex import ALL_TYPES, filter_by_type, type_options

# fetch_region()이 돌려주는 모양과 같은 작은 목록
PIKACHU = {"id": 25, "name": "피카츄", "types": [("electric", "전기")], "image": None}
CHARMANDER = {"id": 4, "name": "파이리", "types": [("fire", "불꽃")], "image": None}
CHARMELEON = {"id": 5, "name": "리자드", "types": [("fire", "불꽃")], "image": None}
CHARIZARD = {"id": 6, "name": "리자몽", "types": [("fire", "불꽃"), ("flying", "비행")], "image": None}
PIDGEY = {"id": 16, "name": "구구", "types": [("normal", "노말"), ("flying", "비행")], "image": None}
SQUIRTLE = {"id": 7, "name": "꼬부기", "types": [("water", "물")], "image": None}
POKEDEX = [CHARMANDER, CHARMELEON, CHARIZARD, SQUIRTLE, PIDGEY, PIKACHU]


class FilterByTypeTest(unittest.TestCase):
    def test_fire_keeps_only_fire(self):
        # 완료 기준: "불꽃"으로 거르면 불꽃 속성 포켓몬만 남는다
        result = filter_by_type(POKEDEX, "불꽃")
        self.assertEqual(result, [CHARMANDER, CHARMELEON, CHARIZARD])
        for p in result:
            self.assertIn("fire", [en for en, _ in p["types"]])

    def test_dual_type_matches_either(self):
        # 완료 기준: 리자몽(불꽃·비행)은 "불꽃"과 "비행" 어느 쪽으로 걸러도 남는다
        self.assertIn(CHARIZARD, filter_by_type(POKEDEX, "불꽃"))
        self.assertIn(CHARIZARD, filter_by_type(POKEDEX, "비행"))
        self.assertEqual(filter_by_type(POKEDEX, "비행"), [CHARIZARD, PIDGEY])

    def test_all_returns_list_unchanged(self):
        # 완료 기준: "전체"면 목록이 그대로다
        self.assertEqual(filter_by_type(POKEDEX, ALL_TYPES), POKEDEX)
        self.assertEqual(filter_by_type(POKEDEX, "전체"), POKEDEX)

    def test_unknown_type_raises(self):
        # 완료 기준: 모르는 속성 이름이면 오류
        with self.assertRaises(ValueError):
            filter_by_type(POKEDEX, "없는속성")
        with self.assertRaises(ValueError):
            filter_by_type(POKEDEX, "")

    def test_no_match_is_empty(self):
        self.assertEqual(filter_by_type(POKEDEX, "드래곤"), [])

    def test_does_not_modify_input(self):
        before = list(POKEDEX)
        filter_by_type(POKEDEX, "물")
        self.assertEqual(POKEDEX, before)


class TypeOptionsTest(unittest.TestCase):
    def test_options_order(self):
        # 이슈 #21: 전체 + 18개 속성, 이슈에 적힌 순서
        self.assertEqual(type_options(), [
            "전체", "노말", "불꽃", "물", "풀", "전기", "얼음", "격투", "독", "땅", "비행",
            "에스퍼", "벌레", "바위", "고스트", "드래곤", "악", "강철", "페어리",
        ])

    def test_every_option_filters(self):
        for name in type_options():
            filter_by_type(POKEDEX, name)  # 오류가 나지 않아야 한다


if __name__ == "__main__":
    unittest.main()
