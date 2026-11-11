# 참고 분석: data · docs · assets · 루트 설정 파일

- 참고 저장소: `SKNETWORKS-FAMILY-AICAMP/SKN38-1st-1Team` main, 커밋 `61ef27d0d879` (2026-11-11 08:56 +0900), `--depth 1` 로 받음. 코드는 실행하지 않고 읽기만 했다.
- 우리 쪽 근거: 2026-11-11 09:20 경 이 폴더(`newgit`)의 파일을 직접 읽고 grep 한 결과. git 저장소가 아니므로 줄 번호는 그 시각 기준이다.
- 표기: `ref:` 로 시작하는 경로는 참고 저장소, 그 밖은 우리 프로젝트.

## 한 줄 결론

데이터 파일을 `data/raw`·`data/processed` 로 나누는 것 자체는 할 만하지만, 지금 우리 코드는 "데이터 파일은 모두 한 폴더에 있다"는 가정을 세 군데(`parking_data.py:32-34`, `risk_data.py:50-79`, `test_risk_inventory.py:16-23`)에 박아 두었고, 같은 파일들을 '점수 미산정처리 원인' 세션이 곧 고친다. 그래서 **경로 상수를 한 모듈로 모으는 일을 먼저 하고, 폴더 이동은 강수 작업(rainfall-all-districts)이 끝난 뒤 한 번에** 하기를 권한다.

---

## 1 참고 저장소 사실

### 1.1 data/ 의 세 폴더와 읽고 쓰는 코드

| 폴더 | 들어 있는 것 | 쓰는 코드 (파일:줄) | 읽는 코드 (파일:줄) |
|---|---|---|---|
| `ref:data/raw/` | `molit_registration_sido_202609.json`, `.gitkeep`(0바이트) | `ref:scripts/preprocess_registration.py:28,124,126` — API 응답 `rows` 를 그대로 JSON 으로 저장 | `ref:scripts/update_registration_db.py:383,386` — 저장한 원본 파일 이름만 DB 출처 행에 기록 |
| `ref:data/processed/` | `truck_business_by_sigungu_202609.csv`, `jimni_faq.json`, `driver_places.csv`, `sigungu_coordinates.csv`, `sido_bubble_points.csv`, `화물차_시군구별_등록현황_202609.xlsx`, `.gitkeep` | `ref:scripts/preprocess_registration.py:29,125,127` (CSV), `ref:scripts/load_faqs.py:32,177` (FAQ JSON), `ref:scripts/collect_driver_places.py:32` (장소 좌표) | `ref:services/truck_map.py:21`, `ref:services/faq.py:17`, `ref:services/driver_sim.py:26`, `ref:scripts/load_registration_csv.py:11`, `ref:scripts/seed_drivers.py:27-28`, `ref:scripts/seed_drivers_excel.py:44`, `ref:scripts/collect_driver_places.py:33` |
| `ref:data/faq/` | `jimni_faq.md` (팀이 손으로 쓴 FAQ 원문) | 없음 (사람이 편집) | `ref:scripts/load_faqs.py:31` 가 읽어 `processed/jimni_faq.json` 을 만든다 (`ref:scripts/load_faqs.py:3-4` 주석) |

사실로 확인한 구분 기준과 예외:

- 기준(코드로 확인): **외부 API 응답 그대로 = raw, 우리 스크립트가 만든 결과 = processed, 사람이 쓴 원문 = faq**. `ref:scripts/preprocess_registration.py:122-128` 의 `save_outputs` 한 함수가 같은 수집에서 raw JSON 과 processed CSV 를 나란히 쓴다.
- 예외 1: 통계누리에서 사람이 내려받은 엑셀 `화물차_시군구별_등록현황_202609.xlsx` 는 원본인데 processed 에 있다. 읽는 쪽 주석이 스스로 "원본 … 파일은 수정하지 않음" 이라고 적는다 (`ref:services/driver_sim.py:4`). 기준이 일관되지 않다.
- 예외 2: `sigungu_coordinates.csv` 는 카카오 재호출을 막는 캐시인데 processed 에 있다 (`ref:scripts/seed_drivers.py:27` 주석 "시군구 좌표 캐시").
- 예외 3: 크롤링한 타사 FAQ `sendy_FAQ`(확장자 없는 JSON)는 data 밖 루트에 있고 어떤 코드도 읽지 않는다 (`ref:scripts/load_faqs.py:3` "sendy_FAQ는 사용하지 않음").
- 경로 쓰는 방식: 대부분 `Path(__file__).resolve().parents[1] / "data" / "processed" / 이름` 으로 파일마다 직접 조립한다 (`ref:services/truck_map.py:21`, `ref:services/faq.py:17`, `ref:services/driver_sim.py:26`). 공용 경로 모듈은 없다. 일부 스크립트는 현재 폴더 기준 상대 문자열을 쓴다 (`ref:scripts/load_registration_csv.py:11`, `ref:scripts/seed_drivers.py:27`) — 프로젝트 루트에서 실행해야만 동작한다.

### 1.2 `.gitkeep`

- `ref:data/raw/.gitkeep`, `ref:data/processed/.gitkeep`, `ref:docs/.gitkeep`, `ref:scripts/.gitkeep`, `ref:sql/.gitkeep` 이 모두 0바이트로 있다. 다섯 폴더 모두 이미 다른 파일이 들어 있어 `.gitkeep` 은 실제로 필요 없는 상태다(처음 폴더 뼈대를 만들 때 남은 것으로 보인다 — 추측).
- `ref:data/faq/` 에는 `.gitkeep` 이 없다.
- `.gitignore` 는 `data/raw/*.zip` 만 제외한다 (`ref:.gitignore:31-32`, 주석 "GitHub 100MB 제한"). raw JSON 자체는 커밋한다.

### 1.3 docs/ 에 두는 문서 종류

| 종류 | 파일 | 근거 |
|---|---|---|
| 주제별 설명 문서(Markdown) | `fare_table.md`(운임 기준표), `registration_pipeline.md`(수집 파이프라인: 파일 역할표 → API 확인 → 실행 방법 → 스케줄러 → 화면 사용 → 좌표) | `ref:docs/fare_table.md:1`, `ref:docs/registration_pipeline.md:1-16,90,107` |
| ERD 그림 | `erd_final_1team.png`, `erd_original.png` | `ref:README.md:159,163` 에서 링크 |
| 서비스 흐름도 | `serviceflow.png` | `ref:README.md:90` |
| README 전용 그림 | `readme_1.png`, `readme_2.png` | `ref:README.md:61`. `ref:assets/` 에도 같은 파일이 있다(md5 동일: `ef2f9309…`, `e2d278c7…`) — 중복 |

- README 가 가리키지만 저장소에 **없는** 파일: `docs/readme_market.svg`(`ref:README.md:30`), `docs/readme_problem.svg`(`ref:README.md:34`), `docs/screens/01_request.png`~`06_rating.png`(`ref:README.md:77-82`). 깨진 링크다.
- README 는 긴 설명을 docs 로 넘기고 링크만 둔다: `[운임 기준표 자세히 보기](docs/fare_table.md)` (`ref:README.md:101`), `[데이터 파이프라인 문서](docs/registration_pipeline.md)` (`ref:README.md:150`).

### 1.4 assets/ 이미지 이름 규칙

- 모두 소문자 + 밑줄(snake_case): `logo_main.png`, `logo_white.png`, `driver_marker.png`, `jimni_main.jpg`.
- 같은 종류 변형은 숫자 접미사: `jimni1.png`~`jimni6.png`, `logo1.png`~`logo4.png`.
- 용도 접미사: `_main`, `_white`, `_marker`.
- 예외: `sub2.png.jpg`(확장자 이중) — `ref:pages/0_Home.py:21` 이 그 이름 그대로 읽는다.
- 코드는 `assets` 경로를 한 곳에서 만든다: `ref:services/ui.py:20` `ASSETS = Path(__file__).resolve().parents[1] / "assets"` 후 `asset(name)` 등 도우미로 이름만 넘긴다 (`ref:services/ui.py:467,476,482,496`, `ref:app.py:13`). 예외로 `ref:services/driver_map.py:127` 은 직접 조립.

### 1.5 루트 설정 파일

| 파일 | 내용 (파일:줄) |
|---|---|
| `ref:.env.example` | 맨 위 두 줄에 "복사해 .env 를 만들고 실제 값 입력, .env 는 GitHub 에 안 올라감" 안내 (`:1-2`). 키 이름만 두고 값은 비움: `MOLIT_API_KEY=`(`:5`), `KAKAO_REST_API_KEY=`(`:11`), `KAKAO_JAVASCRIPT_KEY=`(`:13`), `DB_USER=`·`DB_PASSWORD=`·`DB_NAME=`(`:18-20`). 비밀이 아닌 기본값만 채움: `DB_HOST=localhost`(`:16`), `DB_PORT=3306`(`:17`), API URL(`:7`). 키마다 발급처·용도 주석 한 줄. |
| `.env` 를 읽는 코드 | `python-dotenv` 의 `load_dotenv(ROOT / ".env")`: `ref:services/db.py:22`, `ref:services/kakao_local.py:28`, `ref:scripts/molit_api.py:30`, `ref:scripts/update_registration_db.py:46`. 의존성 `python-dotenv==1.2.4` (`ref:requirements.txt:3`). |
| `ref:.gitignore` | 주석으로 묶은 6개 절: 가상환경(`:1-4`), 환경변수·인증정보(`:6-12`, `.env`·`.env.*` 제외하되 `!.env.example` 로 예시는 포함, `secrets.toml`, `*.pem`, `*.key`), Python 캐시(`:14-18`), IDE·OS(`:20-25`), 로그·임시(`:27-29`), 대용량 원본(`:31-32`). |
| `ref:.streamlit/config.toml` | 맨 위 주석 "색상·글꼴·크기·모서리는 이 파일 한곳에서 관리" (`:1-2`). `[theme]` 에 색 10개·글꼴(CDN)·글자 크기·모서리·차트 색(`:4-29`), `[client] toolbarMode = "minimal"` (`:31-32`). 값마다 행 끝 주석으로 용도. |
| `ref:requirements.txt` | 정확한 버전 고정 `==` (`:1-5,7`), 버전 없는 `certifi`(`:6`). 패키지마다 행 끝 주석으로 용도(`:6-7`). "추후 필요 시 주석 해제" 절(`:9-10`). |
| `ref:README.md` 목차 | 로고·한 줄 소개(`:1-14`) → Demo(`:18`) → Market & Problem / Target Users(`:25,37`) → Why(`:48`) → How It Works(`:58`) → Fare Guide(`:97`) → Key Features(`:105`) → Tech Stack(`:120`) → Data Collection & Processing(`:137`) → Database Design & ERD(`:154`) → Project Structure(`:169`) → Meet the Team(`:226`). 실행 방법·설치 절이 없다. |
| README '폴더 구조' 설명 방식 | `<details><summary>폴더 구조 자세히 보기</summary>` 로 접어 둔다(`:171-172,220`). `text` 코드 블록 안에 `├──`·`└──` 트리, 최상위 이름 뒤 `#` 주석 한 마디(`:176-217`). `pages/`·`services/` 는 파일까지 펼치고, `scripts/`·`data/`·`sql/`·`docs/`·`assets/` 는 폴더 한 줄 설명만 둔다(`:208-212`). 숨김 설정 파일도 트리에 넣는다(`:213-216`). |

---

## 2 따라야 할 규칙

참고 저장소에서 가져올 것과, 참고 저장소의 불일치를 고쳐서 가져올 것을 나눈다.

1. **데이터 분류 기준 (참고 저장소 기준을 일관되게 적용한 형태)**
   - `data/raw/`: 이 저장소의 코드가 만들지 않은 입력. 받은 그대로 두고 코드가 고치지 않는다. 참고 저장소의 예외 1(원본 엑셀을 processed 에 둠)은 따르지 않는다.
   - `data/processed/`: 이 저장소의 스크립트가 raw 에서 만든 결과. 만드는 스크립트 이름을 문서에 적는다.
   - 설정(가중치·정규화 방식 같은 규칙 값)은 raw 도 processed 도 아니다. `data/` 바로 아래에 둔다(참고 저장소에는 설정 파일이 없어 근거가 없다 — 우리 쪽 결정).
   - `data/faq/` 는 FAQ 원문을 파일로 뺄 때만 만든다. 지금 우리 FAQ 는 `app.py:65` 의 파이썬 목록이다.
2. **경로는 한 모듈에서 만든다.** 참고 저장소는 파일마다 조립하지만(1.1), 우리는 데이터 폴더를 나누면 같은 경로가 10곳 넘게 바뀌므로 `ref:services/ui.py:20` 의 `ASSETS` 상수 방식을 데이터에도 확장한다. 루트 기준은 `Path(__file__).resolve()` 로 잡고, 현재 폴더 기준 상대 문자열(`ref:scripts/seed_drivers.py:27` 방식)은 쓰지 않는다.
3. **`.gitkeep` 은 빈 폴더에만** 둔다. 파일이 생기면 지운다. 우리 쪽에서는 `data/raw/kma_hourly/` 가 내려받기 전까지 비어 있으므로 여기에만 해당한다.
4. **문서는 README 에 요약과 링크, 긴 설명은 `docs/`** (`ref:README.md:101,150`). 문서 이름은 소문자 snake_case `.md` (`fare_table.md`, `registration_pipeline.md`).
5. **이미지 이름은 소문자 snake_case**, 변형은 숫자 접미사, 용도는 `_main`·`_white`·`_marker` 접미사. 이중 확장자 금지.
6. **README '폴더 구조'** 는 `<details>` 로 접고, `text` 트리 + 최상위마다 한 마디 주석. README 에 링크한 파일은 실제로 있어야 한다(참고 저장소의 깨진 링크 1.3 은 따르지 않는다).
7. **`.gitignore` 는 주석 달린 절로 묶고**, `.env` 를 제외하면서 `!.env.example` 로 예시는 포함한다.
8. **`requirements.txt` 는 패키지마다 용도 주석.** 버전을 `==` 로 고정할지는 우리 쪽 결정이다(5절).

---

## 3 우리 파일 대응표

"그 경로를 읽는 코드" 칸은 2026-11-11 grep 결과다(`.venv/`, `__pycache__/`, `sql/skn_1st_4team.sql` 의 데이터 행 제외). `sql/skn_1st_4team.sql` 안에는 데이터 파일 경로가 한 줄도 없음을 확인했다(`seoul_parking`·`flood_depth`·`rainfall.csv`·`data/` 검색 0건) — 덤프는 이동 영향이 없다.

### 3.1 데이터

| 옛 경로 | 새 경로 | 분류·이유 | 그 경로를 읽는 코드 파일:줄 |
|---|---|---|---|
| `data/seoul_parking.csv` | `data/raw/seoul_parking.csv` | **raw**. 이 저장소에 만드는 코드가 없다. RISK_MODEL 이 "제공된 주차장 목록" 이라 부른다(`RISK_MODEL.md:3`). 열 이름 `주차장관리번호(수정)` 으로 보아 팀이 저장소 밖에서 손본 파일이다(추측) — 그래도 이 저장소 기준으로는 입력이다. | `parking_data.py:30` (경로 조립), `parking_data.py:33-34` (같은 폴더에서 나머지 원본을 찾음), `service_config.py:12,14` (`DATA` 상수), `risk_audit.json` 의 `source_sha256` 키 `"seoul_parking.csv"` → `test_risk_inventory.py:16,21-23` 이 `data/` + 이 이름으로 해시 비교 |
| `data/flood_depth.xlsx` | `data/raw/flood_depth.xlsx` | **raw**. 받은 엑셀을 수식 실행 없이 읽기만 한다(`risk_data.py:16-17` "supplied single-sheet XLSX"). | `parking_data.py:32` (원본 목록), `risk_data.py:79` (`base / "flood_depth.xlsx"`), `sql/build_dump.py:24,174` (`DATA / "flood_depth.xlsx"`), `sql/build_dump.py:5` (설명 주석), `risk_audit.json` 해시 키 → `test_risk_inventory.py:21-23` |
| `data/lowland.csv` | `data/raw/lowland.csv` | **raw**(외부 가공물). 열 이름이 "저지대상대점수_잠정(0~100)" 인 계산 결과지만, 만드는 코드가 이 저장소에 없다. 그래서 이 저장소 기준 입력으로 분류한다. 만든 방법은 문서에 출처로 적을 것. | `parking_data.py:32`, `risk_data.py:52` (`base / "lowland.csv"`), `risk_audit.json` 해시 키 → `test_risk_inventory.py:21-23` |
| `data/rainfall.csv` | `data/processed/rainfall.csv` | **processed**. `build_rainfall.py` 가 `data/kma_hourly/` 에서 다시 만드는 결과다(`build_rainfall.py:1,140,162-165`). 단 지금 5개 구 행은 시간자료 없이 받은 연간 집계값이다(`RISK_MODEL.md:29`) — 강수 작업이 끝나 24개 구를 다시 만든 뒤에야 온전히 processed 가 된다. | `parking_data.py:32`, `risk_data.py:62`, `service_config.py:5` (주석), `service_config.py:20`, `build_rainfall.py:1,6,140` (기본 출력), `build_rainfall.py:115-125` (덮어쓰기 전 기존 행 재현 확인 — `--output` 경로를 그대로 읽음), `sql/build_dump.py:5,179`, `README.md:52`, `TASKS.md:13,21,35`, `risk_audit.json` 해시 키 → `test_risk_inventory.py:21-23`. `test_build_rainfall.py:48` 은 임시 폴더의 같은 이름이라 영향 없음 |
| `data/kma_hourly/` (아직 없음) | `data/raw/kma_hourly/` | **raw**. 기상자료개방포털에서 사람이 내려받는 시간 강수 CSV(`build_rainfall.py:4`). 내려받기 전까지 빈 폴더이므로 `.gitkeep` 을 둔다. | `build_rainfall.py:4` (설명), `build_rainfall.py:139,145,148` (기본 입력·안내 문구), `README.md:52`, `TASKS.md:13,21` (사용자 내려받기 안내 — **사용자가 이 경로에 파일을 둘 예정**) |
| `data/risk_config.json` | `data/risk_config.json` (그대로) | **설정**. 거리 방식·정규화 방식 같은 규칙 값 5개(`data/risk_config.json`). raw·processed 어느 쪽도 아니다. | `parking_data.py:32`, `risk_data.py:50` (`base / "risk_config.json"`), `RISK_MODEL.md:25`, `risk_audit.json` 에는 해시 키 없음 |
| `data/risk_audit.json` | 테스트 폴더가 생기면 `tests/fixtures/risk_audit.json`, 아니면 `data/risk_audit.json` (그대로) | **검증 기준값**(앱 입력 아님). 원본 해시·총계·표본 7개 점수를 담아 테스트만 읽는다(`RISK_MODEL.md:33`). 독립 계산으로 손으로 만든 값이라 processed(스크립트 산출물)도 아니다. 위치는 테스트 폴더 결정(ref-scripts-sql 범위)에 따라간다. | `test_risk_inventory.py:16-17` (`data/` + 이름), `RISK_MODEL.md:33`, `TASKS.md:13,21`. 이 파일 **안의** `source_sha256` 키 4개가 맨 파일 이름이라 원본이 raw/processed 로 갈리면 키를 `raw/seoul_parking.csv` 처럼 `data/` 기준 상대 경로로 바꿔야 한다(`test_risk_inventory.py:21-23`) |

### 3.2 이미지

| 옛 경로 | 새 경로 | 분류·이유 | 그 경로를 읽는 코드 파일:줄 |
|---|---|---|---|
| `assets/chimchak-logo.png` | `assets/logo_main.png` | 앱 로고. 규칙 5(snake_case, `_main` 접미사, `ref:assets/logo_main.png` 와 같은 이름). 1806×871 PNG. | `app.py:50-51` (`ASSETS / "chimchak-logo.png"`), `README.md:26` |
| `assets/blue-car-marker.png` | `assets/car_marker.png` | 마커 그림을 점수 50 상태로 내보낸 참고 이미지. **어떤 코드도 읽지 않는다** — 실제 마커는 `parking_marker.py` 가 SVG 로 만든다(`UPLOAD_GUIDE.md:25`). 규칙 5에 맞춰 이름만 바꾼다. 쓰이지 않으므로 `docs/` 로 옮기는 안도 있다(5절). | 코드 없음. `UPLOAD_GUIDE.md:25` 만 언급 |

### 3.3 문서

| 옛 경로 | 새 경로 | 분류·이유 | 그 경로를 읽는 코드 파일:줄 |
|---|---|---|---|
| `README.md` | `README.md` (그대로, 내용 개편) | 루트 소개 문서. 실행·테스트 절은 유지하고(참고 README 에 없지만 우리 사용자에게 필요), '폴더 구조' 절을 부록 초안으로 추가. `README.md:33` 의 "`risk_model.py`, `risk_data.py`, `parking_data.py`" 와 `:26`·`:46`·`:52` 의 경로는 이동 후 고쳐야 한다. | 코드가 읽지 않음. 경로를 적은 줄: `README.md:26,33,44,46,52,58` |
| `RISK_MODEL.md` | `docs/risk_model.md` | 주제별 설명 문서 → 규칙 4(`ref:docs/fare_table.md` 와 같은 종류). README 에서 링크한다. | 코드 없음. `TASKS.md:13` 만 언급(강수 작업이 고칠 파일 목록). 문서 안 경로: `RISK_MODEL.md:25` (`data/risk_config.json`), `:33` (`data/risk_audit.json`, 테스트 명령) |
| `UPLOAD_GUIDE.md` | `docs/upload_guide.md` | 팀 공동작업 안내 → 규칙 4. 단 **내용이 현재 파일과 어긋난다**: 없는 `.streamlit/secrets.example.toml`(`:8,17`)과 없는 `assets/design.css`(`:23`)를 가리킨다. 옮길 때 사실에 맞게 고친다. | 코드 없음 |
| (없음) | `docs/restructure/*.md` | 이번 구조 정리 보고서 4개. 정리가 끝나면 지울지 남길지 메인 세션이 정한다. | — |

### 3.4 루트 설정 파일

| 옛 경로 | 새 경로 | 분류·이유 | 그 경로를 읽는 코드 파일:줄 |
|---|---|---|---|
| `.gitignore` | `.gitignore` (그대로, 내용 보강) | 지금 8줄(`.gitignore:1-8`). 규칙 7에 맞춰 주석 절로 묶고 다음을 더한다: `.env.*` + `!.env.example`(예시를 둘 경우), `*.log`, `.pytest_cache/`, `.vscode/`·`.idea/`, `Thumbs.db`. `.python/`·`.uv-cache/` 는 `prepare.bat:5-6` 이 만드는 폴더라 유지. | git 이 읽음. `UPLOAD_GUIDE.md:26` 이 목록을 다시 적고 있어 함께 고친다 |
| `.streamlit/config.toml` | `.streamlit/config.toml` (그대로, 주석만 보강) | 테마 5줄(`.streamlit/config.toml:1-6`). 맨 위에 "색상은 이 파일 한곳에서 관리" 주석과 값별 용도 주석을 단다(`ref:.streamlit/config.toml:1-2`). 마지막 줄 끝에 줄바꿈이 없다(`cat` 출력에서 확인). 값 변경은 이번 범위 밖. | Streamlit 이 실행 폴더 기준으로 읽음. `README.md:44` |
| `requirements.txt` | `requirements.txt` (그대로, 주석 보강) | 범위 지정 5개(`requirements.txt:1-5`). 패키지마다 용도 주석을 단다(`streamlit-js-eval` = GPS 위치 등). `==` 고정 여부는 5절. | `prepare.bat:39,43,52`, `README.md:13` |
| (없음) | `.env.example` — **지금은 만들지 않기를 권함** | 이유(사실): 우리 코드는 `.env` 파일을 읽지 않는다. 키는 `os.environ.get("KAKAO_REST_API_KEY")` 로만 읽고(`app.py:47`), `python-dotenv`·`st.secrets` 사용이 0건이며 `requirements.txt` 에도 없다. 카카오 길찾기는 비활성이다(`README.md:46`). 이 상태에서 `.env.example` 을 두면 "`.env` 에 적으면 된다"는 잘못된 안내가 된다. 만들려면 `python-dotenv` 의존성 추가가 함께 필요하다(5절). | `app.py:47` (환경 변수), `kakao_panel.py:20` (안내 문구가 "app.py 맨 위의 KAKAO_REST_API_KEY에 키를 입력" 이라 **현재 코드와 어긋남**) |
| `실행.bat`, `prepare.bat` | 루트 그대로 (권함) | Windows 사용자가 더블클릭하는 진입점이고 `app.py:25` 가 `실행.bat` 을 이름으로 부른다. 위치 판단은 ref-scripts-sql 범위. 데이터 이동과의 관계만 적는다: `prepare.bat:56,58` 이 `app.py`·`parking_marker.py` 를 이름으로 검사하므로 그 파일들이 `services/` 로 가면 함께 고쳐야 한다. | `app.py:25`, `README.md:17`, `UPLOAD_GUIDE.md:15` |
| `TASKS.md` | 루트 그대로 | 작업 인계 파일. 세션 도구가 이 경로를 정본으로 쓴다. 저장소 구조 정리 대상이 아니다. | 세션 도구 |

---

## 4 깨질 위험과 대비

### 사실 (코드로 확인)

| 위험 | 근거 | 깨지는 모습 | 대비 |
|---|---|---|---|
| 원본 네 개가 한 폴더에 있다는 가정 | `parking_data.py:32-34` 가 `seoul_parking.csv` 의 부모 폴더에서 나머지 원본 3개와 설정을 찾고, `risk_data.py:48-79` 의 `attach_risk_data(parking, data_dir, …)` 가 폴더 하나(`base`)에서 4개를 읽는다. | raw/processed 로 나누는 순간 `FileNotFoundError` 로 앱 첫 화면부터 멈춘다(`app.py:52` `service_inventory()` 가 모듈 적재 때 실행). | `data_dir` 하나 대신 파일별 경로를 넘기도록 함수 모양을 바꾸고, 경로 상수를 한 모듈(예: `services/data_paths.py` 의 `RAW`, `PROCESSED`, `PARKING_CSV`, `FLOOD_XLSX`, `LOWLAND_CSV`, `RAINFALL_CSV`, `RISK_CONFIG`, `KMA_HOURLY_DIR`)에 모은다. 이동은 그 다음 한 번에. |
| 캐시 무효화 키도 같은 가정 | `parking_data.py:33` 이 `path.parent / name` 의 수정 시각으로 `st.cache_data` 키를 만든다. | 경로만 고치고 이 줄을 빠뜨리면 예외가 나거나, 다른 파일의 시각을 보아 고친 데이터가 화면에 늦게 반영된다. | 위 상수 모듈의 경로 목록으로 시각을 계산하게 한 곳에서 바꾼다. |
| 해시 키가 맨 파일 이름 | `test_risk_inventory.py:21-23` 이 `data/` + `source_sha256` 키로 파일을 연다. | 이동 뒤 테스트 `test_source_snapshot_and_coverage` 가 `FileNotFoundError` 로 실패. | `risk_audit.json` 키를 `raw/seoul_parking.csv`·`processed/rainfall.csv` 식으로 바꾸고 테스트 `base` 를 상수 모듈에서 가져온다. 해시 값 자체는 파일 내용이 같으므로 그대로다. |
| 모듈 적재 때 파일을 연다 | `service_config.py:14,20` 이 import 되는 순간 CSV 두 개를 연다. | 경로가 틀리면 `app.py`·`parking_data.py`·`sql/build_dump.py`·테스트 4개가 import 단계에서 모두 실패한다. 실패 위치가 파일 읽는 곳이 아니라 import 줄로 보여 원인 찾기가 늦다. | 경로 상수 모듈을 쓰도록 바꾸는 첫 커밋에서 판정 명령을 바로 돌린다. |
| 다른 세션과 같은 파일을 고친다 | `TASKS.md:13` — '점수 미산정처리 원인' 세션이 `build_rainfall.py`, `data/rainfall.csv`, `data/risk_audit.json`, `test_risk_inventory.py`, `README.md`, `RISK_MODEL.md`, `sql/skn_1st_4team.sql` 을 고칠 예정. | 이동을 먼저 하면 그 세션의 경로(`data/kma_hourly/`, `data/rainfall.csv`)가 사라지고, 같은 파일을 두 세션이 고쳐 한쪽 변경이 덮인다. | 데이터 이동은 rainfall-all-districts 가 끝나고(커밋된 뒤) 한다. 그 전에 할 수 있는 일은 경로 상수 모듈 도입뿐인데, 이것도 `build_rainfall.py`·`test_risk_inventory.py` 를 건드리므로 같은 이유로 뒤로 미루는 편이 안전하다. |
| 사용자가 내려받을 위치 | `TASKS.md:21`, `README.md:52`, `build_rainfall.py:148` 이 모두 `data/kma_hourly/` 를 안내한다. 사용자 단계(기상청 로그인 후 내려받기)가 대기 중이다. | 내려받기 전에 폴더 이름을 바꾸면 사용자가 옛 위치에 파일을 두고, `build_rainfall.py` 는 "CSV 가 없습니다" 로 끝난다(`build_rainfall.py:147-149`, 종료 코드 2). | 내려받은 뒤에 `data/raw/kma_hourly/` 로 옮기거나, 이동 시점에 `build_rainfall.py` 안내 문구·`TASKS.md`·`README.md` 를 같은 커밋에서 바꾼다. |
| `sql/build_dump.py` 의 별도 경로 | `sql/build_dump.py:18,24` 가 자기 위치 기준으로 `ROOT / "data"` 를 따로 만든다. | 상수 모듈을 거치지 않으면 덤프만 옛 경로를 읽다 실패. | 상수 모듈 import 로 바꾼다. 덤프 결과(`sql/skn_1st_4team.sql`)는 경로를 담지 않으므로 다시 만들 필요 없음(덤프 머리 40줄과 끝에 생성 시각 줄이 없음을 확인 — 같은 데이터면 같은 내용으로 다시 나올 것으로 본다. 실제 재생성 비교는 하지 않았다). |
| 로고 이름 변경 | `app.py:51` 만 읽는다. | 빠뜨리면 로고 자리에서 Streamlit 이미지 오류. | 이름 변경과 `app.py`(또는 페이지 분해 후 그 파일) 수정을 한 커밋에. |

### 추측 (확인하지 않음)

- `seoul_parking.csv`·`lowland.csv` 는 팀이 저장소 밖에서 가공한 것으로 보인다. 원래 출처(서울 열린데이터광장 등)와 가공 방법은 이 폴더 안에서 확인할 근거가 없다. raw 분류는 "이 저장소에서 만들지 않음" 기준이다.
- 기상청 시간자료 CSV 24개 지점×1년 크기는 지점당 수백 KB 수준으로 보여(8,760행) GitHub 100MB 제한에 걸리지 않을 것이다. 내려받은 뒤 `du -sh` 로 확인 필요.

### 대안 (폴더를 나누지 않는 경우)

데이터 파일은 7개(곧 폴더 하나 추가)뿐이라 나눠서 얻는 것은 "원본과 결과물이 눈으로 구분된다" 하나다. 잃는 위험은 위 표의 여덟 줄이다. 나누지 않는다면 같은 효과를 이렇게 낼 수 있다.

- `data/` 는 평평하게 두고, `data/README.md` 한 장에 파일별 분류(raw/processed/설정/검증)·출처·만드는 스크립트를 표로 적는다.
- `kma_hourly/` 만 하위 폴더로 둔다(이미 그렇게 설계됨).
- 경로 상수 모듈은 나누든 안 나누든 도입한다 — 나중에 나눌 때 바꿀 곳이 한 곳이 된다.

권하는 순서: ① 강수 작업 완료·커밋 → ② 경로 상수 모듈 도입(동작 변화 없음, 판정 명령 통과 확인) → ③ 그 다음에 raw/processed 로 나눌지 결정·이동. ②까지만 해도 위험의 대부분이 사라진다.

---

## 5 메인 세션이 정할 것

| 정할 것 | 선택지 | 권하는 안 | 되돌리기 |
|---|---|---|---|
| 데이터 폴더를 나눌지 | (가) `data/raw`·`data/processed` 로 나눔 / (나) 평평하게 두고 `data/README.md` 로 분류 표기 | (가) — 사용자가 참고 저장소 구조를 원했다. 단 4절 순서 ①→②→③ 을 지킨다 | 쉬움(파일 이동과 상수 모듈 한 곳) |
| 데이터 이동 시점 | 강수 작업 전 / 후 | **후** (4절 다섯째·여섯째 줄) | — |
| 경로 상수 모듈 위치 | `services/data_paths.py` / `service_config.py` 확장 | ref-services 보고서의 `services/` 경계에 맞춰 결정. `service_config.py` 가 이미 `DATA` 를 가지므로(`service_config.py:12`) 그 파일을 `services/` 로 옮기며 넓히는 것도 자연스럽다 | 쉬움 |
| `risk_audit.json` 위치 | `tests/fixtures/` / `data/` 유지 | ref-scripts-sql 의 테스트 폴더 결정을 따름 | 쉬움 |
| `risk_config.json` 위치 | `data/` 바로 아래 / `config/` 새 폴더 | `data/` 유지 (참고 저장소에 `config/` 가 없다) | 쉬움 |
| `.env.example` | (가) 만들지 않음 / (나) `KAKAO_REST_API_KEY=` 한 줄로 만들고 `python-dotenv` 를 의존성에 추가해 실제로 읽게 함 | (가) — 카카오 길찾기가 비활성이고 키 없이 앱이 돈다(`README.md:18`). 길찾기를 다시 켤 때 (나)로. (나)는 의존성 추가라 사용자 승인 필요 | 쉬움 |
| `requirements.txt` 버전 고정 | 범위 유지 / `==` 고정 | 범위 유지 — `prepare.bat` 이 Windows 에서 새로 설치하므로 범위가 설치 실패에 덜 민감하다(추측). 현재 설치본은 streamlit 1.67.0, pandas 2.3.3(`.venv` 확인) | 쉬움 |
| `assets/blue-car-marker.png` | `assets/car_marker.png` 로 이름만 변경 / `docs/` 로 이동 / 삭제 | 이름만 변경 — 삭제는 사용자 확인 필요 | 쉬움(삭제는 아님) |
| FAQ 를 `data/faq/` 로 뺄지 | 지금처럼 `app.py:65` 의 목록 / `data/faq/chimchak_faq.md` 원문 + 읽는 코드 | ref-pages·ref-services 결정에 맡김. 뺀다면 `sql/build_dump.py:107-112` 가 `app.py` 를 `ast` 로 파싱해 FAQ 를 찾으므로 함께 고쳐야 한다 | 중간 |
| `docs/restructure/` 보고서 | 정리 후 삭제 / `docs/` 에 남김 | 정리 끝난 뒤 사용자에게 묻기 | — |

발견한 어긋남(조사하지 않고 한 줄씩만 적음):

- `UPLOAD_GUIDE.md:8,17` — 없는 `.streamlit/secrets.example.toml` 을 안내. `UPLOAD_GUIDE.md:23` — 없는 `assets/design.css` 를 안내. 선택지: 이동할 때 사실대로 고침 / 지움.
- `kakao_panel.py:20` — "app.py 맨 위의 KAKAO_REST_API_KEY에 키를 입력하세요" 문구가 환경 변수로 읽는 현재 코드(`app.py:47`)와 다름. 선택지: 문구를 "환경 변수 `KAKAO_REST_API_KEY`" 로 고침(ref-services 범위).

---

## 부록 README '폴더 구조' 절 초안

데이터를 나눈 뒤(5절 (가)) 기준이다. `pages/`·`services/` 의 파일 목록은 ref-pages·ref-services 의 대응표가 확정되면 채운다 — 아래 해당 줄은 자리만 잡아 두었다.

````markdown
## 폴더 구조

<details>
<summary><b>폴더 구조 자세히 보기</b></summary>

```text
newgit/
├── app.py                  # Streamlit 진입점
├── pages/                  # 화면 (홈 · FAQ · 분석 데이터 결과)
├── services/               # 위험점수 계산 · 데이터 적재 · 지도 마커 · 경로 상수
├── scripts/                # 일괄 작업 (강수 집계, SQL 덤프 생성)
├── tests/                  # unittest 테스트와 검증 기준값
├── data/
│   ├── raw/                # 받은 그대로 두는 원본 (코드가 고치지 않음)
│   │   ├── seoul_parking.csv     # 서울시 주차장 806개 목록
│   │   ├── flood_depth.xlsx      # 침수 대표좌표 1,132개와 침수심
│   │   ├── lowland.csv           # 주차장별 저지대 상대점수(0~100)
│   │   └── kma_hourly/           # 기상청 2025 시간 강수량 CSV (직접 내려받기)
│   ├── processed/          # 스크립트가 raw 에서 만든 결과
│   │   └── rainfall.csv          # 자치구별 강수 지표 (scripts 의 강수 집계가 생성)
│   └── risk_config.json    # 점수 계산 설정 (거리 방식 · 정규화 방식)
├── sql/                    # MySQL 덤프와 조회 쿼리
├── docs/                   # 위험점수 설명 · 공동작업 안내
│   ├── risk_model.md
│   └── upload_guide.md
├── assets/                 # 로고 · 마커 이미지
├── .streamlit/             # Streamlit 테마 설정
├── 실행.bat / prepare.bat   # Windows 더블클릭 실행
├── requirements.txt
├── .gitignore
└── README.md
```

</details>

위험점수 계산 방법은 [docs/risk_model.md](docs/risk_model.md), 팀 공동작업은 [docs/upload_guide.md](docs/upload_guide.md) 에 있습니다.
````

초안에서 확인할 것: 트리에 적은 모든 경로가 이동 뒤 실제로 있어야 한다(규칙 6). `scripts/`·`tests/` 줄은 ref-scripts-sql 결정, `pages/` 화면 이름은 ref-pages 결정에 맞춰 고친다.
