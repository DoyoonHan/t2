import base64
from pathlib import Path

import requests
import streamlit as st

from detail import fetch_basic, fetch_detail, radar_svg
from pokedex import text_color, type_color

LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"

GRAPHQL_URL = "https://graphql.pokeapi.co/v1beta2"
KO = 3  # PokeAPI language_id for Korean

QUERY = """
query Gen1Pokedex($lang: Int!) {
  pokemon(where: {id: {_gte: 1, _lte: 151}}, order_by: {id: asc}) {
    id
    pokemonspecy {
      pokemonspeciesnames(where: {language_id: {_eq: $lang}}) { name }
    }
    pokemontypes(order_by: {slot: asc}) {
      type {
        name
        typenames(where: {language_id: {_eq: $lang}}) { name }
      }
    }
    pokemonsprites {
      artwork: sprites(path: "other.official-artwork.front_default")
    }
  }
}
"""

@st.cache_data(show_spinner="포켓몬 데이터를 불러오는 중...")
def fetch_pokedex():
    res = requests.post(
        GRAPHQL_URL,
        json={"query": QUERY, "variables": {"lang": KO}},
        timeout=30,
    )
    res.raise_for_status()
    payload = res.json()
    if "errors" in payload:
        raise RuntimeError(payload["errors"])

    pokedex = []
    for p in payload["data"]["pokemon"]:
        types = [
            (t["type"]["name"], t["type"]["typenames"][0]["name"])
            for t in p["pokemontypes"]
        ]
        pokedex.append({
            "id": p["id"],
            "name": p["pokemonspecy"]["pokemonspeciesnames"][0]["name"],
            "types": types,
            "image": p["pokemonsprites"][0]["artwork"],
        })
    return pokedex


@st.cache_data(show_spinner="상세 정보를 불러오는 중...")
def load_detail(pokemon_id):
    # 누른 포켓몬 한 마리만 조회하고, 포켓몬별로 캐시한다.
    return fetch_detail(pokemon_id, KO)


@st.cache_data(show_spinner=False)
def load_basic(pokemon_id):
    # 진화도에서 누른 1세대 밖 포켓몬(예: 피츄)의 이름·속성·이미지만 조회한다.
    return fetch_basic(pokemon_id, KO)


CSS = """
<style>
:root {
  --base: #121212; --surface: #181818; --surface-hover: #282828; --mid: #1f1f1f;
  --text: #ffffff; --silver: #b3b3b3;
  --font: "Helvetica Neue", helvetica, arial, "Apple SD Gothic Neo", "Malgun Gothic",
          "Hiragino Sans", "Hiragino Kaku Gothic ProN", Meiryo, sans-serif;
}
html, body, [data-testid="stAppViewContainer"], .stMarkdown { font-family: var(--font); color: var(--text); }
[data-testid="stAppViewContainer"] { background: var(--base); }
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: none; padding: 48px 24px 64px; }

.head { margin-bottom: 16px; text-align: center; }
.head h1 { font: 700 24px/normal var(--font); color: var(--text); margin: 0; padding: 0; }
.head .logo { display: block; margin: 0 auto; width: 100%; max-width: 360px; height: auto; }
.head p { font: 400 14px/normal var(--font); color: var(--silver); margin: 4px 0 0; }

.dex { display: grid; grid-template-columns: repeat(8, minmax(0, 1fr)); gap: 12px; }
.card {
  display: block; color: inherit; text-decoration: none; cursor: pointer;
  background: var(--surface); border-radius: 8px; padding: 12px;
  transition: background-color .2s ease, box-shadow .2s ease;
}
.dex a.card, .dex a.card:hover, .dex a.card:visited { color: var(--text) !important; text-decoration: none !important; }
.card:hover { background: var(--surface-hover); box-shadow: rgba(0,0,0,0.3) 0px 8px 8px; }
.card .art {
  background: var(--mid); border-radius: 6px; aspect-ratio: 1; display: flex;
  box-shadow: rgba(0,0,0,0.5) 0px 8px 24px;
}
.card .art img { width: 100%; height: 100%; object-fit: contain; padding: 8px; }
.card .name {
  font: 700 16px/normal var(--font); color: var(--text); margin-top: 12px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.card .no { font: 400 14px/normal var(--font); color: var(--silver); margin-top: 4px; }
.card .types { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }
.badge {
  display: inline-flex; align-items: center; white-space: nowrap;
  font: 700 12px/1.5 var(--font); color: var(--silver);
  background: var(--mid); border-radius: 9999px; padding: 2px 10px;
}

.credit {
  font: 400 14px/normal var(--font); color: #cbcbcb; text-align: center;
  background: var(--surface); border-radius: 8px; padding: 16px; margin-top: 48px;
}
.credit a { color: var(--text); font-weight: 700; text-decoration: none; }
.credit a:hover { text-decoration: underline; }

.dt-top { display: flex; gap: 24px; align-items: center; flex-wrap: wrap; }
.dt-art { background: var(--mid); border-radius: 8px; width: 220px; max-width: 100%; aspect-ratio: 1; display: flex; }
.dt-art img { width: 100%; height: 100%; object-fit: contain; padding: 12px; }
.dt-info .no { font: 400 14px/normal var(--font); color: var(--silver); }
.dt-info .name { font: 700 28px/normal var(--font); color: var(--text); margin: 4px 0 12px; }
.dt-info .types { display: flex; gap: 6px; }
.dt-sec { font: 700 16px/normal var(--font); color: var(--text); margin: 28px 0 12px; }
.radar { width: 100%; max-width: 340px; display: block; margin: 0 auto; }
.radar .grid { fill: none; stroke: #3e3e3e; stroke-width: 1; }
.radar .value { fill: rgba(30,215,96,0.35); stroke: #1ed760; stroke-width: 2; }
.radar .label { font: 700 12px var(--font); fill: var(--silver); }
.radar .num { font: 700 13px var(--font); fill: var(--text); }
.evo { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.evo-stage { display: flex; flex-direction: column; gap: 8px; }
.evo-arrow { color: var(--silver); font-size: 20px; }
.evo-mon { background: var(--surface); border-radius: 8px; padding: 8px; width: 96px; text-align: center; }
.evo-mon img { width: 72px; height: 72px; object-fit: contain; }
.evo-mon div { font: 700 13px/normal var(--font); color: var(--text); }
.evo-mon.now { outline: 2px solid #1ed760; }
.evo a.evo-mon, .evo a.evo-mon:visited, .evo a.evo-mon:hover { display: block; color: var(--text) !important; text-decoration: none !important; cursor: pointer; }
.evo a.evo-mon { transition: background-color .2s ease; }
.evo a.evo-mon:hover { background: var(--surface-hover); }
.moves { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.move { background: var(--surface); border-radius: 8px; padding: 10px 12px; display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.move .mv { font: 700 14px/normal var(--font); color: var(--text); }
.lv { font: 400 12px/normal var(--font); color: var(--silver); }

@media (max-width: 1280px) { .dex { grid-template-columns: repeat(6, minmax(0, 1fr)); } }
@media (max-width: 896px)  { .dex { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
@media (max-width: 576px)  { .dex { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
"""


def type_badges(types):
    badges = []
    for en, ko in types:
        bg = type_color(en)
        badges.append(f'<span class="badge" style="background:{bg};color:{text_color(bg)}">{ko}</span>')
    return "".join(badges)


def card(pokemon):
    return (
        f'<a class="card" href="?no={pokemon["id"]}" target="_self">'
        f'<div class="art"><img src="{pokemon["image"]}" alt="{pokemon["name"]}" loading="lazy"></div>'
        f'<div class="name">{pokemon["name"]}</div>'
        f'<div class="no">No.{pokemon["id"]:03d}</div>'
        f'<div class="types">{type_badges(pokemon["types"])}</div>'
        f'</a>'
    )


def evolution_html(stages, current_id):
    parts = []
    for i, stage in enumerate(stages):
        if i:
            parts.append('<div class="evo-arrow">→</div>')
        mons = ""
        for s in stage:
            inner = (f'<img src="{s["image"]}" alt="{s["name"]}">' if s["image"] else "") + f'<div>{s["name"]}</div>'
            if s["id"] == current_id:
                mons += f'<div class="evo-mon now">{inner}</div>'
            else:
                # 누르면 그 포켓몬의 상세 창으로 이동
                mons += f'<a class="evo-mon" href="?no={s["id"]}" target="_self" title="{s["name"]} 상세 보기">{inner}</a>'
        parts.append(f'<div class="evo-stage">{mons}</div>')
    return f'<div class="evo">{"".join(parts)}</div>'


def moves_html(moves):
    if not moves:
        return '<p class="lv">레벨업으로 배우는 기술이 없습니다.</p>'
    return '<div class="moves">' + "".join(
        f'<div class="move"><div><div class="mv">{m["name"]}</div><div class="lv">Lv.{m["level"]}</div></div>'
        f'{type_badges([m["type"]])}</div>'
        for m in moves
    ) + "</div>"


def close_detail():
    st.query_params.pop("no", None)


def show_detail(pokemon):
    @st.dialog(f'No.{pokemon["id"]:03d} {pokemon["name"]}', width="medium", on_dismiss=close_detail)
    def dialog():
        d = load_detail(pokemon["id"])
        st.markdown(
            '<div class="dt-top">'
            f'<div class="dt-art"><img src="{pokemon["image"]}" alt="{pokemon["name"]}"></div>'
            f'<div class="dt-info"><div class="no">No.{pokemon["id"]:03d}</div>'
            f'<div class="name">{pokemon["name"]}</div>'
            f'<div class="types">{type_badges(pokemon["types"])}</div></div>'
            '</div>'
            f'<div class="dt-sec">능력치</div>{radar_svg(d["chart"])}'
            f'<div class="dt-sec">진화</div>{evolution_html(d["evolution"], pokemon["id"])}'
            f'<div class="dt-sec">기술 (레벨업으로 마지막에 배우는 4개)</div>{moves_html(d["moves"])}',
            unsafe_allow_html=True,
        )
        if st.button("닫기", width="stretch"):
            close_detail()
            st.rerun()

    dialog()


def selected_pokemon(pokedex):
    try:
        no = int(st.query_params.get("no", ""))
    except ValueError:
        return None
    found = next((p for p in pokedex if p["id"] == no), None)
    if found or no < 1:
        return found
    # 진화도에서 누른 1세대 밖 포켓몬은 그 한 마리만 조회한다.
    try:
        return load_basic(no)
    except Exception:
        return None


def title_html():
    """로고 이미지를 쓰고, 파일을 못 읽으면 원래 글자 타이틀을 쓴다."""
    try:
        data = base64.b64encode(LOGO_PATH.read_bytes()).decode()
    except OSError:
        return "<h1>포켓몬 도감</h1>"
    return f'<img class="logo" src="data:image/png;base64,{data}" alt="포켓몬 도감">'


st.set_page_config(page_title="포켓몬 도감", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

pokedex = fetch_pokedex()

st.markdown(
    f'<div class="head">{title_html()}<p>1세대 · 151마리</p></div>'
    f'<div class="dex">{"".join(card(p) for p in pokedex)}</div>'
    '<div class="credit">데이터: <a href="https://pokeapi.co/" target="_blank">PokeAPI</a></div>',
    unsafe_allow_html=True,
)

selected = selected_pokemon(pokedex)
if selected:
    show_detail(selected)
