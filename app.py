import requests
import streamlit as st

from pokedex import text_color, type_color

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

.head { margin-bottom: 16px; }
.head h1 { font: 700 24px/normal var(--font); color: var(--text); margin: 0; padding: 0; }
.head p { font: 400 14px/normal var(--font); color: var(--silver); margin: 4px 0 0; }

.dex { display: grid; grid-template-columns: repeat(8, minmax(0, 1fr)); gap: 12px; }
.card {
  background: var(--surface); border-radius: 8px; padding: 12px;
  transition: background-color .2s ease, box-shadow .2s ease;
}
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
        f'<div class="card">'
        f'<div class="art"><img src="{pokemon["image"]}" alt="{pokemon["name"]}" loading="lazy"></div>'
        f'<div class="name">{pokemon["name"]}</div>'
        f'<div class="no">No.{pokemon["id"]:03d}</div>'
        f'<div class="types">{type_badges(pokemon["types"])}</div>'
        f'</div>'
    )


st.set_page_config(page_title="포켓몬 도감", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

pokedex = fetch_pokedex()

st.markdown(
    '<div class="head"><h1>포켓몬 도감</h1><p>1세대 · 151마리</p></div>'
    f'<div class="dex">{"".join(card(p) for p in pokedex)}</div>'
    '<div class="credit">데이터: <a href="https://pokeapi.co/" target="_blank">PokeAPI</a></div>',
    unsafe_allow_html=True,
)
