import base64
from urllib.parse import urlencode
from pathlib import Path

import requests
import streamlit as st

from detail import fetch_basic, fetch_detail, radar_svg
from pokedex import (
    ALL_REGIONS, ALL_TYPES, REGIONS, filter_by_type, region_options, region_range,
    text_color, type_color, type_options,
)

LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"

GRAPHQL_URL = "https://graphql.pokeapi.co/v1beta2"
KO = 3  # PokeAPI language_id for Korean

QUERY = """
query RegionPokedex($lang: Int!, $start: Int!, $end: Int!) {
  pokemon(where: {id: {_gte: $start, _lte: $end}}, order_by: {id: asc}) {
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
def fetch_region(region):
    """지역 하나의 포켓몬 목록을 불러온다. 지역별로 캐시한다."""
    start, end = region_range(region)
    res = requests.post(
        GRAPHQL_URL,
        json={"query": QUERY, "variables": {"lang": KO, "start": start, "end": end}},
        timeout=30,
    )
    res.raise_for_status()
    payload = res.json()
    if "errors" in payload:
        raise RuntimeError(payload["errors"])

    pokedex = []
    for p in payload["data"]["pokemon"]:
        types = [
            (t["type"]["name"], t["type"]["typenames"][0]["name"] if t["type"]["typenames"] else t["type"]["name"])
            for t in p["pokemontypes"]
        ]
        names = p["pokemonspecy"]["pokemonspeciesnames"]
        sprites = p["pokemonsprites"]
        pokedex.append({
            "id": p["id"],
            "name": names[0]["name"] if names else str(p["id"]),
            "types": types,
            "image": sprites[0]["artwork"] if sprites else None,
        })
    return pokedex


def loaded_count():
    """지금까지 불러온 지역 수. 주소의 ?r= 값에 보관해 새로고침·상세 창 이동 후에도 유지한다."""
    try:
        n = int(st.query_params.get("r", "1"))
    except ValueError:
        n = 1
    return min(max(n, 1), len(REGIONS))


def load_next_region():
    st.query_params["r"] = str(min(loaded_count() + 1, len(REGIONS)))


def detail_href(no):
    params = {k: v for k, v in st.query_params.items() if k != "no"}
    params["r"] = str(loaded_count())
    params["no"] = str(no)
    return "?" + urlencode(params)


def selected_region():
    """주소의 ?region= 값. 없거나 모르는 지역이면 "전체"."""
    name = st.query_params.get("region", ALL_REGIONS)
    return name if name in region_options() else ALL_REGIONS


def change_region():
    """드롭다운에서 고른 지역을 주소에 남긴다. "전체"면 지우고 관동부터 다시 불러온다."""
    choice = st.session_state["region-select"]
    if choice == ALL_REGIONS:
        st.query_params.pop("region", None)
    else:
        st.query_params["region"] = choice
    st.query_params.pop("r", None)
    st.query_params.pop("no", None)


def selected_type():
    """고른 속성. 주소의 ?type= 값에 보관해 상세 창을 열고 닫거나 새로고침해도 유지한다."""
    name = st.query_params.get("type", ALL_TYPES)
    return name if name in type_options() else ALL_TYPES


def change_type():
    name = st.session_state["type-select"]
    if name == ALL_TYPES:
        st.query_params.pop("type", None)
    else:
        st.query_params["type"] = name


# 바둑판 맨 아래의 보이지 않는 표시. 화면에 들어오면(끝까지 스크롤) Python에 알린다.
SCROLL_SENTINEL = st.components.v2.component(
    "region_scroll_sentinel",
    html='<div class="load-sentinel" style="height:1px"></div>',
    js="""
export default function(component) {
  const { data, setTriggerValue, parentElement } = component;
  const el = parentElement.querySelector('.load-sentinel');
  if (!el || !data) return;
  // 붙인 직후 이미 보이는 상태라면 무시하고, 한 번 화면 밖에 있다가 다시 들어올 때만 알린다.
  let armed = false, fired = false;
  const io = new IntersectionObserver((entries) => {
    const visible = entries.some((e) => e.isIntersecting);
    if (!visible) { armed = true; return; }
    if (armed && !fired) {
      fired = true;
      setTriggerValue('reached', data.next);
    }
  }, { rootMargin: '0px 0px 400px 0px' });
  io.observe(el);
  return () => io.disconnect();
}
""",
)


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
/* 새 지역이 붙을 때 브라우저가 화면을 맨 아래에 고정하지 않도록 (연달아 불러오는 것 방지) */
[data-testid="stAppViewContainer"], [data-testid="stMain"], .main, section { overflow-anchor: none; }
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

.region {
  display: flex; align-items: center; gap: 12px; margin: 40px 0 16px;
  font: 700 20px/normal var(--font); color: var(--text);
}
.region:first-child { margin-top: 8px; }
.region::after { content: ""; flex: 1; height: 1px; background: #3e3e3e; }
.region small { font: 400 14px/normal var(--font); color: var(--silver); }
.empty { font: 400 14px/normal var(--font); color: var(--silver); text-align: center; padding: 24px 0; }
.all-loaded { font: 400 14px/normal var(--font); color: var(--silver); text-align: center; margin-top: 24px; }

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

/* 바둑판 칸 수: PC 8칸 → 패드(1024px 이하) 4칸 → 모바일(576px 이하) 2칸 */
@media (max-width: 1024px) { .dex { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
@media (max-width: 576px) {
  .dex { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
  .block-container { padding: 32px 16px 48px; }
  /* 좁은 카드에서도 이름이 말줄임(…)으로 잘리지 않고 줄바꿈되게 */
  .card { padding: 10px; }
  .card .name { white-space: normal; word-break: keep-all; overflow-wrap: anywhere; }
  /* 상세 창: 이미지·글자·기술 목록이 휴대폰 너비 안에 들어오게 */
  .dt-top { gap: 16px; }
  .dt-art { width: 100%; max-width: 220px; margin: 0 auto; }
  .dt-info .name { font-size: 24px; }
  .moves { grid-template-columns: minmax(0, 1fr); }
  .move .mv { overflow-wrap: anywhere; }
}
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
        f'<a class="card" href="{detail_href(pokemon["id"])}" target="_self">'
        f'<div class="art"><img src="{pokemon["image"] or ""}" alt="{pokemon["name"]}" loading="lazy"></div>'
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
                mons += f'<a class="evo-mon" href="{detail_href(s["id"])}" target="_self" title="{s["name"]} 상세 보기">{inner}</a>'
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

st.markdown(
    f'<div class="head">{title_html()}<p>1세대 · 151마리</p></div>',
    unsafe_allow_html=True,
)

# 바둑판 위 선택 줄: 왼쪽 칸은 지역, 오른쪽 칸은 속성 드롭다운.
# 둘 다 주소(?region=, ?type=) 값으로 맞춰 두어 새 세션(링크 이동·새로고침)에서도 유지한다.
region_col, type_col = st.columns(2)
with region_col:
    if st.session_state.get("region-select") != selected_region():
        st.session_state["region-select"] = selected_region()
    st.selectbox("지역", region_options(), key="region-select", on_change=change_region)

type_name = selected_type()
st.session_state["type-select"] = type_name
with type_col:
    st.selectbox("속성", type_options(), key="type-select", on_change=change_type)

chosen = selected_region()
loaded = loaded_count()
shown_regions = REGIONS[:loaded] if chosen == ALL_REGIONS else [r for r in REGIONS if r[0] == chosen]
pokedex = []
sections = []
for region, start, end in shown_regions:
    mons = fetch_region(region)
    pokedex += mons
    shown = filter_by_type(mons, type_name)
    grid = (f'<div class="dex">{"".join(card(p) for p in shown)}</div>' if shown
            else '<div class="empty">해당 속성의 포켓몬이 없습니다.</div>')
    sections.append(f'<div class="region">{region} <small>No.{start:03d} – {end:03d}</small></div>' + grid)

st.markdown("".join(sections), unsafe_allow_html=True)

if chosen != ALL_REGIONS:
    pass  # 지역 하나만 볼 때는 다음 지역을 이어서 불러오지 않는다.
elif loaded < len(REGIONS):
    next_region = REGIONS[loaded][0]
    # 끝까지 스크롤하면 자동으로 다음 지역을 불러오고, 자동 감지가 안 되는 환경을 위해 버튼도 둔다.
    SCROLL_SENTINEL(key="region-sentinel", data={"next": next_region, "loaded": loaded},
                    on_reached_change=load_next_region)
    st.button(f"다음 지역({next_region}) 불러오기", on_click=load_next_region, width="stretch")
else:
    st.markdown('<div class="all-loaded">모든 지역을 불러왔습니다.</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="credit">데이터: <a href="https://pokeapi.co/" target="_blank">PokeAPI</a></div>',
    unsafe_allow_html=True,
)

selected = selected_pokemon(pokedex)
if selected:
    show_detail(selected)
