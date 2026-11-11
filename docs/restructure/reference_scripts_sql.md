# 참고 저장소 scripts·sql 분석과 우리 일괄 작업·SQL·실행 파일·테스트의 새 위치

- 작성: 2026-11-11, 읽기 전용 분석 세션(참고 분석: scripts·sql·테스트 위치)
- 참고 저장소: `SKNETWORKS-FAMILY-AICAMP/SKN38-1st-1Team` main, 커밋 `61ef27d0` (2026-11-11 08:56 +0900), `--depth 1` 로 받음
- 참고 저장소 안의 코드는 실행하지 않았다. 우리 쪽 측정은 프로젝트 사본(스크래치패드 `mirror/`)에서만 했고, 이 프로젝트에서는 판정 명령을 `-B`(바이트코드 파일 안 만듦)로 한 번 돌렸다.
- 줄 번호 표기: 참고 저장소는 `ref:scripts/…:줄`, 우리 코드는 `파일:줄`(2026-11-11 09:20 기준, 커밋 전 상태).

## 1 참고 저장소 사실

### 1.1 `scripts/` 구성 (사실)

`scripts/` 에는 11개 항목이 있다: `.py` 9개, `.bat` 1개, 빈 `.gitkeep` 1개. `__init__.py` 는 없다(이름공간 패키지로 import 됨). 반대로 `services/__init__.py` 는 있다.

| 파일 | 성격 | 입력 → 출력 | 근거 |
|---|---|---|---|
| `molit_api.py` | 수집(국토부 OpenAPI 호출) | API → 메모리(행 목록) | `ref:scripts/molit_api.py:1`, `:67`, `:103` |
| `preprocess_registration.py` | 전처리·검증 | API 응답 → `data/raw/molit_registration_sido_{월}.json`, `data/processed/truck_business_by_sigungu_{월}.csv` | `:27-29`, `:121-128` |
| `update_registration_db.py` | DB 적재(월간 갱신, 트랜잭션) | API → MySQL 3테이블, 로그 `logs/update_registration_db.log` | `:1-20`, `:45-47`, `:355-399` |
| `load_registration_csv.py` | DB 적재(API 키 없을 때 대체) | `data/processed/…202609.csv` → MySQL | `:1-4`, `:11` |
| `run_update_registration.bat` | 스케줄러 실행 파일 | `update_registration_db.py` 실행 | `:2`, `:6-7` |
| `load_faqs.py` | 변환·DB 적재 | `data/faq/jimni_faq.md` → `data/processed/jimni_faq.json` → MySQL `faqs` | `:3-4`, `:31-32` |
| `seed_drivers.py` | 시드(가상 기사) | 시군구 좌표 캐시 → MySQL `drivers` | `:6`, `:27-28` |
| `seed_drivers_excel.py` | 시드(엑셀 기반 1만 명) | `data/processed/*.xlsx`, `driver_places.csv` → MySQL | `:4-7`, `:19-21` |
| `collect_driver_places.py` | 수집(카카오 장소 좌표) | 카카오 API → `data/processed/driver_places.csv` | `:12`, `:32-33` |
| `test_booking_lookup.py` | DB·화면 통합 점검 | 실제 MySQL 세션의 임시 테이블 | `:1-7`, `:45-51` |

### 1.2 `scripts/` 로 가는 코드의 공통점 (사실)

- 앱(`streamlit run app.py`)이 import 하지 않고, 사람이나 스케줄러가 따로 한 번씩 실행하는 코드다. 모든 파일이 `if __name__ == "__main__":` 실행 입구를 가진다(`ref:scripts/molit_api.py:118`, `preprocess_registration.py:131`, `update_registration_db.py:419`, `load_faqs.py:193`, `seed_drivers.py:150`, `seed_drivers_excel.py:184`, `collect_driver_places.py:107`, `test_booking_lookup.py:183`, `load_registration_csv.py:42`).
- 쓰기 동작에는 미리보기·점검 모드가 따로 있다: `--check`·`--dry-run`(`update_registration_db.py:404-405`), `--apply` 를 줘야 적재(`load_faqs.py:15-16`, `:161`), `--dry-run`(`seed_drivers_excel.py:20`, `:128`).
- 파일 맨 위 docstring 에 목적·입력·출력·실행 명령을 적는다(위 표의 근거 줄 전부).

### 1.3 테스트가 `scripts/` 에 있는 이유 (사실 + 추측)

- 사실: 참고 저장소 전체에 `unittest`·`pytest` 를 쓰는 파일이 하나도 없다(`.py` 전체 grep, 0건). `tests/` 폴더도 없다.
- 사실: `test_booking_lookup.py` 는 unittest 가 아니라 직접 실행하는 점검 스크립트다. 자체 `check()` 로 PASS/FAIL 을 출력하고(`:28-30`), 실패하면 종료 코드 1(`:178-180`). 실행은 `python scripts/test_booking_lookup.py`(`:7`).
- 사실: 실제 MySQL 연결이 있어야 돈다. 같은 세션에 TEMPORARY TABLE 을 만들고(`:3-5`, `:54-57`), `sql/schema.sql` 에서 DDL 을 읽어 온다(`:46-51`). 실제 테이블 건수가 전후로 같은지 확인한다(`:168`, `:176-177`). 화면은 `pages/3_Booking_Lookup.py` 를 `AppTest` 로 연다(`:125`, `:128`).
- 추측: DB·`.env` 가 있어야 하는 "실행형 점검"이라 다른 일괄 작업과 같은 취급을 받아 `scripts/` 에 놓였다. 자동 테스트 묶음을 의도한 배치가 아니다.

### 1.4 파일 이름 규칙 (사실)

- 동사_명사(목적어) 순서: `collect_driver_places`, `load_faqs`, `load_registration_csv`, `preprocess_registration`, `seed_drivers`, `seed_drivers_excel`, `update_registration_db`. 동사 목록은 collect·load·preprocess·seed·update.
- 예외 2개: `molit_api.py`(동사 없는 클라이언트 모듈, 다른 스크립트가 import 함 — `update_registration_db.py:36`, `preprocess_registration.py:133`), `test_booking_lookup.py`(`test_` 접두어).
- 실행 파일은 `run_` + 대상 스크립트 이름: `run_update_registration.bat`.

### 1.5 `scripts/` 가 `services` 와 서로를 import 하는 방법 (사실)

세 가지 방식이 섞여 있다.

| 방식 | 실행 명령 | 근거 |
|---|---|---|
| A. 루트를 `sys.path` 맨 앞에 넣고 `services` import | `python scripts/x.py` | `load_faqs.py:28-29`, `test_booking_lookup.py:17-21` |
| B. `scripts/` 자신을 `sys.path` 에 넣고 형제 모듈을 맨 이름으로 import | `python scripts/x.py` | `update_registration_db.py:35-37`, `preprocess_registration.py:132-133` |
| C. `sys.path` 처리 없이 패키지 경로로 import (루트에서 `-m` 으로 실행해야 함) | `python -m scripts.x` | `seed_drivers.py:6`, `:14-17`; `seed_drivers_excel.py:20-21`, `:34-37`; `collect_driver_places.py:15`, `:26-30`; `load_registration_csv.py:4`, `:9` |

- 경로 기준점은 모두 `ROOT = Path(__file__).resolve().parents[1]`(`molit_api.py:29`, `preprocess_registration.py:27`, `load_faqs.py:28`, `update_registration_db.py:45`, `test_booking_lookup.py:17`, `collect_driver_places.py:32-33`).
- 예외: `seed_drivers.py:27-28`, `load_registration_csv.py:11` 은 `"data/processed/…"` 상대 경로를 써서, 루트에서 실행해야만 맞다.
- `services` 쪽도 SQL 을 같은 방식으로 찾는다: `ref:services/truck_stats.py:19` `QUERY_FILE = Path(__file__).resolve().parents[1] / "sql" / "registration_queries.sql"`.

### 1.6 입력·출력 경로 규칙 (사실)

- 외부에서 받은 원본은 `data/raw/`, 가공 결과는 `data/processed/`, 팀이 쓴 원문은 `data/faq/`(`preprocess_registration.py:28-29`, `:124-125`; `load_faqs.py:31-32`; `collect_driver_places.py:32`).
- 출력 폴더는 스크립트가 만든다(`preprocess_registration.py:122-123`).
- 로그는 `logs/`, `.gitignore` 의 `*.log` 로 올리지 않는다(`update_registration_db.py:19`, `:47`).

### 1.7 실행 안내 방식 (사실)

- 각 스크립트 docstring 에 실행 명령(위 1.2 근거 줄).
- 파이프라인 문서 `ref:docs/registration_pipeline.md:7-12` 에 파일별 역할 표, `:95-99` 에 실행 순서, `:114`, `:121` 에 Windows 작업 스케줄러 등록 명령.
- `ref:scripts/run_update_registration.bat` 는 ASCII 전용(`:3`), `chcp 65001`·`PYTHONIOENCODING=utf-8`(`:4-5`), `cd /d "%~dp0.."` 로 루트로 이동(`:6`), `.venv\Scripts\python.exe` 로 실행(`:7`), 종료 코드 전달(`:8`).
- README 폴더 트리에는 한 줄 설명만 있다: `scripts/ # 데이터 수집 및 DB 적재`, `sql/ # DB 스키마 및 쿼리`(`ref:README.md:208`, `:210`).

### 1.8 `sql/` 의 분리 방식 (사실)

| 파일 | 역할 | 근거 |
|---|---|---|
| `schema.sql` | 전체 DDL: `CREATE TABLE` 7개 → PK `ALTER` → FK `ALTER` 순서 | `ref:sql/schema.sql:1-99`, `:109-133`, `:140-148` |
| `registration_queries.sql` | 화면 한 곳(`pages/4_Truck_Map.py`)용 조회 4개. 순서가 고정되어 `services/truck_stats.py` 가 `;` 로 잘라 그대로 읽는다 | `ref:sql/registration_queries.sql:2-3`; `ref:services/truck_stats.py:3`, `:24-29` |
| `registration_stats_unique.sql` | 선택 마이그레이션(UNIQUE 인덱스), 실행 전 확인 쿼리를 주석으로 둠 | `:1-17` |
| `bookings_agreement_columns.sql` | 기존 DB 용 1회 마이그레이션(`ALTER TABLE … ADD COLUMN`), 새 DB 는 `schema.sql` 에 이미 포함 | `:1-15` |

- 규칙: 구조(schema) 1파일, 기능별 조회(`<주제>_queries.sql`) 1파일씩, 변경(`<테이블>_<변경내용>.sql`) 1파일씩. 머리 주석에 용도·데이터 출처 스크립트·실행 전 확인을 적는다.
- `sql/` 에는 `.sql` 만 있다. SQL 을 만드는 파이썬 코드는 없다.

## 2 따라야 할 규칙

참고 저장소에서 확인한 사실(1장)을 우리 프로젝트에 옮길 때의 규칙이다. 괄호는 근거.

1. 앱이 import 하지 않고 사람이 따로 실행하는 일괄 작업은 `scripts/` 에 둔다(1.2). → `build_rainfall.py`, `sql/build_dump.py` 가 해당.
2. 스크립트 이름은 동사_명사(1.4). 이미 규칙에 맞는 이름은 바꾸지 않는다.
3. import 방식은 참고의 세 방식 중 A 하나로 통일한다: `ROOT = Path(__file__).resolve().parents[1]` + `sys.path.insert(0, str(ROOT))`(1.5). 이유: `python scripts/x.py` 와 `python -m scripts.x` 둘 다 동작하고(사본에서 확인, 4장), 우리 문서가 이미 `python build_rainfall.py` 형태로 안내하고 있어 명령 모양이 크게 안 바뀐다. 참고의 B·C 방식은 따르지 않는다(B는 형제 모듈만 보이고, C는 `-m` 을 빠뜨리면 바로 깨진다).
4. 데이터 경로는 `ROOT` 기준으로만 쓴다. 상대 문자열 경로(참고 `seed_drivers.py:27` 같은 것)는 쓰지 않는다(1.5 예외).
5. 쓰기 동작은 점검 모드를 먼저 둔다(1.2). 우리 `build_rainfall.py --check-only`(`build_rainfall.py:141`)가 이미 맞다.
6. `sql/` 에는 `.sql` 만 둔다(1.8). 덤프 생성기는 `scripts/` 로 옮긴다.
7. 실행 안내는 각 스크립트 docstring 과 README 에 둔다(1.7). 스케줄러용 `.bat` 은 `scripts/` 에 두되, 사용자가 더블클릭하는 진입 `.bat` 은 참고에 대응물이 없으므로 루트에 둔다(4.3 근거).
8. 테스트는 참고를 따르지 않는다: 참고는 자동 테스트 묶음이 없어서(1.3) 따를 형태가 없다. 우리 6개는 모두 `unittest.TestCase` 이므로 `tests/` 에 모은다(3.2에서 근거·명령).

## 3 우리 코드 대응표

### 3.1 대응표

"사실" 칸은 코드를 읽거나 사본에서 실행해 확인한 것, "추측·조건" 칸은 다른 세션의 결정에 따라 달라지는 것이다.

| 옛 경로 | 새 경로 | 이유 | 고쳐야 할 import·경로·명령 (사실, 사본에서 확인) | 추측·조건 |
|---|---|---|---|---|
| `build_rainfall.py` | `scripts/build_rainfall.py` | 앱이 import 하지 않는 일괄 변환(기상청 시간자료 → `data/rainfall.csv`), 이름이 이미 동사_명사 | `build_rainfall.py:20` `from risk_model import …` → 아래 줄 뒤로 옮기고 `# noqa: E402`; `build_rainfall.py:22` `ROOT = Path(__file__).resolve().parent` → `.parents[1]` 와 다음 줄에 `sys.path.insert(0, str(ROOT))`(`sys` 는 `:15` 에서 이미 import); docstring `:6-7` `python build_rainfall.py` → `python scripts/build_rainfall.py`; `:140`, `:145` 의 `ROOT / "data" / …` 는 `ROOT` 만 고치면 그대로 맞다 | `risk_model.py` 가 `services/` 로 가면 `:20` 은 `from services.risk_model import …`. `data/` 가 raw·processed 로 나뉘면 `:140` → `ROOT / "data" / "processed" / "rainfall.csv"`, `:145` → `ROOT / "data" / "raw" / "kma_hourly"`, 안내 문구 `:4`, `:139`, `:148` 도 같이 |
| `sql/build_dump.py` | `scripts/build_sql_dump.py` | `sql/` 에는 `.sql` 만(규칙 6). `build_dump` 만으로는 무엇의 덤프인지 안 보여 목적어를 붙임 | `sql/build_dump.py:18-19` 는 그대로 맞다(`parent.parent` 가 `scripts/` 에서도 루트); `:25` `OUTPUT = Path(__file__).resolve().parent / "skn_1st_4team.sql"` → `ROOT / "sql" / "skn_1st_4team.sql"`(안 고치면 `scripts/skn_1st_4team.sql` 에 씀); docstring `:1`, `:8` 과 덤프 머리말 문자열 `:136`(`sql/build_dump.py 가 만든 파일`) 을 새 이름으로 | `:24` `DATA = ROOT / "data"` 와 `:174`, `:179` 의 `DATA / "flood_depth.xlsx"`, `DATA / "rainfall.csv"` 는 data 폴더 분할 시 바뀜. `:122`, `:163-165` 의 `parking_marker`·`parking_data`·`risk_data` import 와 `:108` `ROOT / "app.py"`(FAQ 목록을 `app.py` 에서 읽음)는 services·pages 재배치 시 바뀜 |
| `sql/skn_1st_4team.sql` | 그대로 | 생성물 덤프, `.sql` 이므로 `sql/` 에 둠 | 없음. 생성기 이름을 바꾸면 다음 재생성 때 1줄째 머리말 문구가 바뀜 | 참고의 `schema.sql` 처럼 DDL 만 따로 떼는 것은 메인 세션 결정(5장) |
| `sql/faq_queries.sql` | 그대로 | 참고의 `<주제>_queries.sql` 규칙과 같음 | 없음. 앱 코드가 읽지 않음(실행 안내만 `:6-7`) | FAQ 가 `app.py` 에서 `data/faq/` 로 옮겨져도 이 파일은 DB 테이블만 봄 |
| `sql/flood_rainfall_queries.sql` | 그대로 | 위와 같음 | 없음(`:6-7` 실행 안내는 `sql/…` 그대로 맞음) | 없음 |
| `sql/parking_risk_queries.sql` | 그대로 | 위와 같음 | 없음(`:5-6`) | 없음 |
| `launch.py` | 그대로(루트) | 앱 진입점의 일부. `app.py:28` 이 `from launch import main` 으로 부르고, `실행.bat:9` 가 직접 실행. 참고 `scripts/` 의 성격(데이터 일괄 작업)과 다름 | 테스트·스크립트 이동만으로는 바뀌는 줄 없음. `launch.py:12` `APP_DIR = Path(__file__).resolve().parent`, `:17-18` `.venv` 경로, `:50` `"app.py"`, `:53` `cwd=APP_DIR` 모두 루트 기준이라 그대로 맞다 | `app.py` 가 루트에 남는 한 그대로. 만약 `scripts/` 로 옮긴다면 `:12` → `.parents[1]`, `app.py:28` → `from scripts.launch import main`, `실행.bat:9` → `scripts\launch.py` 세 곳(추천하지 않음) |
| `실행.bat` | 그대로(루트) | 사용자가 더블클릭하는 진입점. `app.py:25` 가 `cwd=` 루트에서 `"실행.bat"` 으로 부르고, `README.md:17`, `UPLOAD_GUIDE.md:15` 가 루트 파일로 안내 | 테스트·스크립트 이동만으로는 바뀌는 줄 없음(`:3` `cd /d "%~dp0"`, `:7` `call prepare.bat`, `:9` `launch.py`) | 없음 |
| `prepare.bat` | 그대로(루트) | `실행.bat:7` 이 같은 폴더에서 부름 | 테스트·스크립트 이동만으로는 바뀌는 줄 없음. 검증 단계는 `:56` `py_compile app.py parking_marker.py`, `:58` `from parking_marker import marker_icon, risk_band` 두 줄뿐이며 테스트·`build_rainfall`·`sql` 을 부르지 않음 | `parking_marker.py` 가 `services/` 로 가면 `:56` → `app.py services\parking_marker.py`, `:58` → `from services.parking_marker import …`. `app.py` 가 `pages/` 구조로 바뀌면 `:56` 컴파일 대상도 |
| `test_risk_model.py` | `tests/test_risk_model.py` | `unittest` 묶음, 루트 정리 | 파일 안 바뀌는 줄 없음(`:3` 은 루트가 `sys.path` 에 있어 그대로 동작) | `risk_model` 이 `services/` 로 가면 `:3` → `from services.risk_model import …` |
| `test_parking_marker.py` | `tests/test_parking_marker.py` | 위와 같음 | 없음(`:3`) | `parking_marker` 이동 시 `:3` |
| `test_map_payload.py` | `tests/test_map_payload.py` | 위와 같음 | 없음(`:6`) | `map_payload` 이동 시 `:6` |
| `test_risk_inventory.py` | `tests/test_risk_inventory.py` | 위와 같음 | `:16` `cls.base = Path(__file__).parent / "data"` → `Path(__file__).resolve().parents[1] / "data"`(안 고치면 `tests/data/risk_audit.json` 을 찾다가 setUpClass 오류, 사본에서 확인) | `:7-10` 의 `map_payload`·`parking_data`·`parking_marker`·`service_config` import 는 services 이동 시. data 분할 시 `:16`, `:23` 과 `data/risk_audit.json` 의 `source_sha256` 키(지금 `seoul_parking.csv`·`lowland.csv`·`rainfall.csv`·`flood_depth.xlsx`, `data/` 기준 이름)가 같이 바뀜 |
| `test_gps_location.py` | `tests/test_gps_location.py` | 위와 같음 | `:10` `APP = str(Path(__file__).resolve().parent / "app.py")` → `.parents[1] / "app.py"`(안 고치면 AppTest 3개가 `tests/app.py` 없음으로 오류, 사본에서 확인) | `:7-8` `import parking_map`, `from parking_map import …` 와 `:43` `mock.patch.object(parking_map, "get_geolocation", …)` 는 `parking_map` 이 `services/` 로 가면 `services.parking_map` 으로. mock 대상이 그 모듈 객체여야 하므로 import 이름과 함께 바꿔야 함 |
| `test_build_rainfall.py` | `tests/test_build_rainfall.py` | 위와 같음 | `:9` `from build_rainfall import read_hourly, gaps, main` → `from scripts.build_rainfall import read_hourly, gaps, main`; docstring `:1` 파일 이름 | 없음 |
| (새 파일) | `tests/__init__.py` (빈 파일) | 없으면 `python -m unittest discover -s tests -t .` 가 `Start directory is not importable` 로 실패(Python 3.13.15, 사본에서 확인) | — | — |
| (새 폴더) | `scripts/` (`__init__.py` 없음) | 참고와 같음. 이름공간 패키지로 `from scripts.build_rainfall import …` 와 `python -m scripts.build_rainfall` 둘 다 동작(사본에서 확인) | — | 메인 세션이 `__init__.py` 를 두기로 해도 동작은 같음 |

### 3.2 테스트 위치 추천: `tests/` 로 모은다

- 근거 1(사실): 참고 저장소에는 자동 테스트 묶음이 없고, 유일한 `test_booking_lookup.py` 는 실제 MySQL 이 필요한 실행형 점검이라 `scripts/` 에 있다(1.3). 우리 6개는 모두 `unittest.TestCase` 이고 DB 없이 돈다. 성격이 달라 참고 배치를 그대로 따를 이유가 없다.
- 근거 2(사실): 6개 파일이 루트 파일 30여 개 가운데 섞여 있다. 사용자가 원한 것이 루트 정리다.
- 근거 3(사실, 측정): 사본에서 `tests/` 로 옮기고 3.1 의 4줄(`test_risk_inventory.py:16`, `test_gps_location.py:10`, `test_build_rainfall.py:9`, `tests/__init__.py` 추가)만 고치자 28개 통과. 고치기 전에는 21개만 실행되고 오류 5개(가져오기 실패 1, AppTest 경로 3, 데이터 경로 1).
- 대가: 테스트를 루트에서만 실행할 수 있다. `tests/` 안에서 `python -m unittest test_risk_model` 을 치면 `risk_model` 을 못 찾아 실패한다(사본에서 확인).

바뀐 뒤의 판정 명령(루트에서, 사본에서 `Ran 28 tests … OK` 확인):

```bash
.venv/bin/python -m unittest discover -s tests -t .
```

개별 실행이 필요하면:

```bash
.venv/bin/python -m unittest tests.test_risk_model tests.test_build_rainfall
```

이 명령을 같이 고쳐야 하는 문서 줄(사실): `README.md:58`, `RISK_MODEL.md:33`(둘 다 지금 `python -m unittest test_risk_model … test_build_rainfall`). `TASKS.md` 「인계」의 판정 명령도. `README.md:52` 의 `python build_rainfall.py` 는 `python scripts/build_rainfall.py` 로, `RISK_MODEL.md:27` 과 `service_config.py:5`(주석)의 `build_rainfall.py` 언급은 `scripts/build_rainfall.py` 로.

### 3.3 실행 파일에서 같이 바꿀 줄 정리

| 파일:줄 | 지금 | 테스트·scripts 이동 때 | services·pages 재배치 때(다른 세션 결정) |
|---|---|---|---|
| `prepare.bat:56` | `py_compile app.py parking_marker.py` | 그대로 | 옮긴 경로로 |
| `prepare.bat:58` | `from parking_marker import marker_icon, risk_band` | 그대로 | `from services.parking_marker import …` 등 |
| `실행.bat:9` | `".venv\Scripts\python.exe" launch.py` | 그대로 | `launch.py` 를 옮기지 않으면 그대로 |
| `launch.py:50` | `"app.py"` | 그대로 | `app.py` 가 루트 진입점으로 남으면 그대로(참고도 `app.py` 가 루트) |
| `app.py:25`, `app.py:28` | `"실행.bat"`, `from launch import main` | 그대로 | `실행.bat`·`launch.py` 를 루트에 두면 그대로 |

## 4 깨질 위험과 대비

| 위험 | 사실/추측 | 대비 |
|---|---|---|
| `test_risk_inventory.py:16`, `test_gps_location.py:10` 을 안 고치면 오류 5개, `tests/__init__.py` 를 빼면 탐색 자체가 실패 | 사실(사본 측정) | 3.1 의 고칠 줄을 이동과 같은 커밋에 넣고, 이동 직후 `discover -s tests -t .` 결과가 `Ran 28` 인지 확인. 21개로 줄면 가져오기 실패가 숨은 것 |
| `build_rainfall.py` 를 옮기고 `ROOT` 만 고치고 `sys.path` 를 안 넣으면 `python scripts/build_rainfall.py` 가 `risk_model` 을 못 찾음 | 사실(`python scripts/x.py` 는 `scripts/` 만 `sys.path` 에 넣음) | 규칙 3 의 `sys.path.insert` 를 같이. 사본에서 `python scripts/build_rainfall.py --check-only` 와 `python -m scripts.build_rainfall --check-only` 둘 다 import 를 통과함을 확인 |
| `sql/build_dump.py:25` 를 안 고치면 덤프가 `scripts/skn_1st_4team.sql` 로 써지고 `sql/` 의 덤프는 낡은 채로 남음 | 사실(코드) | `:25` 를 `ROOT / "sql" / …` 로. 사본에서 고친 생성기의 출력이 `sql/skn_1st_4team.sql` 에 써짐을 확인 |
| 다른 세션('점수 미산정처리 원인')이 루트의 `build_rainfall.py` 를 고치는 중에 이동하면 변경이 갈라짐 | 추측(동시 편집) | 그 세션이 끝난 뒤 옮기거나, 옮기기 전에 아래 전달 사항을 보냄 |
| `data/` 를 raw·processed 로 나누면 `build_rainfall.py:140`, `:145`, `test_risk_inventory.py:16`·`:23`, `data/risk_audit.json` 키, `sql/build_dump.py:174`·`:179`, `service_config.py:12` 가 한꺼번에 바뀜 | 사실(줄 목록) / 분할 여부는 추측 | data 분할을 한 단위로 묶고 같은 커밋에서 위 줄을 모두 고침 |
| `parking_map` 을 옮기면 `test_gps_location.py:43` 의 `mock.patch.object(parking_map, …)` 가 옛 모듈을 패치해 GPS 흐름 테스트가 브라우저 응답을 못 받음 | 추측(mock 대상이 모듈 객체라서) | import 이름과 mock 대상을 같은 새 모듈로 |
| 루트에 `__pycache__/`, `sql/__pycache__/` 가 남아 옛 모듈 이름으로 import 가 될 것처럼 보임 | 사실(두 폴더 있음, `.gitignore` 로 올라가지는 않음) | 이동 뒤 지워도 됨(생성물). 지우기는 메인 세션 판단 |

### 다른 세션('점수 미산정처리 원인')에 알릴 것

1. 새 위치: `build_rainfall.py` → `scripts/build_rainfall.py`, `test_build_rainfall.py` → `tests/test_build_rainfall.py`.
2. 새 실행 명령: `.venv/bin/python scripts/build_rainfall.py --check-only`, 쓰기는 `--check-only` 없이. 판정 명령은 `.venv/bin/python -m unittest discover -s tests -t .`.
3. 파일 안에서 바뀌는 줄: `ROOT` 가 `.parents[1]` 이 되고 그 아래 `sys.path.insert(0, str(ROOT))` 가 들어가며, `from risk_model import …` 는 그 뒤로 내려감. 테스트는 `from scripts.build_rainfall import …`.
4. 기본 입력·출력 경로(`data/kma_hourly/`, `data/rainfall.csv`)는 data 폴더를 나누지 않는 한 그대로. 나누기로 하면 `:140`, `:145` 와 안내 문구 `:4`, `:139`, `:148` 이 바뀌므로 내려받은 CSV 를 둘 폴더도 바뀜.
5. 그 세션이 고칠 예정인 `test_risk_inventory.py` 는 이동 뒤 `:16` 기준 경로가 바뀌어 있음. `README.md:52`·`:58`, `RISK_MODEL.md:27`·`:33` 의 명령도 새 명령으로.
6. `sql/skn_1st_4team.sql` 재생성 명령은 `python scripts/build_sql_dump.py` 가 됨.

### 진행 중 발견한 이상 (조사하지 않음, 보고만)

- `data/kma_hourly/` 가 없을 때 `build_rainfall.py` 는 `:148` 의 안내 대신 `FileNotFoundError` 를 낸다. 없는 폴더를 파일로 취급하기 때문(`:145-146`). 이 프로젝트에서 `--check-only` 로 확인. 선택지: 그 세션이 `:146` 에서 존재 여부를 보도록 고치기 / 그대로 두기.
- 지금 `sql/skn_1st_4team.sql` 은 `app.py` FAQ 와 어긋나 있다. 사본에서 생성기를 다시 돌리면 62번째 줄(FAQ004 답변, GPS 안내 문장)만 다르다. GPS 세션이 FAQ 를 바꾼 뒤 덤프를 다시 만들지 않은 것으로 보임(추측). 선택지: 구조 정리 때 생성기로 다시 만들기 / 강수 작업 때 같이 다시 만들기.

## 5 메인 세션이 정할 것

모두 되돌릴 수 있는 결정이며, 괄호가 이 보고서의 추천이다.

1. 덤프 생성기 새 이름: `scripts/build_sql_dump.py`(추천) / 이름 유지 `scripts/build_dump.py`. 이름을 바꾸면 `sql/build_dump.py:1`, `:8`, `:136` 문구와 문서 명령이 같이 바뀐다.
2. 이동 순서: '점수 미산정처리 원인' 세션이 `build_rainfall.py`·`test_build_rainfall.py`·`test_risk_inventory.py` 를 다 고친 뒤 이동(추천) / 지금 이동하고 4장의 전달 사항을 그 세션에 보냄.
3. data 폴더 분할(ref-data-docs 보고서 결정)과 이 이동을 한 커밋으로 묶을지: 나눔(추천: 테스트·scripts 이동을 먼저 커밋하고 `Ran 28` 확인, 그다음 data 분할) / 한 번에.
4. `sql/skn_1st_4team.sql` 에서 참고의 `schema.sql` 처럼 DDL 만 떼어 낼지: 떼지 않음(추천: 덤프가 생성물이라 생성기가 둘을 따로 써야 하고, 지금 이 파일 하나로 적재 안내가 끝남) / 떼어 냄.
5. `scripts/__init__.py` 를 둘지: 두지 않음(추천: 참고와 같고 사본에서 동작 확인) / 둠.
