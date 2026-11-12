import unittest

from detail import evolution_stages, last_moves, radar_svg, stats_to_chart

PIKACHU_STATS = {
    "hp": 35, "attack": 55, "defense": 40,
    "special-attack": 50, "special-defense": 50, "speed": 90,
}


def move(name, level, version=27):
    return {"name": name, "level": level, "version": version, "type": ("normal", "노말")}


class StatsToChartTest(unittest.TestCase):
    def test_six_stats_in_order(self):
        self.assertEqual(stats_to_chart(PIKACHU_STATS), [
            ("HP", 35), ("공격", 55), ("방어", 40),
            ("스피드", 90), ("특수방어", 50), ("특수공격", 50),
        ])

    def test_missing_stat_is_zero(self):
        chart = stats_to_chart({"hp": 10})
        self.assertEqual(len(chart), 6)
        self.assertEqual(chart[0], ("HP", 10))
        self.assertTrue(all(v == 0 for _, v in chart[1:]))

    def test_radar_svg_has_six_labels(self):
        svg = radar_svg(stats_to_chart(PIKACHU_STATS))
        self.assertTrue(svg.startswith("<svg"))
        self.assertEqual(svg.count('class="label"'), 6)


class LastMovesTest(unittest.TestCase):
    def test_picks_last_four_by_level(self):
        moves = [move("a", 1), move("b", 9), move("c", 16), move("d", 26), move("e", 33), move("f", 43)]
        self.assertEqual([m["name"] for m in last_moves(moves)], ["c", "d", "e", "f"])

    def test_uses_only_latest_version(self):
        moves = [move("old", 99, version=20), move("a", 5), move("b", 6)]
        self.assertEqual([m["name"] for m in last_moves(moves)], ["a", "b"])

    def test_duplicate_move_counted_once(self):
        moves = [move("a", 1), move("a", 40), move("b", 10), move("c", 20), move("d", 30)]
        self.assertEqual([m["name"] for m in last_moves(moves)], ["b", "c", "d", "a"])

    def test_empty(self):
        self.assertEqual(last_moves([]), [])


class EvolutionStagesTest(unittest.TestCase):
    def test_linear_chain(self):
        species = [
            {"id": 172, "from": None, "name": "피츄"},
            {"id": 25, "from": 172, "name": "피카츄"},
            {"id": 26, "from": 25, "name": "라이츄"},
        ]
        self.assertEqual([[s["name"] for s in st] for st in evolution_stages(species)],
                         [["피츄"], ["피카츄"], ["라이츄"]])

    def test_branching_chain(self):
        species = [
            {"id": 133, "from": None, "name": "이브이"},
            {"id": 134, "from": 133, "name": "샤미드"},
            {"id": 135, "from": 133, "name": "쥬피썬더"},
        ]
        self.assertEqual([[s["name"] for s in st] for st in evolution_stages(species)],
                         [["이브이"], ["샤미드", "쥬피썬더"]])


if __name__ == "__main__":
    unittest.main()
