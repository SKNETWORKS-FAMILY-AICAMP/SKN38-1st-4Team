# 참고 분석: 진입점과 pages 서열

- 대상: 참고 저장소 `SKNETWORKS-FAMILY-AICAMP/SKN38-1st-1Team` main, 커밋 `61ef27d0`(2026-11-11 08:56 +0900), 얕은 복제로 받아 읽기만 함.
- 우리 쪽 기준: `app.py` 372줄(2026-11-11 09:17 읽음, GPS 기능이 반영된 커밋 전 상태), Streamlit 1.67.0(`.venv` 에서 `streamlit.__version__` 확인).
- 줄 번호 표기: 참고 저장소는 `ref:파일:줄`, 우리 코드는 `파일:줄`.
- 실험: 스크래치패드의 작은 모형 앱 3개(`navtest`, `navtest2`, `navtest3`)를 `AppTest` 와 실제 브라우저(포트 8599, 확인 후 종료)로 돌려 봄. 프로젝트 파일은 하나도 고치지 않았다.

## 1 참고 저장소 사실

### 1.1 진입점 방식

| 사실 | 근거 |
|---|---|
| `st.navigation` + `st.Page` 방식이다. `pages/` 자동 인식에 기대지 않는다. | `ref:app.py:17-32` |
| `st.set_page_config` 는 진입점에서 한 번만 부른다. 화면 파일 9개 어디에도 없다. | `ref:app.py:13`, `pages/` 전체 grep 결과 0건 |
| 진입점이 공통 스타일·로고를 먼저 그린다: `apply_global_style()`, `show_logo()`(내부는 `st.logo`). | `ref:app.py:14-15`, `ref:services/ui.py:460-461`, `ref:services/ui.py:491-492` |
| 메뉴에 보이는 화면 6개와 숨김 화면 3개(`visibility="hidden"`)를 한 목록으로 넘긴다. 메뉴는 화면 위쪽에 둔다(`position="top"`). | `ref:app.py:18-32` |
| 푸터 순서: 본문 자리 `st.container()` 를 먼저 만들고, 푸터를 그린 뒤, 그 자리 안에서 `nav.run()`. 화면이 `st.stop()` 으로 중간에 끝나도 푸터가 본문 아래에 남게 하려는 것이라고 주석에 적혀 있다. | `ref:app.py:34-39` |
| 테마(색·글꼴·모서리)는 `.streamlit/config.toml`, 그 밖의 모양은 `services/ui.py` 의 CSS 문자열을 `st.html` 로 넣는다. | `ref:.streamlit/config.toml:1-32`, `ref:services/ui.py:1-10`, `ref:services/ui.py:460-461` |

### 1.2 번호·이름 규칙과 서열

| 사실 | 근거 |
|---|---|
| 파일 이름은 `숫자_영문PascalCase.py`(`0_Home`, `1_Delivery_Request` … `8_Driver_Login`). | `ref:README.md` 폴더 구조, `pages/` 목록 |
| 사이드바(여기서는 위쪽 메뉴) 표시 순서는 파일 번호가 아니라 `st.navigation` 에 넘긴 목록 순서로 정해진다. 메뉴 순서는 0 → 1 → 4 → 3 → 8 → 5 로 번호와 다르다. | `ref:app.py:18-25` |
| 표시 제목은 `st.Page(title=...)` 의 한글 제목, 아이콘은 `:material/...:`, 주소는 `url_path`(kebab-case, 예: `truck-map`, `booking-lookup`). 홈만 `default=True` 로 주소가 없다. | `ref:app.py:17-29` |
| 따라서 번호는 "만든 순서·파일 정렬용" 역할만 하고 화면 표시에 영향이 없다. | 위 두 줄에서 나온 결론(코드상 번호를 읽는 곳 없음) |
| 메뉴에 안 보이는 화면(매칭 결과·예약하기·요금표)은 버튼(`st.switch_page`)과 푸터 링크(`st.page_link`)로만 들어간다. | `ref:app.py:26-30`, `ref:pages/0_Home.py:27`, `ref:services/ui.py:540` |

### 1.3 화면 파일의 `services` import

| 사실 | 근거 |
|---|---|
| 화면 파일은 `from services.x import ...` 또는 `from services import a, b` 로 바로 가져온다. | `ref:pages/0_Home.py:8-10`, `ref:pages/2_Driver_Matching.py:13`, `ref:pages/3_Booking_Lookup.py:16-19` |
| `sys.path` 를 고치는 코드는 저장소 전체에 없다(`app.py`·`pages`·`services` grep 0건). Streamlit 이 진입점 폴더를 import 경로에 넣어 주는 동작에 기댄다. | grep 결과 |
| `services/__init__.py` 는 docstring 만 있고 "pages 에는 화면 코드만, 계산·조회 로직은 services" 라고 적어 둔다. | `ref:services/__init__.py:1-17` |
| `services/ui.py` 는 자기 위치 기준 한 단계 위의 `assets` 를 찾는다(`parents[1]`). | `ref:services/ui.py:20` |
| 의존 방향은 `app.py → services`, `pages → services` 한 방향이다. `services` 가 `pages` 를 import 하는 곳은 없다. 단, `services/ui.py` 는 푸터 링크에서 `pages/…py` 경로 문자열을 쓴다. | `ref:services/ui.py:532-540` |

### 1.4 공통 머리·사이드바·푸터와 화면 간 이동

| 사실 | 근거 |
|---|---|
| 공통 머리(로고)와 푸터는 진입점이 그리고, 그리는 함수는 `services/ui.py` 에 있다. 화면 파일은 공통부를 그리지 않는다. | `ref:app.py:11-15`, `ref:app.py:36-39`, `ref:services/ui.py:491-541` |
| 화면 간 이동은 `st.switch_page("pages/…py")`(진입점 기준 상대 경로 문자열). | `ref:pages/0_Home.py:25,27,62`, `ref:pages/6_Booking.py:32,65,104,118,120,218` |
| 화면 사이에 넘기는 값은 `st.session_state` 에 담는다. 여러 화면이 함께 쓰는 키는 `services` 에 상수로 둔다(`REQUEST_KEY`, `SELECTED_DRIVER_KEY`). 한 화면만 쓰는 키는 그 화면 위쪽 상수로 둔다. | `ref:pages/1_Delivery_Request.py:22-33,39-40`, `ref:pages/6_Booking.py:18,21-23` |
| 다른 화면으로 넘어가기 전에 값을 미리 정해 두는 방식도 쓴다(홈 → 지역별 현황으로 갈 때 `region_view` 를 정함). | `ref:pages/0_Home.py:61-62` |
| 같은 키 문자열이 두 화면에 중복 정의된 곳이 있다(`"lookup_auth"`). | `ref:pages/3_Booking_Lookup.py:23`, `ref:pages/6_Booking.py:23` |
| 앞 단계 값이 없으면 안내 → 이동 버튼 → `st.stop()` 으로 막는다. | `ref:pages/2_Driver_Matching.py:37-45`, `ref:pages/6_Booking.py:26-33` |

### 1.5 화면 파일 하나의 내부 순서

| 순서 | 내용 | 근거 |
|---|---|---|
| 1 | 모듈 docstring: 화면 이름, 진입 경로, 데이터 출처, 다른 화면과의 관계 | `ref:pages/1_Delivery_Request.py:1-7`, `ref:pages/5_FAQ.py:1-6` |
| 2 | import: 표준 라이브러리 → `streamlit` → `services` | `ref:pages/1_Delivery_Request.py:9-36` |
| 3 | 화면 상수와 세션 키 상수 | `ref:pages/1_Delivery_Request.py:38-40`, `ref:pages/3_Booking_Lookup.py:22-25` |
| 4 | 머리 표시(단계 표시·제목) | `ref:pages/1_Delivery_Request.py:42-44`, `ref:pages/2_Driver_Matching.py:29-30` |
| 5 | 세션 상태 읽기·초기화, 앞 단계 값 확인 | `ref:pages/1_Delivery_Request.py:46-60`, `ref:pages/6_Booking.py:26-33` |
| 6 | 화면 안에서만 쓰는 렌더 함수·콜백(`_select`, `address_picker` 등) | `ref:pages/1_Delivery_Request.py:66-191` |
| 7 | 본문(구역 주석 `# ── … ──` 또는 `# ===` 번호 구역) | `ref:pages/1_Delivery_Request.py:193-294`, `ref:pages/2_Driver_Matching.py:25-295` |

이 순서는 엄격하지 않다. 예약 조회 화면은 본문 중간에 함수를 정의한다(`ref:pages/3_Booking_Lookup.py:94,100,179,188`). 화면 파일에는 `if __name__ == "__main__"` 블록이 없다.

## 2 따라야 할 규칙

"참고 사실"은 1절에서 그대로 옮긴 것이고, "우리 선택"은 우리 조건(사이드바 유지, HTML 금지)에 맞춰 고른 것이다.

| 규칙 | 구분 |
|---|---|
| 진입점은 `app.py` 하나. `st.set_page_config` 는 여기서만 부른다. | 참고 사실 |
| 화면 목록은 `st.navigation([...])` 에 넘긴 순서가 곧 서열이다. 순서 목록은 홈 → FAQ → 분석 데이터 결과. | 참고 사실 + 우리 순서 |
| 파일 이름은 `숫자_영문PascalCase.py`. 번호를 현재 표시 순서와 같게 맞춰 `0_Home`, `1_FAQ`, `2_Analysis_Results` 로 한다(참고 저장소처럼 번호와 순서가 어긋나면 헷갈리므로). | 우리 선택 |
| 표시 제목은 `st.Page(title=...)` 로 지금 글자 그대로("홈 (주차장 탐색)", "FAQ", "분석 데이터 결과"). `url_path` 는 kebab-case(`faq`, `analysis-results`), 홈은 `default=True`. | 참고 규칙 + 우리 글자 |
| 공통부(브랜드 바, 서비스 요약 한 줄, 사이드바, 푸터)는 진입점이 그리고, 그리는 함수는 `services/ui.py` 에 둔다. | 참고 사실 |
| 화면 파일은 화면 코드만. 여러 화면이 쓰는 계산(거리, 등급, 데이터 로드)은 `services/` 로, 한 화면만 쓰는 렌더 함수는 그 화면 파일 안에 둔다. | 참고 사실(`ref:services/__init__.py:16`, `ref:pages/1_Delivery_Request.py:131`) |
| 의존 방향: `app.py → services`, `pages → services`. `services → pages` import 금지. `sys.path` 조작 금지. | 참고 사실 |
| 화면 이동은 `st.switch_page(<st.Page 객체 또는 "pages/…py">)`. 화면 사이 값은 `st.session_state`. | 참고 사실 |
| 화면 파일 내부 순서: docstring → import → 상수 → 상태 읽기 → 렌더 함수 → 본문. | 참고 사실(느슨한 관례) |
| 참고 저장소의 `st.html` + CSS 문자열 방식(`ref:services/ui.py:460-461`, 화면 곳곳의 `st.html`)은 따르지 않는다. 우리 README 원칙(HTML·CSS·JS 파일 없음, `unsafe_allow_html` 없음)에 어긋난다. Streamlit 기본 요소만 쓴다. | 우리 선택 |
| 사이드바는 참고 저장소의 위쪽 메뉴(`position="top"`)가 아니라 지금처럼 왼쪽 사이드바 버튼으로 둔다: `st.navigation(..., position="hidden")` + 사이드바에 버튼을 직접 그리고 누르면 `st.switch_page`. | 우리 선택(근거는 4절 측정) |

진입점이 될 모양(코드 초안, 아직 어디에도 쓰지 않음):

```python
# app.py (분해 후 초안)
"""침착: Streamlit 진입점 (실행: streamlit run app.py) — 공통부와 화면 목록만 둔다."""
import os
from pathlib import Path

if __name__ == "__main__":
    ...  # 지금 app.py:8-29 그대로

import streamlit as st

from services.parking_frame import load_frame          # 가칭, 5절 결정 1
from services.ui import render_brand_bar, render_footer, render_service_summary, render_sidebar
from service_config import PARKING_DATA_VERSION, SERVICE_DISTRICTS   # 위치는 ref-services 결과를 따름

st.set_page_config(page_title="침착 | 주차장 침수 위험도", page_icon="💧", layout="wide", initial_sidebar_state="expanded")
st.session_state["_kakao_rest_api_key"] = os.environ.get("KAKAO_REST_API_KEY", "").strip()

# 세션 상태 초기화 — 지금 app.py:163-179 그대로(모든 화면보다 먼저)
...

home = st.Page("pages/0_Home.py", title="홈 (주차장 탐색)", default=True)
faq = st.Page("pages/1_FAQ.py", title="FAQ", url_path="faq")
analysis = st.Page("pages/2_Analysis_Results.py", title="분석 데이터 결과", url_path="analysis-results")
nav = st.navigation([home, faq, analysis], position="hidden")

frame = load_frame()
render_brand_bar()
render_service_summary(frame)
render_sidebar([home, faq, analysis], current=nav)   # 버튼 key 는 지금처럼 f"nav_{title}"
body = st.container()
render_footer()
with body:
    nav.run()
```

## 3 우리 코드 대응표

옛 위치는 `app.py` 1–372줄을 빈틈 없이 나눈 것이다. 새 파일 이름 중 `services/parking_frame.py` 와 `services/faq.py` 는 가칭이다(5절 결정 1·2). 기존 루트 모듈(`parking_marker`, `parking_data`, `parking_map`, `service_config`)이 `services/` 로 옮겨지면 오른쪽 칸의 import 를 `services.` 접두로 바꾼다(ref-services 보고서 결과를 따름).

| 옛 위치 | 새 파일 | 이유 | 고쳐야 할 import·경로 |
|---|---|---|---|
| `app.py:1-4` 모듈 docstring | `app.py`(진입점 설명으로 고침) + 각 화면 파일 머리 docstring 새로 씀 | 참고 규칙 1.5-1 | 없음 |
| `app.py:5-6` `os`, `Path` | `app.py` | 직접 실행 블록·카카오 키에 필요 | 없음 |
| `app.py:7-29` 직접 실행 블록 | `app.py` 맨 위 그대로 | `launch.py`·`실행.bat` 과 "Run Python File" 이 이 파일을 부른다 | 없음. 화면 파일에는 넣지 않는다 |
| `app.py:30-31` `math` import | `services/parking_frame.py` | `distance()` 와 함께 이동 | 없음 |
| `app.py:32-35` `altair`·`pandas`·`streamlit` | `altair` → `pages/2_Analysis_Results.py`; `pandas` → `pages/0_Home.py`, `pages/2_Analysis_Results.py`, `services/parking_frame.py`; `streamlit` → 모든 파일 | 쓰는 곳에서만 import | 없음 |
| `app.py:36-40` 프로젝트 import | `parking_marker` → `pages/0_Home.py`(핀·범례) + `services/parking_frame.py`(`risk_band`, `RISK_BANDS`); `service_inventory` → `services/parking_frame.py`; `render_map` → `pages/0_Home.py`; `PARKING_DATA_VERSION` → `app.py`; `SERVICE_DISTRICTS` → `app.py`·`pages/0_Home.py`·`services/parking_frame.py` | 쓰는 곳으로 나눔 | 모듈이 `services/` 로 가면 `from services.parking_map import render_map` 처럼 바꿈. 같은 모듈을 두 경로로 import 하지 않기(4절 위험 3) |
| `app.py:41-43` `risk_band`, `RISK_BANDS` 별칭 | `services/parking_frame.py` | `level()`·`COLORS`·분석 화면이 함께 씀 | 화면은 `from services.parking_frame import RISK_BANDS, risk_band` |
| `app.py:44-47` `set_page_config`, 카카오 키 | `app.py`(`st.navigation` 보다 앞) | 참고 규칙: 설정은 진입점에서 한 번 | `kakao_panel.py:18` 이 `_kakao_rest_api_key` 를 읽으므로 키 이름 유지 |
| `app.py:48-49` `NOTE` | `services/ui.py` | 사이드바·홈·분석 세 곳이 씀 | 화면은 `from services.ui import NOTE` |
| `app.py:50-51` `ASSETS`, `LOGO` | `services/ui.py` | 브랜드 바·사이드바·홈 히어로가 씀 | 경로 기준이 바뀜: `Path(__file__).resolve().parents[1] / "assets"`(`ref:services/ui.py:20` 과 같은 방식) |
| `app.py:52-56` `FRAME`, `SERVICE_AREA`, `COLOR_MIN`, `COLOR_MAX` | `services/parking_frame.py` 의 함수(예: `load_frame()`, `color_range(frame)`, `SERVICE_AREA`) | 세 화면과 진입점이 모두 씀 | 모듈 맨 위 상수로 두지 말고 매 실행 부르는 함수로(4절 위험 6) |
| `app.py:57-61` `marker_icon()` | `pages/0_Home.py` | 홈 지도만 씀 | `COLOR_MIN/MAX` 를 `parking_frame` 에서 받음 |
| `app.py:62-64` `COLORS` | `services/parking_frame.py` | `RISK_BANDS` 와 "미산정" 글자에서 만들어지는 공용 값. 지금은 분석 화면만 씀 | 분석 화면이 import |
| `app.py:65-71` `FAQ` 목록 | `services/faq.py`(가칭, 참고 저장소에도 `services/faq.py` 가 있음) | 참고 구조: 화면은 표시만, 내용은 화면 밖 | `pages/1_FAQ.py` 가 `from services.faq import FAQ`. 데이터 파일로 뺄지는 5절 결정 2 |
| `app.py:72-77` `level()` | `services/parking_frame.py` | 모든 화면의 `frame["level"]` 과 홈 배지가 씀 | 홈이 import |
| `app.py:78-85` `distance()` | `services/parking_frame.py` | 계산 로직 | 없음 |
| `app.py:86-90` `badge()` | `pages/0_Home.py` | 홈 목록·상세만 씀 | `level` import |
| `app.py:91-93` 카카오 길찾기 비활성 주석 | `pages/0_Home.py`(상세 패널 근처) | 길찾기가 다시 켜지면 붙을 자리 | 없음 |
| `app.py:94-117` `detail()` | `pages/0_Home.py` | 홈 검색·비교에서만 씀(참고 관례: 한 화면 전용 렌더 함수는 그 화면에) | `NOTE` import |
| `app.py:118-129` `toggle_compare()`, `sync_compare()` | `pages/0_Home.py` | 홈 위젯 콜백 | 없음. `compare_ids` 키 문자열 유지 |
| `app.py:130-149` `legend()` | `pages/0_Home.py` | 홈 지도 범례 | `marker_svg`, `RISK_BANDS`, `COLOR_MIN/MAX` import |
| `app.py:150-156` 상단 브랜드 바 | `services/ui.py` 의 `render_brand_bar()`, `app.py` 에서 `nav.run()` 전에 호출 | 지금도 세 화면 모두 위에 나옴 | `LOGO` 경로(위 50–51 줄) |
| `app.py:157-161` 서비스 지역 요약 캡션 2줄 | `services/ui.py` 의 `render_service_summary(frame)`, `app.py` 에서 호출 | 세 화면 공통 | `unscored_count` 는 분석 화면이 따로 다시 셈(`app.py:330-334` 에서도 씀) |
| `app.py:162-168` 데이터 버전·`compare_ids`·`selected_id` 초기화 | `app.py`(`nav.run()` 전) | 어느 화면으로 들어와도 같은 상태여야 함 | 키 이름 그대로 |
| `app.py:169-180` 미리보기 기준점 초기화, `lat, lon` 읽기 | 172–179 → `app.py`; 180 → `pages/0_Home.py` 맨 위에서 `st.session_state["current_location"]` 읽기 | `test_gps_location.py:59,65` 가 이 기준점 값을 기대 | 키 `preview_location_version`, `current_location`, `parking_view_request`, `selected_id` 그대로 |
| `app.py:181-191` 사이드바(로고·문구·화면 버튼 3개·구분선·`NOTE`) | `services/ui.py` 의 `render_sidebar(pages, current)`, `app.py` 에서 호출. `st.navigation(..., position="hidden")` | 지금 모양·순서를 지키면서 참고 진입점 방식으로 | `sidebar_page` 키와 `page` 변수는 없어짐(다른 곳에서 안 읽음: 루트 `*.py` grep). 버튼 key `nav_{제목}` 유지, `on_click` 대신 `if st.button(...): st.switch_page(p)` |
| `app.py:192-194` 거리·등급 열 붙이기 | `services/parking_frame.py` 의 `with_distance(frame, lat, lon)` | 홈은 거리·등급, 분석은 등급이 필요 | 홈·분석 화면이 각자 호출 |
| `app.py:195-206` 화면 분기 `if page == …` 와 홈 히어로 | 분기(196)는 없어짐(`nav.run()` 이 대신함). 히어로 197–206 → `pages/0_Home.py` | 참고 구조 | `LOGO` import |
| `app.py:207-249` 홈 검색 조건·범위·안내 문구 | `pages/0_Home.py` | 홈 전용 | `SERVICE_DISTRICTS`, `SERVICE_AREA` import. 위젯 key `parking_query`, `parking_district` 와 `parking_scope`, `parking_radius` 유지 |
| `app.py:250-294` 홈 "주변 주차장 검색" 모드(목록·지도·상세) | `pages/0_Home.py` | 홈 전용 | `render_map`, `marker_icon`, `legend`, `detail` |
| `app.py:295-309` 홈 "주차장 상세 비교" 모드 | `pages/0_Home.py` | 같은 화면 안의 라디오 전환. 화면을 더 쪼개지 않음(5절 결정 4) | `compare_picker` key 유지 |
| `app.py:310-325` 홈 아래 "데이터 출처·계산 방법" 탭 | `pages/0_Home.py` | 지금 홈에만 나옴 | `frame` 의 `depth_reference_max`, `rain_reference_max` 사용 |
| `app.py:326-358` 분석 데이터 결과(`elif` 포함) | `pages/2_Analysis_Results.py` | 참고 구조: 화면 하나에 파일 하나 | `altair`, `pandas`, `COLORS`, `RISK_BANDS`, `risk_band`, `NOTE`, `SERVICE_AREA`, `with_distance`(또는 등급만) |
| `app.py:359-366` FAQ(`else` 포함) | `pages/1_FAQ.py` | 같음 | `from services.faq import FAQ` |
| `app.py:367-372` 푸터 | `services/ui.py` 의 `render_footer()`, `app.py` 에서 본문 자리를 먼저 만든 뒤 호출 | 참고 진입점의 푸터 순서(`ref:app.py:34-39`) | 없음 |

## 4 깨질 위험과 대비

### 4.1 측정한 사실

| 번호 | 측정 결과 | 영향 | 대비 |
|---|---|---|---|
| 1 | `AppTest.from_file` 로 `st.navigation` 진입점을 띄우면 첫 실행은 기본 화면(`default=True`)을 그린다. 루트 모듈 import 와 `mock.patch.object(모듈, ...)` 가 화면 파일 안까지 먹는다. 버튼 클릭 뒤 세션 상태 값도 읽힌다. (`navtest`) | `test_gps_location.py:43-55` 구조는 그대로 통과할 수 있다 | 홈을 `default=True` 로 두고, GPS 버튼(`gps_button`)은 홈 화면 안에 둔다 |
| 2 | `AppTest`(1.67)에서는 두 번째 실행부터 진입점이 그린 요소(사이드바·푸터·공통 캡션)가 요소 목록에서 빠지고 화면 파일 요소만 남는다. 첫 실행 목록: `entry-before, page-a, entry-after, side`. 다시 실행: `page-a`. (`navtest2`) | 지금 GPS 테스트는 버튼 클릭 뒤 화면 안의 캡션·경고만 보므로(`test_gps_location.py:55,60`) 영향 없음. 클릭 뒤 사이드바나 공통 캡션을 검사하는 테스트를 새로 쓰면 실패한다 | 공통부 검사는 첫 실행 결과로만 한다. GPS 캡션·경고는 화면 파일(또는 화면 파일이 부르는 `parking_map`) 안에서 그린다 |
| 3 | `AppTest` 에서 진입점 사이드바 버튼 → `st.switch_page` 전환은 재현되지 않았다(클릭 뒤에도 홈). 대신 `at.switch_page("pages/1_FAQ.py")` 는 동작한다. 실제 브라우저에서는 같은 코드로 버튼을 누르면 `/faq` 로 바뀌고, 바뀐 뒤에도 진입점 사이드바가 남는다. `position="hidden"` 이면 자동 메뉴는 안 생긴다(사이드바에서 "FAQ" 글자는 버튼 하나만 찾힘). (`navtest3`, 포트 8599) | 화면 전환 테스트는 버튼 클릭으로 못 쓴다 | 테스트에서는 `at.switch_page(...)` 를 쓴다 |
| 4 | 화면을 떠나면 그 화면 위젯 상태(`parking_query` 등)가 지워진다. 옛 방식(한 파일 + `sidebar_page`)과 새 방식(`st.navigation`) 모두 같았다. 위젯이 아닌 키(`compare_ids`)는 남는다. (`navtest3`) | 바뀌는 동작 없음 | 화면을 넘어 남아야 하는 값은 지금처럼 위젯이 아닌 키(`compare_ids`, `selected_id`, `current_location`, `parking_scope`, `parking_radius`)로 둔다 |

### 4.2 코드에서 읽은 사실

| 번호 | 내용 | 대비 |
|---|---|---|
| 5 | 테스트는 `app.py` 를 경로로 직접 띄운다(`test_gps_location.py:10,44`). `launch.py:50` 과 `실행.bat:9`(→ `launch.py`)은 `streamlit run app.py` 를 쓴다. | 진입점 이름·위치를 `app.py` 로 유지하면 셋 다 손댈 필요가 없다 |
| 6 | `FRAME = service_inventory()` 는 지금 매 실행 호출된다(`app.py:52`). 그 아래 `load_parking_data` 만 `st.cache_data`(`parking_data.py:12-13`)이고 파일 수정 시각을 인자로 받는다. | `services` 모듈 맨 위 상수로 옮기면 프로세스당 한 번만 계산되어, 다른 세션이 데이터를 갱신해도 서버를 다시 켜야 반영된다. 함수로 두고 `app.py`·화면에서 매번 부른다 |
| 7 | GPS 테스트가 `parking_map.get_geolocation` 을 바꿔치기한다(`test_gps_location.py:7,43`). | `parking_map` 이 `services/` 로 옮겨지면 테스트와 화면이 같은 경로(`services.parking_map`)로 import 해야 한다. 한쪽이 `parking_map`, 다른 쪽이 `services.parking_map` 이면 모듈이 두 개 생겨 바꿔치기가 안 먹는다 |
| 8 | 화면 간 공유 키는 여러 파일에 문자열로 흩어져 있다: `parking_map.py:37-147`(`parking_view_request`, `location_*`, `gps_*`, `selected_id`, `current_location`, `map_show_all`), `app.py:163-217`, 테스트(`current_location`, `location_lat`, `location_lon`, `gps_pending`). | 키 문자열을 바꾸지 않는다. 상수 모듈로 모으는 일은 이번 분해와 따로 한다 |
| 9 | `LOGO` 는 `app.py` 위치 기준 `assets` 를 찾는다(`app.py:50-51`). | `services/ui.py` 로 옮기면 `parents[1]` 로 바꾼다 |
| 10 | 직접 실행 블록(`app.py:8-29`)은 Streamlit 실행 맥락이 없을 때만 동작한다. | 진입점 맨 위에 그대로 둔다. 화면 파일에는 넣지 않는다 |
| 11 | `prepare.bat:56` 은 `app.py parking_marker.py` 만 문법 검사한다. | 분해 뒤 `pages\*.py`, `services\*.py` 도 넣어야 한다(ref-scripts-sql 범위) |
| 12 | `kakao_panel.py:20` 오류 문구가 "app.py 맨 위의 KAKAO_REST_API_KEY" 를 가리키지만 실제로는 환경 변수에서 읽는다(`app.py:47`). | 분해와 무관한 낡은 문구. 한 줄 보고만 함 |

### 4.3 추측(확인 필요)

| 번호 | 내용 | 확인 방법 |
|---|---|---|
| 13 | 사이드바 모양: `st.navigation(position="hidden")` + 직접 그린 버튼이면 지금 모양(로고·문구·버튼 3개·현재 화면 강조)이 그대로일 것이다. 강조는 `nav.url_path` 비교로 할 수 있었다(모형 앱에서 예외 없음). | 분해 뒤 `~/.claude/local/app-verification/verify-app` 스크린샷 |
| 14 | 첫 접속 주소가 `/` 에서 그대로 홈이고, 예전 북마크(주소 하나뿐이던 시절)는 계속 홈으로 간다. | 같은 스크린샷 |
| 15 | 다른 세션 '점수 미산정처리 원인'의 수정 목록에는 `app.py` 가 없지만, `README.md`·`RISK_MODEL.md` 의 화면 설명이 바뀌면 FAQ·계산 방법 문구(`app.py:66,70,321-325`)와 어긋날 수 있다. | 분해와 그 세션 작업 중 나중 쪽이 문구를 맞춘다 |
| 16 | 'GPS 현재위치 기능' 세션이 아직 살아 있다. 그 세션이 `app.py`·`parking_map.py` 를 다시 고치면 분해 작업과 겹친다. | 분해 시작 전에 그 세션이 끝났는지 확인 |

## 5 메인 세션이 정할 것

| 번호 | 정할 것 | 이 보고서의 추천 | 맞춰 볼 곳 |
|---|---|---|---|
| 1 | 공용 계산 모듈 이름과 자리: 새 `services/parking_frame.py`(가칭) 로 만들지, 옮겨질 `parking_data` 에 합칠지 | 새 모듈 하나(거리·등급·데이터 로드·색 범위·`COLORS`·`SERVICE_AREA`). `parking_data` 는 원본 읽기만 남김 | ref-services 보고서 |
| 2 | FAQ 내용 자리: `services/faq.py` 상수, 또는 참고 저장소처럼 `data/faq/` 파일 + 읽기 함수 | `services/faq.py` 상수(새 파일 형식·읽기 코드를 늘리지 않음) | ref-data-docs 보고서(`ref:data/faq/jimni_faq.md`, `ref:services/faq.py`) |
| 3 | 사이드바 방식: 직접 그린 버튼(`position="hidden"`) 또는 Streamlit 기본 사이드바 메뉴(`position="sidebar"`, 코드가 짧지만 모양이 바뀜) | 직접 그린 버튼(지금 모양·순서 유지, 실제 브라우저에서 전환 확인함) | 4절 3, 13 |
| 4 | 홈의 "주변 검색 / 상세 비교" 를 화면 두 개로 더 쪼갤지 | 쪼개지 않음. 사용자 요구는 세 화면 유지이고, 라디오 전환을 화면 전환으로 바꾸면 위젯 상태가 지워짐(4절 4) | 사용자 |
| 5 | `detail()`·`badge()`·`legend()` 를 홈 파일에 둘지 `services/ui.py` 에 둘지 | 홈 파일(홈만 씀, 참고 관례). 홈 파일은 약 230줄로 참고 화면(최대 305줄) 범위 안 | 없음 |
| 6 | `url_path` 이름(`faq`, `analysis-results`)과 파일 번호(0·1·2) | 위 이름 그대로 | 없음 |
| 7 | 분해 시작 시점 | GPS 세션 종료와 기준 커밋 뒤. `app.py` 는 한 세션만 고친다 | 4절 16 |
| 8 | 분해 뒤 테스트 추가 여부: `at.switch_page` 로 FAQ·분석 화면이 예외 없이 뜨는지 보는 테스트 | 추가 권장(지금은 세 화면 중 홈만 테스트가 띄움) | 4절 3 |
