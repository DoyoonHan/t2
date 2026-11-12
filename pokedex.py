"""포켓몬 속성(타입) 색상 관련 함수."""

# 이슈 #8 색상표의 속성별 라벨 색. 색상표가 이미지라서 라벨 띠의 색을 추출해 옮겼다.
TYPE_COLORS = {
    "normal": "#AEA794", "fire": "#F35806", "water": "#0467C5", "grass": "#399806",
    "electric": "#EFA802", "ice": "#6BD4F4", "fighting": "#C33028", "poison": "#6D256E",
    "ground": "#C9581C", "flying": "#5C73D1", "psychic": "#DE2F66", "bug": "#888C11",
    "rock": "#9E863C", "ghost": "#6C5583", "dragon": "#4E3BA4", "dark": "#3C2E25",
    "steel": "#908F9F", "fairy": "#DF8DE2",
}

# 한국어 속성 이름 → 영어 이름
KO_NAMES = {
    "노말": "normal", "불꽃": "fire", "물": "water", "풀": "grass", "전기": "electric",
    "얼음": "ice", "격투": "fighting", "독": "poison", "땅": "ground", "비행": "flying",
    "에스퍼": "psychic", "벌레": "bug", "바위": "rock", "고스트": "ghost", "드래곤": "dragon",
    "악": "dark", "강철": "steel", "페어리": "fairy",
}

UNKNOWN_COLOR = "#888888"  # 모르는 속성은 회색

LIGHT_TEXT = "#FFFFFF"
DARK_TEXT = "#000000"


def type_color(name):
    """속성 이름(영어 또는 한국어)을 받아 색상 값을 돌려준다. 모르는 속성은 회색."""
    key = (name or "").strip()
    key = KO_NAMES.get(key, key.lower())
    return TYPE_COLORS.get(key, UNKNOWN_COLOR)


def _luminance(hex_color):
    """WCAG 상대 휘도."""
    h = hex_color.lstrip("#")
    channels = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a, b):
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def text_color(background):
    """배경색 위에서 더 잘 읽히는 글자색(흰색 또는 검정)을 돌려준다."""
    if contrast_ratio(background, LIGHT_TEXT) >= contrast_ratio(background, DARK_TEXT):
        return LIGHT_TEXT
    return DARK_TEXT


# 지역(세대)별 전국도감 번호 범위. 순서대로 불러온다.
REGIONS = [
    ("관동", 1, 151),
    ("성도", 152, 251),
    ("호연", 252, 386),
    ("신오", 387, 493),
    ("하나", 494, 649),
    ("칼로스", 650, 721),
    ("알로라", 722, 809),
    ("가라르", 810, 905),
    ("팔데아", 906, 1025),
]


def region_range(name):
    """지역 이름을 받아 (시작 번호, 끝 번호)를 돌려준다. 없는 지역이면 ValueError."""
    for region, start, end in REGIONS:
        if region == name:
            return start, end
    raise ValueError(f"알 수 없는 지역: {name!r}")


# 지역 드롭다운에서 모든 지역을 차례로 보여 주는 선택지
ALL_REGIONS = "전체"


def region_options():
    """지역 드롭다운 선택지. "전체" 다음에 REGIONS 순서대로 지역 이름을 둔다."""
    return [ALL_REGIONS] + [name for name, _, _ in REGIONS]
