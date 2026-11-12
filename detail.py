"""포켓몬 상세 정보(스탯 · 진화도 · 기술) 조회와 가공."""

import math
from html import escape

import requests

GRAPHQL_URL = "https://graphql.pokeapi.co/v1beta2"
ARTWORK = 'sprites(path: "other.official-artwork.front_default")'

DETAIL_QUERY = f"""
query PokemonDetail($id: Int!, $lang: Int!) {{
  pokemon(where: {{id: {{_eq: $id}}}}) {{
    pokemonstats {{ base_stat stat {{ name }} }}
    pokemonspecy {{
      evolutionchain {{
        pokemonspecies(order_by: {{order: asc}}) {{
          id
          evolves_from_species_id
          pokemonspeciesnames(where: {{language_id: {{_eq: $lang}}}}) {{ name }}
          pokemons(where: {{is_default: {{_eq: true}}}}) {{ pokemonsprites {{ artwork: {ARTWORK} }} }}
        }}
      }}
    }}
    pokemonmoves(where: {{movelearnmethod: {{name: {{_eq: "level-up"}}}}}}) {{
      level
      versiongroup {{ order }}
      move {{
        name
        movenames(where: {{language_id: {{_eq: $lang}}}}) {{ name }}
        type {{ name typenames(where: {{language_id: {{_eq: $lang}}}}) {{ name }} }}
      }}
    }}
  }}
}}
"""

# 그래프에 그릴 순서와 한국어 이름 (위에서 시작해 시계 방향)
STAT_ORDER = [
    ("hp", "HP"),
    ("attack", "공격"),
    ("defense", "방어"),
    ("speed", "스피드"),
    ("special-defense", "특수방어"),
    ("special-attack", "특수공격"),
]


def _first_name(names, fallback):
    return names[0]["name"] if names else fallback


def fetch_detail(pokemon_id, lang=3):
    """포켓몬 한 마리의 상세 데이터를 PokeAPI에서 받아 화면용 형태로 돌려준다."""
    res = requests.post(
        GRAPHQL_URL,
        json={"query": DETAIL_QUERY, "variables": {"id": pokemon_id, "lang": lang}},
        timeout=30,
    )
    res.raise_for_status()
    payload = res.json()
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    p = payload["data"]["pokemon"][0]

    stats = {s["stat"]["name"]: s["base_stat"] for s in p["pokemonstats"]}

    species = []
    for s in p["pokemonspecy"]["evolutionchain"]["pokemonspecies"]:
        sprites = s["pokemons"][0]["pokemonsprites"] if s["pokemons"] else []
        species.append({
            "id": s["id"],
            "from": s["evolves_from_species_id"],
            "name": _first_name(s["pokemonspeciesnames"], str(s["id"])),
            "image": sprites[0]["artwork"] if sprites else None,
        })

    moves = []
    for m in p["pokemonmoves"]:
        mv = m["move"]
        moves.append({
            "name": _first_name(mv["movenames"], mv["name"]),
            "level": m["level"],
            "version": m["versiongroup"]["order"],
            "type": (mv["type"]["name"], _first_name(mv["type"]["typenames"], mv["type"]["name"])),
        })

    return {
        "chart": stats_to_chart(stats),
        "evolution": evolution_stages(species),
        "moves": last_moves(moves),
    }


def stats_to_chart(stats):
    """{"hp": 35, ...} 형태의 스탯을 6각형 그래프용 [(이름, 값), ...] 6개로 바꾼다.

    순서는 STAT_ORDER를 따르고, 없는 스탯은 0으로 채운다.
    """
    return [(label, int(stats.get(key, 0))) for key, label in STAT_ORDER]


def last_moves(moves, count=4):
    """레벨업 기술 목록에서 가장 마지막에 배우는 기술 count개를 고른다.

    - 가장 최신 버전(version 값이 가장 큰 것)의 기술만 본다.
    - 같은 기술이 여러 번 있으면 가장 높은 레벨 하나만 센다.
    - 결과는 배우는 순서(레벨 오름차순)로 돌려준다.
    """
    if not moves:
        return []
    latest = max(m["version"] for m in moves)
    best = {}
    for m in moves:
        if m["version"] != latest:
            continue
        if m["name"] not in best or m["level"] > best[m["name"]]["level"]:
            best[m["name"]] = m
    picked = sorted(best.values(), key=lambda m: m["level"], reverse=True)[:count]
    return sorted(picked, key=lambda m: m["level"])


def evolution_stages(species):
    """진화 계통의 종 목록을 단계별 리스트로 나눈다. [[1단계...], [2단계...], ...]"""
    by_id = {s["id"]: s for s in species}

    def depth(s):
        d = 0
        while s["from"] in by_id:
            s = by_id[s["from"]]
            d += 1
        return d

    stages = {}
    for s in species:
        stages.setdefault(depth(s), []).append(s)
    return [stages[d] for d in sorted(stages)]


def radar_svg(chart, size=300, max_value=None):
    """[(이름, 값), ...]로 6각형(레이더) 그래프 SVG 문자열을 만든다."""
    n = len(chart)
    cx = cy = size / 2
    r = size / 2 - 60
    top = max_value or max(150, *(v for _, v in chart))

    def point(i, ratio):
        a = -math.pi / 2 + 2 * math.pi * i / n
        return cx + r * ratio * math.cos(a), cy + r * ratio * math.sin(a)

    def poly(ratios):
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in (point(i, t) for i, t in enumerate(ratios)))

    parts = [f'<svg class="radar" viewBox="0 0 {size} {size}" role="img" aria-label="스탯 그래프">']
    for level in (0.25, 0.5, 0.75, 1):
        parts.append(f'<polygon points="{poly([level] * n)}" class="grid"/>')
    for i in range(n):
        x, y = point(i, 1)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" class="grid"/>')
    parts.append(f'<polygon points="{poly([v / top for _, v in chart])}" class="value"/>')
    for i, (label, v) in enumerate(chart):
        x, y = point(i, 1.22)
        parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="middle">'
            f'<tspan class="label">{escape(label)}</tspan>'
            f'<tspan class="num" x="{x:.1f}" dy="15">{v}</tspan></text>'
        )
    parts.append("</svg>")
    return "".join(parts)
