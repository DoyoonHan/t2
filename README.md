# 포켓몬 도감

1세대 포켓몬(No.001 ~ No.151)을 한눈에 볼 수 있는 Streamlit 도감 페이지입니다.
포켓몬 데이터는 [PokeAPI GraphQL](https://graphql.pokeapi.co/v1beta2)에서 가져옵니다.

## 주요 내용

- 1세대 포켓몬 151마리를 가로 8칸 바둑판 형식으로 나열
- 카드마다 **이미지 · 번호 · 이름 · 속성**만 표시
- 이름과 속성은 한국어로 표시
- Spotify 디자인 시스템을 참고한 다크 테마 ([DESIGN.md](DESIGN.md))
- 화면 폭에 따라 열 수가 자동으로 줄어드는 반응형 그리드 (8 → 6 → 4 → 2칸)

## 기술 스택

| 구분 | 사용 기술 |
|---|---|
| 웹 UI | [Streamlit](https://streamlit.io/) |
| 데이터 | [PokeAPI](https://pokeapi.co/) GraphQL (`https://graphql.pokeapi.co/v1beta2`) |
| HTTP | requests |
| 언어 | Python 3.15 |

## 프로젝트 구조

```
.
├── app.py                  # Streamlit 앱 (데이터 조회 + 화면 렌더링)
├── DESIGN.md               # 디자인 참고 문서 (Spotify 스타일)
├── requirements.txt        # 의존 패키지 목록
└── .streamlit/
    └── config.toml         # Streamlit 테마 설정 (다크 테마)
```

## 시작하기

### 1. 저장소 받기

```bash
git clone https://github.com/DoyoonHan/t2.git
cd t2
```

### 2. 가상환경 만들기

Python 3.15를 기준으로 개발했습니다.

```bash
python -m venv .venv
```

[uv](https://docs.astral.sh/uv/)를 쓴다면 다음 명령으로도 만들 수 있습니다.

```bash
uv venv .venv --python 3.15 --seed
```

### 3. 가상환경 활성화

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 4. 패키지 설치

```bash
pip install -r requirements.txt
```

### 5. 실행

```bash
streamlit run app.py
```

브라우저에서 <http://localhost:8501> 이 열리면 도감을 볼 수 있습니다.

## 참고 사항

- 첫 실행 시 PokeAPI에서 151마리 데이터를 한 번에 받아옵니다. 받은 데이터는 Streamlit 캐시(`st.cache_data`)에 저장되어, 새로고침해도 다시 요청하지 않습니다.
- 인터넷 연결이 필요합니다. 포켓몬 이미지는 PokeAPI 스프라이트 저장소(GitHub)에서 직접 불러옵니다.
- `.streamlit/config.toml`의 테마 설정은 서버를 다시 시작해야 적용됩니다.

## 디자인 브랜치

같은 도감을 여러 디자인 시스템으로 만든 브랜치가 있습니다. 각 브랜치의 `DESIGN.md`가 참고한 디자인 문서입니다.

| 브랜치 | 디자인 |
|---|---|
| `master` | Spotify 스타일 (다크 테마) |
| `spotify-design` | Spotify 스타일 (다크 테마) |
| `vercel-design` | Vercel 스타일 (밝은 캔버스, 메시 그라데이션 히어로) |
| `notion-design` | Notion 스타일 (네이비 히어로, 파스텔 속성 태그) |

다른 디자인을 보려면 브랜치를 바꾼 뒤 Streamlit을 다시 시작하세요.

```bash
git checkout vercel-design
```

디자인 참고 문서 출처: [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)

## 데이터 출처

- 포켓몬 데이터와 이미지: [PokeAPI](https://pokeapi.co/)
- Pokémon 및 관련 이름은 Nintendo, Game Freak, The Pokémon Company의 상표입니다.
