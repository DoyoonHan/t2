import requests
import streamlit as st

GRAPHQL_URL = "https://graphql.pokeapi.co/v1beta2"
KO = 3  # PokeAPI language_id for Korean
COLUMNS = 8

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

TYPE_COLORS = {
    "normal": "#A8A77A", "fire": "#EE8130", "water": "#6390F0", "electric": "#F7D02C",
    "grass": "#7AC74C", "ice": "#96D9D6", "fighting": "#C22E28", "poison": "#A33EA1",
    "ground": "#E2BF65", "flying": "#A98FF3", "psychic": "#F95587", "bug": "#A6B91A",
    "rock": "#B6A136", "ghost": "#735797", "dragon": "#6F35FC", "dark": "#705746",
    "steel": "#B7B7CE", "fairy": "#D685AD",
}


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


def type_badges(types):
    return " ".join(
        f'<span style="background:{TYPE_COLORS.get(en, "#888")};color:#fff;'
        f'padding:2px 8px;border-radius:10px;font-size:0.75rem;'
        f'display:inline-block;white-space:nowrap;margin:2px 0;">{ko}</span>'
        for en, ko in types
    )


st.set_page_config(page_title="포켓몬 도감", layout="wide")
st.title("포켓몬 도감")

pokedex = fetch_pokedex()

for start in range(0, len(pokedex), COLUMNS):
    cols = st.columns(COLUMNS)
    for col, pokemon in zip(cols, pokedex[start:start + COLUMNS]):
        with col.container(border=True):
            st.markdown(
                f'<div style="text-align:center;">'
                f'<img src="{pokemon["image"]}" alt="{pokemon["name"]}" loading="lazy" '
                f'style="width:100%;aspect-ratio:1;object-fit:contain;">'
                f'<div style="color:#888;font-size:0.8rem;">No.{pokemon["id"]:03d}</div>'
                f'<div style="font-weight:600;margin:2px 0 6px;">{pokemon["name"]}</div>'
                f'<div>{type_badges(pokemon["types"])}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
