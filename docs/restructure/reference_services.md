# 참고 저장소 `services/` 분석과 우리 코드 대응표

- 참고 저장소: `SKNETWORKS-FAMILY-AICAMP/SKN38-1st-1Team` main, 커밋 `61ef27d0` (2026-11-11 08:56 +0900), `--depth 1` 로 받아 읽기만 함.
- 아래 `services/…:줄` 은 참고 저장소, 접두어 없는 파일(`app.py:…`, `parking_map.py:…` 등)은 이 프로젝트의 현재 위치다.
- 작성: 2026-11-11, 읽기 전용 분석 세션(ref-services). 이 프로젝트의 다른 파일은 고치지 않았다.

## 1 참고 저장소 사실

### 1.1 모듈 크기와 책임 (21개, 3,378줄)

| 모듈 | 줄 | streamlit import | 책임 (docstring 기준) |
|---|---|---|---|
| `__init__.py` | 17 | 없음 | 모듈 목록 docstring 만 |
| `ui.py` | 563 | `ui.py:17` | 공통 CSS·로고·푸터·단계 표시 |
| `fare.py` | 641 | 없음 | 카카오 거리 + 운임 계산·차량 추천 (`fare.py:1-5`) |
| `driver_map.py` | 313 | `driver_map.py:30` | 기사 위치 지도(pydeck) |
| `kakao_local.py` | 217 | `kakao_local.py:25` | 카카오 Local API 주소 검색 + 위치 지도 |
| `truck_map.py` | 213 | `truck_map.py:19` | 시도별 버블 지도(pydeck) |
| `booking_lookup.py` | 161 | 없음 | 예약 조회·평점 저장 |
| `booking.py` | 147 | 없음 | 예약 저장 |
| `agreement.py` | 139 | 없음 | 운임 합의 해시 |
| `fare_table.py` | 138 | 없음 | 운임 기준 상수표 |
| `driver_sim.py` | 123 | `driver_sim.py:24` | 엑셀 기반 시연용 기사 분포 |
| `matching.py` | 110 | 없음 | 기사 검색·추천, `haversine_km` |
| `faq.py` | 88 | `faq.py:13` | FAQ 조회(DB 우선, JSON 대체)·검색 |
| `transport_request.py` | 88 | 없음 | 요청 입력값 정의·검증, session_state 키 상수 |
| `fare_rules_db.py` | 77 | `fare_rules_db.py:9` | 요금표 DB 조회 → 표 |
| `assignment.py` | 67 | 없음 | 기사 배정·예약 확정 |
| `settlement.py` | 64 | 없음 | 수수료·정산 계산 |
| `truck_stats.py` | 58 | `truck_stats.py:15` | 화물차 등록 통계 조회 |
| `fare_view.py` | 55 | `fare_view.py:10` | 요금표 화면 조각 |
| `db.py` | 54 | 없음 | MySQL 연결 |
| `notifications.py` | 45 | `notifications.py:12` | 사이트 내부 알림 문구·표시 |

### 1.2 사실과 해석

| 사실 (파일:줄) | 해석·추측 |
|---|---|
| 이름은 업무 명사 하나(`faq`, `matching`, `booking`, `settlement`)이고, 접미사로 성격을 드러낸다: `_view` = 화면 조각(`fare_view.py:1` "요금표 화면 조각"), `_db` = DB 조회(`fare_rules_db.py:1`), `_table` = 상수표(`fare_table.py:1`), `_map` = pydeck 지도(`truck_map.py`, `driver_map.py`), `_stats`·`_sim` = 자료 집계 | 접미사 규칙은 문서로 정해진 것은 아니고 파일 이름에서 읽은 관례다 |
| 외부 API 모듈은 `제공자_API이름`: `kakao_local.py:1-10` (카카오 Local API). DB 연결은 `db.py` 하나(`db.py:36 get_connection`) | |
| 모듈 하나는 대체로 50~320줄. 예외는 `fare.py` 641줄, `ui.py` 563줄(그중 `_CSS` 문자열이 `ui.py:34-458`) | |
| streamlit 을 import 하는 10개 중 화면을 그리는 모듈은 `ui`, `fare_view`, `notifications`, `kakao_local`, `truck_map`, `driver_map`. 나머지 `faq`, `fare_rules_db`, `truck_stats`, `driver_sim` 은 `st.cache_data` 만 쓴다(`faq.py:21,28`, `fare_rules_db.py:27`, `truck_stats.py:32`, `driver_sim.py:43,101`) | 경계는 "streamlit 유무"가 아니라 "화면을 그리느냐"다. 캐시를 위한 streamlit import 는 자료 모듈에도 허용된다 |
| 순수 계산 모듈 11개(`agreement`, `assignment`, `booking`, `booking_lookup`, `db`, `fare`, `fare_table`, `matching`, `settlement`, `transport_request`, `__init__`)는 streamlit 을 import 하지 않는다. `transport_request.py:45-46` 은 session_state 키 이름만 상수로 두고 직접 읽지 않는다 | |
| 순수 모듈 안에도 HTML 문자열을 돌려주는 함수가 있다: `matching.py:109 avatar_html`, `truck_map.py:103 legend_html`, `driver_map.py:293 zoom_map_html` | 이 프로젝트 README 원칙(HTML 금지)과 맞지 않으므로 따라 하지 않는다 |
| `__init__.py` 는 docstring 뿐이다. `__all__`·import 없음(`services/__init__.py:1-17`). docstring 은 11개 모듈만 적고 나머지 10개(`ui`, `faq`, `driver_map` 등)는 빠졌다. 원칙 문장: "페이지(pages/)에는 화면 코드만 두고, 계산·조회 로직은 이 폴더에 작성합니다."(`services/__init__.py:16`) | docstring 목록은 갱신이 밀린 상태다 |
| pages 의 import 형태 세 가지: 이름 직접 `from services.faq import ALL, …`(`pages/5_FAQ.py:10`), 모듈 묶음 `from services import agreement, fare, matching, settlement`(`pages/2_Driver_Matching.py:13`), 별칭 `from services import booking_lookup as bl`(`pages/3_Booking_Lookup.py:16`), `from services import driver_map as dm`(`pages/4_Truck_Map.py:18`). 진입점은 `from services.ui import …`(`app.py:11`) | |
| pages 에는 `sys.path` 조작이 없다(pages 전체 grep 0건). `app.py:17-32` 가 `st.navigation` 으로 pages 를 실행하므로 루트가 import 경로가 된다 | |
| scripts 는 두 방식: `sys.path.insert(0, ROOT)`(`scripts/load_faqs.py:28-29`, `scripts/test_booking_lookup.py:17-18`) 또는 `python -m scripts.이름` 실행 전제(`scripts/seed_drivers.py:6`, `scripts/collect_driver_places.py:15`) | |
| services 사이 의존: 화면 조각 → 자료·계산(`fare_view.py:12-14`), 지도 → 다른 지도 상수·계산(`driver_map.py:33-34`), 계산 → 외부 API(`matching.py:12`). 화면 조각을 import 하는 계산 모듈은 없다 | 방향은 pages → (view/map) → (계산·자료) → (db·외부 API) |
| scripts 가 밑줄 함수를 가져다 쓴다: `kakao_local._get`(`scripts/collect_driver_places.py:29`), `truck_stats._load_queries`(`scripts/seed_drivers.py:17`) | 공개 범위가 느슨하다. 따라 하지 않는 편이 낫다 |
| 경로는 모두 `Path(__file__).resolve().parents[1]` 로 루트를 잡고 모듈마다 직접 계산한다: `db.py:21`, `faq.py:17`, `driver_sim.py:26`, `truck_map.py:21`, `truck_stats.py:19`, `driver_map.py:127`, `ui.py:20`, `kakao_local.py:28`. 중앙 경로 모듈은 없다. 예외: `fare.py:31` 은 경로 없이 `load_dotenv()` | |
| 파일이 바뀌면 캐시를 새로 읽게 `mtime` 을 인자로 넘긴다: `faq.py:29`, `truck_map.py:62`, `driver_sim.py:44` | 우리 `parking_data.py:13,31` 과 같은 방식이다 |
| `st.cache_resource` 는 이미지·아이콘에만: `ui.py:464,479`, `driver_map.py:131` | |
| 무거운 의존은 함수 안에서 늦게 import: `driver_sim.py:108`(DB 없이 엑셀만 쓰는 스크립트 배려), `kakao_local.py:204`(pydeck) | |
| `ui.py` 함수 목록: `apply_global_style`(`:460`, `st.html(_CSS)`), `logo_image`(`:465`), `image_data_uri`(`:473`), `trimmed_image`(`:480`), `show_logo`(`:491`, `st.logo`), `asset`(`:495`, 자산 경로 문자열), `section_title`(`:499`), `how_it_works`(`:505`), `stat_cards`(`:516`), `render_footer`(`:523`), `status_stepper`(`:545`), `step_header`(`:556`). 상수: 색 토큰(`:21-23`), `REQUEST_STEPS`(`:25`), `STEP_DETAILS`(`:26`) | `ui.py` 는 CSS 주입(`st.html`)과 HTML 조각이 중심이라 우리 README 원칙과 충돌한다. "공통 머리·바닥·자산 경로를 한곳에" 라는 역할만 가져온다 |
| `app.py:34-39` 는 본문 자리를 먼저 만들고 `render_footer()` 뒤 `nav.run()` 해서 푸터를 항상 아래에 둔다 | pages 세션 범위지만 `ui.render_footer` 를 만들면 같은 방식이 필요하다 |
| 테스트 폴더는 없다. 테스트 하나가 `scripts/test_booking_lookup.py` 에 있다 | |

## 2 따라야 할 규칙

1. 의존 방향은 `app.py`·`pages/*` → `services/*` 한 방향이다. services 는 pages 를 import 하지 않는다. services 안에서는 화면 조각(`_view`, `_map`, `ui`, `compare`) → 자료(`*_data`, `service_config`) → 순수 계산(`risk_model`, `parking_marker`, `map_payload`) → 표준 라이브러리·외부 API(`kakao_navi`) 순서로만 내려간다.
2. 순수 계산 모듈은 streamlit 을 import 하지 않는다. 자료 모듈은 `st.cache_data` 를 위해서만 streamlit 을 import 할 수 있다. 화면을 그리는 함수(`st.write`, `st.button`, `st.session_state` 사용)는 `_view` 또는 `_map` 모듈, 공통 머리·바닥은 `ui.py` 에 둔다.
3. 이름: 업무 명사 하나 + 성격 접미사(`_view`, `_map`, `_data`, `_config`). 외부 API 는 `kakao_` 접두어 + API 이름. 공개 함수 이름은 그대로 두고, 밑줄 함수는 다른 모듈에서 가져다 쓰지 않는다.
4. 경로는 모듈마다 `Path(__file__).resolve().parents[1]` 로 루트를 잡는다. `services/` 로 한 단계 깊어지므로 지금의 `.parent` 는 모두 `parents[1]` 로 바뀐다.
5. `st.cache_data` 는 파일을 읽는 services 함수에 붙이고, 파일 변경 감지는 `mtime` 인자로 한다(지금 방식 유지).
6. `services/__init__.py` 는 docstring 으로 모듈 목록과 원칙만 적고 아무것도 내보내지 않는다. 목록은 실제 파일과 맞춘다(참고 저장소는 어긋나 있음).
7. 이 프로젝트에서 바꾸는 부분: HTML·CSS 문자열과 `st.html`·`unsafe_allow_html` 은 쓰지 않는다(README 원칙). 참고 `ui.py` 의 `_CSS`, `section_title`, `how_it_works` 류는 가져오지 않는다.

## 3 우리 코드 대응표

새 모듈 칸은 제안이다. "현재 import 하는 곳" 은 이동 뒤 `from services.<모듈> import …` 로 바꿔야 하는 줄이다.

### 3.1 기능 모듈 9개 (공개 함수·상수 전부)

| 옛 위치 | 새 모듈 | 이유 | 고쳐야 할 import·경로 |
|---|---|---|---|
| `service_config.py` 전체: `PARKING_DATA_VERSION`(:11), `DATA`(:12), `PARKING_DISTRICTS`(:15), `RAINFALL_DISTRICTS`(:21), `SERVICE_DISTRICTS`(:23) | `services/service_config.py` (이름 유지) | 순수(streamlit 없음). 서비스 범위 설정 | 경로 `service_config.py:12` `Path(__file__).parent / "data"` → `Path(__file__).resolve().parents[1] / "data"`. import 하는 곳: `parking_data.py:7`, `app.py:40`, `test_risk_inventory.py:10` |
| `risk_model.py` 전체: `finite_number`(:6), `normalize_by_max`(:14), `distance_score`(:23), `rainfall_risk`(:34), `weighted_risk`(:43), `annual_rainfall_metrics`(:54) | `services/risk_model.py` (유지) | 순수 계산식 | 경로 없음. import 하는 곳: `risk_data.py:11`, `build_rainfall.py:20`, `test_risk_model.py:3` |
| `risk_data.py` 전체: `RISK_DATA_VERSION`(:13), `read_flood_points`(:16), `attach_risk_data`(:47-48) | `services/risk_data.py` (유지) | 자료 결합. `st.cache_data` 용 streamlit 만 사용(참고 `faq.py:21` 과 같은 경우) | 자기 import `risk_data.py:11` → `from services.risk_model import …`. 자기 경로 없음(`data_dir` 인자, `parking_data.py:34` 에서 받음). import 하는 곳: `parking_data.py:6`, `sql/build_dump.py:165` |
| `parking_data.py` 전체: `DATA_VERSION`(:9), `load_parking_data`(:12-13), `parking_inventory`(:29), `service_inventory`(:37) | `services/parking_data.py` (유지) | 자료 적재 + 캐시 | 경로 `parking_data.py:30` `Path(__file__).parent / "data" / …` → `parents[1]`. 자기 import `:6` → `services.risk_data`, `:7` → `services.service_config`. import 하는 곳: `app.py:38`, `test_risk_inventory.py:8`, `sql/build_dump.py:163` |
| `parking_marker.py` 전체: `MARKER_VERSION`(:6), `normalized_marker_score`(:9), `RISK_BANDS`(:18), `risk_band`(:27), `marker_svg`(:34-35), `marker_icon`(:84) | `services/parking_marker.py` (유지) | 순수. SVG 문자열은 `st.image`·pydeck 아이콘 자료일 뿐 HTML 화면 조각이 아니다 | 경로 없음. import 하는 곳: `app.py:37`(`import parking_marker as marker_source`), `test_parking_marker.py:3`, `test_risk_inventory.py:9`, `sql/build_dump.py:122,164`, `prepare.bat:56`(py_compile 대상 경로), `prepare.bat:58`(`from parking_marker import …`) |
| `map_payload.py`: `json_records`(:5) | `services/map_payload.py` (유지) | 순수. 지도 모듈에 합치면 순수 테스트(`test_map_payload`)가 streamlit·pydeck 에 묶인다 | 경로 없음. import 하는 곳: `parking_map.py:14`, `test_map_payload.py:6`, `test_risk_inventory.py:7` |
| `parking_map.py` 전체: `GPS_ERRORS`(:17), `GPS_INSECURE_ORIGIN`(:23), `LOCATION_PRESETS`(:27), `read_gps_result`(:61), `map_controls`(:125), `render_map`(:154). 밑줄 함수 `_show_all_changed`(:36), `_radius_changed`(:40), `_preset_changed`(:44), `_valid_coordinate`(:49), `_apply_location`(:53), `_request_gps`(:88), `_gps_location`(:94), `_map_selected`(:118) | `services/parking_map.py` (유지, GPS 포함 한 모듈) | 참고 `truck_map.py`·`driver_map.py` 와 같은 지도 모듈. 200줄이라 참고 모듈 크기 범위 안. GPS 를 떼면 테스트의 가짜 함수 대상이 바뀐다(5절 4번) | 자기 import `parking_map.py:14` → `from services.map_payload import json_records`. `:12` `streamlit_js_eval` 은 외부 패키지라 그대로. import 하는 곳: `app.py:39`, `test_gps_location.py:7`(`import parking_map` → `from services import parking_map`), `test_gps_location.py:8`, `test_gps_location.py:43`(`mock.patch.object(parking_map, "get_geolocation")` — 7번 줄을 바꾸면 그대로 동작, 2026-11-11 스크래치패드 시험판으로 확인) |
| `kakao_navi.py`: `DirectionsError`(:8), `directions`(:12) | `services/kakao_navi.py` (유지) | 외부 API(카카오모빌리티 길찾기), 표준 라이브러리만. 참고 `kakao_local.py` 이름 규칙과 같다 | 경로 없음. import 하는 곳: `kakao_panel.py:8`(함수 안 import) |
| `kakao_panel.py`: `route_panel`(:6) | `services/kakao_navi_view.py` (모듈 이름 변경, 함수 이름 유지) | 화면 조각이므로 `_view` 규칙(참고 `fare_view.py:1`). `kakao_navi` 와 짝이 보이게 | `kakao_panel.py:8` → `from services.kakao_navi import directions, DirectionsError`. import 하는 곳 없음(`app.py:93` 은 주석). 키는 `app.py:47` 이 session_state 에 넣는다 — app.py 에 남긴다 |

### 3.2 `app.py` 안의 도우미

| 옛 위치 | 새 모듈 | 이유 | 고쳐야 할 import·경로 |
|---|---|---|---|
| `level`(`app.py:74-77`) | `services/parking_marker.py` `level` | 순수. `risk_band` 위 얇은 포장이라 같은 곳에 둔다 | 호출처 `app.py:89,194`. `badge` 가 쓰므로 `parking_view` 가 import |
| `distance`(`app.py:80-85`) | `services/parking_search.py` `distance` (새 모듈) | 순수. 참고 저장소는 거리 함수를 쓰는 업무 모듈에 둔다(`matching.py:43 haversine_km`). 우리는 홈의 주변 검색만 쓴다(`app.py:193`). 지도 모듈에 넣으면 순수 함수가 streamlit 에 묶인다 | `from math import …`(`app.py:31`) 도 함께 옮긴다 |
| `badge`(`app.py:88-90`) | `services/parking_view.py` `badge` (새 모듈) | `st.badge` 를 그리는 화면 조각 → `_view` | `from services.parking_marker import level` 필요. 호출처 `app.py:100,269` |
| `detail`(`app.py:95-117`) | `services/parking_view.py` `detail` | 상세 패널 화면 조각. 탐색·비교 두 곳에서 쓴다(`app.py:294,309`) | `NOTE` 를 `services.risk_model` 에서, `badge` 를 같은 모듈에서. `import pandas as pd` 필요 |
| `toggle_compare`(`app.py:120-125`), `sync_compare`(`app.py:128-129`) | `services/compare.py` (새 모듈) | 비교함 상태 콜백. session_state 키 `compare_ids`·`compare_picker` 를 한곳에 모은다(참고 `transport_request.py:45-46` 이 키를 모듈에 모으는 방식) | 호출처 `app.py:274`(on_click), `app.py:300`(on_change). 초기값 `app.py:164-166` 의 `compare_ids` 는 페이지에 남는다 |
| `legend`(`app.py:132-149`) | `services/parking_map.py` `legend` | 지도 범례는 지도 모듈 책임(참고 `truck_map.py:103 legend_html`). HTML 대신 `st.image` 로 그리는 지금 방식 유지 | 전역 `COLOR_MIN/MAX` 를 못 보므로 인자 추가: `legend(map_data, color_min, color_max, per_row=6)` — 이름 유지, 매개변수만 늘림. `from services.parking_marker import RISK_BANDS, marker_svg` 필요. 호출처 `app.py:285` |
| `marker_icon`(`app.py:59-60`) | 삭제(호출처에서 `services.parking_marker.marker_icon` 직접 호출) | `services.parking_marker.marker_icon` 과 이름이 겹친다. 포장이 하는 일은 `COLOR_MIN/MAX` 전달뿐 | 호출처 `app.py:279` → `marker_icon(score, selected, color_min, color_max)` |
| `COLORS`(`app.py:63-64`) | `services/parking_marker.py` `COLORS` | `RISK_BANDS` 에서 만든 등급→색 표. 등급 정의와 같은 곳 | 호출처 `app.py:332,340` |
| `FAQ` 목록(`app.py:65-71`) | `services/faq.py` `FAQ` (새 모듈, streamlit 없음) | 참고 `faq.py` 가 FAQ 자료를 맡는다. 우리 FAQ 는 리터럴이라 순수 모듈로 충분 | `sql/build_dump.py:105-112` 가 `ast.parse(ROOT / "app.py")` 로 `FAQ` 를 찾는다 → `from services.faq import FAQ` 로 바꾸거나 파싱 대상을 `services/faq.py` 로. docstring `sql/build_dump.py:5-6`, SQL 주석 `:138`, `:158` 의 "app.py" 문구도. 카테고리 목록 `app.py:361` 은 페이지에 남기거나 `faq.py` 에 함께 둔다 |
| `NOTE`(`app.py:49`) | `services/risk_model.py` `NOTE` | 점수 성격을 설명하는 고정 문구. 참고 저장소는 이런 문구를 업무 모듈 상수로 둔다(`truck_stats.py:21 DATA_NOTE`, `driver_sim.py:31 ASSUMPTION`) | 호출처 `app.py:101,191,287,329` |
| `COLOR_MIN`, `COLOR_MAX`(`app.py:54-56`, 중간값 `scored_values`) | `services/parking_data.py` `score_color_range(frame) -> (min, max)` (상수 → 함수, 이름 변경) | 모듈 상수로 두면 import 순간 전체 자료를 읽어 `sql/build_dump.py` 등 import 만 하는 곳이 무거워진다. 기준은 `service_inventory()` 결과(서비스 지역만)로 지금과 같게 | 호출처 `app.py:60,136,139`. 빈 경우 0·100 기본값 유지 |

### 3.3 목록 밖이지만 `app.py` 에서 함께 나갈 것 (추가 발견)

| 옛 위치 | 새 모듈 | 이유 | 고쳐야 할 import·경로 |
|---|---|---|---|
| `ASSETS`, `LOGO`(`app.py:50-51`) | `services/ui.py` `ASSETS`, `LOGO`, `asset(name)` | 참고 `ui.py:20,495` 와 같은 자산 경로 자리 | `Path(__file__).resolve().parent / "assets"` → `parents[1] / "assets"` |
| 상단 브랜드 바(`app.py:153-156`), 사이드바 로고(`app.py:182-183`), 푸터(`app.py:369-372`) | `services/ui.py` `show_brand()`, `render_footer()` | 모든 페이지 공통. 참고 `ui.py:491 show_logo`, `:523 render_footer`. CSS 없이 지금 위젯 그대로 | 진입점에서 한 번 호출(참고 `app.py:34-39` 처럼 본문 자리 먼저) |
| `SERVICE_AREA`(`app.py:53`) | `services/service_config.py` `SERVICE_AREA` | `SERVICE_DISTRICTS` 에서 바로 나오는 값 | 호출처 `app.py:159,249,330` |
| `risk_band`, `RISK_BANDS` 별칭(`app.py:42-43`) | 삭제, pages 가 `services.parking_marker` 에서 직접 import | 별칭만 하는 줄 | 호출처 `app.py:63,77,137,347,348` |
| `FRAME`(`app.py:52`) | 모듈 없음. 각 페이지가 `service_inventory()` 호출 | 적재 함수 안쪽이 이미 캐시됨(`parking_data.py:12`, `risk_data.py:47`) | — |
| 직접 실행 처리(`app.py:5-29`), 카카오 키(`app.py:47`) | `app.py` 에 남김 | 진입점 책임 | `app.py:28 from launch import main` 은 `launch.py` 위치(scripts 세션 몫)에 따라 바뀐다 |

### 3.4 제안 결과 모양

```text
services/
  __init__.py          docstring 만 (모듈 목록·원칙)
  service_config.py    순수        서비스 구, SERVICE_AREA
  risk_model.py        순수        계산식, NOTE
  parking_marker.py    순수        RISK_BANDS·risk_band·level·COLORS·마커 SVG
  parking_search.py    순수        distance
  map_payload.py       순수        json_records
  faq.py               순수        FAQ
  kakao_navi.py        순수        카카오 길찾기 API
  risk_data.py         자료+캐시   위험 입력 결합
  parking_data.py      자료+캐시   주차장 적재, score_color_range
  parking_view.py      화면 조각   badge, detail
  compare.py           화면 상태   toggle_compare, sync_compare
  parking_map.py       화면 조각   지도·GPS·legend
  kakao_navi_view.py   화면 조각   route_panel (비활성)
  ui.py                화면 조각   로고·브랜드 바·푸터·자산 경로
```

순환 import 확인(제안 기준): `parking_data → risk_data → risk_model`, `parking_data → service_config`, `parking_view → parking_marker, risk_model`, `parking_map → map_payload, parking_marker`, `kakao_navi_view → kakao_navi`. 되돌아오는 화살표 없음.

## 4 깨질 위험과 대비

| 위험 (사실) | 일어나는 일 | 대비 |
|---|---|---|
| `Path(__file__).parent` 3곳: `service_config.py:12`, `parking_data.py:30`, `app.py:50` | 옮기기만 하면 `services/data/...` 를 찾다 실패. `service_config.py:14-21` 은 import 시점에 파일을 읽으므로 앱 전체가 시작 단계에서 멈춘다(크게 드러남) | 이동과 같은 단위에서 `parents[1]` 로 바꾸고 판정 명령 실행 |
| `sql/build_dump.py:105-112` 가 `app.py` 를 `ast` 로 읽어 `FAQ` 를 찾는다 | FAQ 가 나가면 `ValueError`(:112) 로 덤프 생성 실패 | `from services.faq import FAQ` 로 교체. `services/faq.py` 는 streamlit 을 import 하지 않게 |
| `test_gps_location.py:7,43` 는 모듈 객체에 가짜 함수를 꽂는다 | 페이지와 테스트가 서로 다른 이름(`parking_map` 대 `services.parking_map`)으로 import 하면 모듈 객체가 둘이 되어 가짜 함수가 안 먹는다 | 모두 `services.parking_map` 으로만 import. 스크래치패드 시험판(streamlit 1.67.0)에서 `st.navigation` 기본 페이지 + `AppTest.from_file(app.py)` + `mock.patch.object(services 모듈)` + `switch_page` 가 통과함을 확인(1개 테스트, 2026-11-11) |
| `test_gps_location.py:10` `APP = …parent / "app.py"`, `test_risk_inventory.py:16` `…parent / "data"` | 테스트를 `tests/` 등으로 옮기면 경로가 한 단계 어긋남 | 테스트 위치를 바꿀 때만 `parents[1]`. 판정 명령 `python -m unittest test_…` 도 함께 바뀐다 |
| `build_rainfall.py:20` 루트 import, `:22 ROOT = …parent` | scripts 로 옮기면 `services` 를 못 찾고 ROOT 도 어긋남 | 참고 방식 둘 중 하나: `sys.path.insert(0, ROOT)`(`scripts/load_faqs.py:28-29`) 또는 `python -m scripts.build_rainfall`(`scripts/seed_drivers.py:6`) |
| `sql/build_dump.py:18-19` 는 루트를 `sys.path` 에 넣고 `:122,163-165` 에서 루트 모듈 import | import 줄 4개가 실패 | `from services.parking_marker …`, `services.parking_data`, `services.risk_data` 로 교체. ROOT 는 sql/ 에 있는 한 그대로 |
| `prepare.bat:56,58` (Windows 준비) | 이동 뒤 `py_compile parking_marker.py` 와 import 확인이 실패 → Windows 준비 실패. macOS 에서는 드러나지 않는다 | `services\parking_marker.py`, `from services.parking_marker import …` 로 수정 |
| 문서 언급: `README.md:26,33,46`, `UPLOAD_GUIDE.md:24`, `RISK_MODEL.md:3,33` | 실행은 안 깨지지만 문서가 틀린다 | 문서 갱신 단위에 포함 |
| '점수 미산정처리 원인' 세션이 `build_rainfall.py`, `test_risk_inventory.py`, `README.md`, `RISK_MODEL.md`, `sql/skn_1st_4team.sql` 를 고칠 예정 | 이 재배치도 같은 파일의 import 줄을 바꾼다 → 겹쳐 쓰기 | 그 세션이 끝난 뒤 이동하거나, 그 세션에 새 경로를 알려 준다 |
| 데이터 폴더를 `data/raw`·`data/processed` 로 나누면 | `parking_data.py:30-34` 는 폴더 하나(`data_dir`)를 넘기고 `risk_data.py:50,52,62,79` 가 그 안의 4개 파일을 읽는다. `service_config.py:14,20`, `sql/build_dump.py:24,174` 도 `data/` 직접 | 코드 이동과 데이터 이동을 다른 단위로 나눈다. 데이터 이동 때 `attach_risk_data` 인자를 파일별 경로로 바꿀지 결정 필요 |
| 사용처 0건 상수: `DATA_VERSION`(`parking_data.py:9`), `MARKER_VERSION`(`parking_marker.py:6`), `RISK_DATA_VERSION`(`risk_data.py:13`) | 프로젝트 `.py` 전체(`.venv` 제외) grep 기준 정의 외 사용 0건. 이동에는 영향 없음 | 그대로 옮긴다(정리는 이번 범위 밖) |
| `kakao_panel.py:20` 안내 문구가 "app.py 맨 위의 KAKAO_REST_API_KEY" 라고 하지만 실제로는 환경 변수(`app.py:47`) | 비활성 코드라 지금은 영향 없음 | 한 줄 보고. 고칠지는 메인 세션 |

추측(확인 안 함):
- `st.cache_data` 캐시 키에 함수의 모듈 경로가 들어가므로 이동 직후 첫 실행은 캐시를 다시 만든다. 결과는 같고 첫 화면만 느려질 것이다.
- 위젯 키(`parking_query`, `parking_radius`, `location_lat` 등)는 그 위젯이 그려지지 않은 실행에서 정리된다. 지금도 사이드바로 FAQ 화면에 가면 홈 위젯이 그려지지 않으므로, pages 로 나눠도 동작 차이는 없을 것이다. pages 세션이 실제 화면으로 확인할 일.
- `.venv` 의 site-packages 에 `services`·`pages`·`scripts` 라는 최상위 패키지는 없다(확인함). 다른 실행 환경(Windows `.venv`)도 같다고 추측한다.

## 5 메인 세션이 정할 것

| 정할 것 | 추천 | 다른 선택지 | 되돌리기 |
|---|---|---|---|
| 1. GPS 를 `parking_map` 에서 떼어 `services/location.py` 로 | 떼지 않는다(200줄, 참고 모듈 크기 안) | 떼면 `test_gps_location.py:7-8,43` 의 대상이 `services.location` 으로 바뀐다 | 쉬움 |
| 2. 비교함 콜백 위치 | `services/compare.py` | 홈 페이지 파일 안에 둔다(홈에서만 씀) | 쉬움 |
| 3. `distance` 위치 | `services/parking_search.py` 새 모듈 | `services/parking_data.py` 에 함께 | 쉬움 |
| 4. `kakao_panel` 모듈 이름 | `kakao_navi_view` | `kakao_panel` 유지 | 쉬움 |
| 5. FAQ 자료 형태 | `services/faq.py` 의 파이썬 리터럴 + `build_dump` 직접 import | 참고처럼 `data/faq/` 파일로 빼기(ref-data-docs 보고서와 맞춰야 함) | 보통 |
| 6. `services/ui.py` 신설 | 만든다(로고·브랜드 바·푸터·자산 경로, CSS 없음) | 진입점 `app.py` 에 그대로 둔다 | 쉬움 |
| 7. 이동 순서 | '점수 미산정처리 원인' 세션이 끝난 뒤 코드 이동 → 판정 명령 → 데이터 이동은 별도 단위 | 동시에 진행하고 그 세션에 새 경로 통보 | 겹쳐 쓰기는 되돌리기 어려움(아직 git 없음) |
| 8. 테스트 위치 | 루트 유지(판정 명령 그대로) | `tests/` 로 이동 시 경로 2곳과 판정 명령 변경 | 쉬움 |

이 보고서가 틀렸다는 신호: 이동 뒤 판정 명령 `.venv/bin/python -m unittest test_risk_model test_parking_marker test_map_payload test_risk_inventory test_gps_location test_build_rainfall` 에서 `ModuleNotFoundError` 나 `FileNotFoundError` 가 위 표에 없는 줄에서 나오면 대응표가 빠뜨린 곳이다.
