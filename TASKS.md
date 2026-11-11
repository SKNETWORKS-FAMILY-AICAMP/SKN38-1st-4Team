# TASKS — 침착 앱 현재 위치(GPS) 기능
<!--
규칙 1: 「인계」는 40줄·3,000자 안에 쓴다. 넘치는 계약·긴 메모는 「결정」으로 옮긴다.
규칙 2: 「인계」 말고는 통째로 다시 쓰지 않는다. 할 일·제약·결정·함정·실측은 줄 단위로만 고친다.
-->

## 끝났다는 것
지도 위 ‘◎ 현재 위치’ 팝오버의 ‘GPS로 내 위치 찾기’가 브라우저 위치로 기준점·반경·거리를 바꾸고, 거부·대기도 안내한다.
판정: `.venv/bin/python -m unittest test_risk_model test_parking_marker test_map_payload test_risk_inventory test_gps_location test_build_rainfall`

## 할 일
- [x] gps-location — streamlit-js-eval 로 현재 위치 추가 · 검증 위 판정 명령 통과(24) · 앱 안 브라우저(8502)에서 거부·도착 두 경로 확인 · 커밋 없음(git 저장소 아님) (2026-11-11 09:05)
- [x] service-five-districts — 앱 서비스·표시를 강수 자료가 있는 5개 구(163개, 전부 산정)로 좁힘, 점수·정규화 기준은 806개 그대로 · writes service_config.py, parking_data.py(service_inventory), app.py, parking_map.py, test_risk_inventory.py, README.md, RISK_MODEL.md · 검증 판정 명령에 test_build_rainfall 추가해 통과(28) · AppTest 홈·구별·분석 화면 미산정 0 · verify-app 흐름 통과(지도 배경만 인터넷 차단) (2026-11-11 09:40)
- [ ] rainfall-all-districts — 보류(2026-11-11 사용자가 5개 구 우선 선택) · 19개 구 확대 시 기상청 2025 시간 강수량으로 참고 지표 추가 및 최종 점수 CSV 확보 · verify `python scripts/build_rainfall.py --check-only` 후 `python -m unittest discover -s tests -t .`
- [x] restructure-reference-layout — 참고 저장소 SKN38-1st-1Team 구조로 앱 진입점·번호 화면·서비스·스크립트·테스트·데이터·문서 분리. 대응표 `docs/restructure/target_map.md` · 기존 테스트 28개 + 화면 회귀 테스트 1개 통과, 서버 세 화면 전환 확인, SQL 기준 일치 (2026-11-11)
- [x] supplied-risk-scores — `parking_risk_result_recalculated.csv`의 `total_risk_score` 137개를 관리번호로 연결. 서비스 163개 중 26개 미산정. 화면·지도·SQL 정수 확인, 테스트 29개 통과 (2026-11-11)

## 지켜야 할 제약
- (2026-11-11) "python라이브러리에서 GPS 라이브러리 이용해서 현재위치 기능 추가해줘."
- README 원칙: 프로젝트에 HTML·CSS·JavaScript 파일을 두지 않고 `unsafe_allow_html` 을 쓰지 않는다.
- (2026-11-11) "5개 구만 우선적으로 구현을 진행하려고 해"
- 위험점수 규칙(RISK_MODEL.md): 빠진 입력을 0으로 채우거나 가중치를 재분배하지 않는다.

## 인계
- 갱신: 2026-11-11 (최종 위험지수 CSV 적용 완료 · 강수 지역 확대 보류)
- 상태(supplied-risk-scores): 제공 파일에서 실제 G열인 `total_risk_score`를 `parking_lot_id`로 연결한다. 137개 원점수 21~80, 정수형 `Int64`. 서비스 5개 구 163개 중 26개 미산정. SQL의 전체 806개 행 중 669개는 최종 점수 NULL.
- 마지막 검증(supplied-risk-scores): Homebrew Python 3.12에서 `python -B -m unittest discover -s tests -t .` → 29 OK. AppTest 목록·핀·툴팁·상세·분석 정수 확인. 생성 SQL의 `tinyint unsigned` 및 137개 관리번호별 값이 원본 CSV와 일치. `git diff --check` 통과.
- 상태(restructure): `docs/restructure/target_map.md` 4단계 완료. 앱은 `app.py`로 실행. README의 새 테스트 명령이 이 문서 상단의 이동 전 GPS 판정 명령을 대체한다.
- 다음 행동(restructure): 메인 담당이 `git status --short`에서 이동 전후 파일을 확인하고 검증한 변경을 커밋한다. 테스트 명령은 프로젝트 루트에서 `python -m unittest discover -s tests -t .`.
- 마지막 검증(restructure): Homebrew Python 3.12 환경에서 29개 OK(기존 28개 + 화면 회귀 1개). AppTest와 실제 Streamlit 서버의 버튼 이벤트로 홈 → FAQ → 분석 → 홈, 5개 구·163개 확인. 생성 SQL의 주석 외 전체가 변경 전 생성 기준과 일치, 기존 덤프의 FAQ004 GPS 문구 동기화. 실제 브라우저 시각 검증과 Windows 배치 실행은 미실행.
- 커밋 안 된 파일: 구조 정리 변경과 점수 CSV, 화면·서비스·SQL·테스트·문서 변경을 `git status --short`에서 확인. 구조 변경 대응표는 `docs/restructure/target_map.md`. 임시 검증 환경 정리 완료.
- 한도 대비(사용자 지시 2026-11-11 "세션이 한도에 걸릴 경우 codex cli를 이용해서 작업 계속 이어가도록 해"): 대본에 "You've hit your session limit" 가 마지막이면 .handoff/codex_fallback.py 가 herdr-launcher 로 codex(--effort high)를 띄워 .handoff/cards/<이름>.md 로 잇는다
- 기준점: git 커밋 57e85ef(구조 정리 전 전체, docs/restructure 제외) · 판정 명령+test_build_rainfall → 28 통과 · 실패 0 (09:24)
- 서비스 범위(service-five-districts): `services.parking_data.service_inventory()`는 강수 자료가 있는 5개 구의 주차장 163개를 표시한다. CSV에 점수가 없으면 목록·지도·분석에서 미산정으로 표시한다.
- 다음 행동(rainfall, 보류): 구를 늘릴 때만 「사용자 단계」 3번 로그인 → AWS 23지점(`scripts.build_rainfall.STATIONS`, 108 제외) + ASOS 108의 2025 시간 강수량 CSV를 `data/raw/kma_hourly/`에 → `python scripts/build_rainfall.py --check-only` → 강수 집계 갱신. 최종 위험지수는 별도로 점수 CSV에 추가.
- 마지막 검증(서비스 범위): 판정 명령 → Ran 28 · OK · AppTest 홈 163개·구 선택 5개·분석 지표에 미산정 없음 · verify-app 흐름(홈·분석 캡처) 통과, 지도 배경만 인터넷 차단
- git: 2026-11-11 09:24 저장소 만듦(main). 커밋 안 된 파일은 `git status --short` 로 본다
- 미결정: 없음 (사용자가 2026-11-11 '5개 구 우선' 선택)

## 사용자 단계
1. 켜져 있는 앱(localhost:8501, 08:52 시작)을 끄고 다시 켠다 — 이전 코드를 메모리에 들고 있어 GPS 버튼이 안 보인다.
2. 실제 브라우저에서 ‘◎ 현재 위치’ → ‘GPS로 내 위치 찾기’ → 위치 ‘허용’. macOS 는 시스템 설정 > 개인정보 보호 및 보안 > 위치 서비스에서 브라우저도 켜져 있어야 한다.
3. (보류 — 구를 늘릴 때만) (강수) Claude 앱 오른쪽 브라우저 창에 열린 data.kma.go.kr 에서 직접 로그인한다(회원가입 필요 시 가입). 비밀번호는 Claude 가 입력하지 않는다.
4. (restructure 한도 대비) 터미널 패널 'codex 폴더 신뢰 1회' 탭에 뜬 Codex 화면에서 이 폴더를 신뢰(Trust)로 고른 뒤 `/quit` 으로 닫는다 — 신뢰 전에는 감시기가 띄운 Codex 가 'blocked' 로 멈춘다.

## 결정
- (2026-11-11) 한도 대비: 감시기 `.handoff/codex_fallback.py`(터미널 탭 'Codex 이어받기 감시', 60초 주기)가 등록부 `.handoff/sessions.json` 의 대본 끝이 한도 오류면 카드를 만들고 herdr-launcher 로 codex --effort high 를 띄운다. Codex 는 커밋 못 함(쓰기 범위 작업 폴더뿐) — 커밋은 메인. 2단계 세션은 시작 직후 등록부에 marker 로 추가. 멈추기: `touch .handoff/stop`.
- (2026-11-11) GPS 라이브러리는 streamlit-js-eval 1.0.0 의 get_geolocation() — 권한 거부·시간 초과를 Python 으로 돌려준다. streamlit-geolocation 0.0.10 은 오류를 돌려주지 않아 제외.
- (2026-11-11) 서버 쪽 위치 라이브러리(geocoder IP 위치, gpsd)는 서버 컴퓨터의 위치라 사용자 위치가 아니어서 제외.
- (2026-11-11) 구별 관측소: 구 이름과 같은 AWS 지점, 없으면 주소가 그 구인 지점. 관악 509(남현 425 아님), 동작 410 기상청(현충원 889 아님), 영등포 510(한강 418 아님), 종로는 AWS 지점명이 없어 ASOS 108 서울(송월동, 북악산 422 은 해발 334m 산 지점이라 제외). 출처: data.kma.go.kr 관측지점정보.
- (2026-11-11) 기존 5개 구 값을 같은 내려받기에서 그대로 재현해야만 rainfall.csv 를 덮어쓴다(build_rainfall.py 가 강제).
- (2026-11-11) 서비스 지역 = 주차장 목록의 구 ∩ rainfall.csv 의 구(service_config.SERVICE_DISTRICTS). 점수는 806개 전체로 계산한 뒤 화면용으로만 거른다 — id·정규화 기준·163개 점수가 그대로이고, parking_inventory()·SQL 덤프·FAQ 는 806개 기준으로 둔다(build_dump.py 가 app.py 의 FAQ 를 읽음). PARKING_DATA_VERSION 을 rainfall-districts-v4 로 올려 이전 세션의 비교함을 비운다. 강남역·서울시청 기준 장소는 서비스 밖이라 뺐다.

## 함정
- 브라우저 위치는 https 또는 http://localhost 에서만 된다 — http://192.168… 로 접속하면 거부 안내가 뜨고 기준 위치를 직접 골라야 한다.
- 실행 중인 Streamlit 서버는 parking_map.py 수정을 자동으로 다시 읽지 않았다 — 서버를 다시 켜야 반영된다.
- 기상자료개방포털은 로그인 없이 조회하면 10줄만 보여 주고 CSV 내려받기는 로그인이 필요하다 — 1년치 시간자료는 로그인 후 CSV 로만 받는다. 시간 자료는 1회 최대 1년.
- verify-app 은 인터넷이 없는 컨테이너라 지도 배경(basemaps.cartocdn.com) 요청이 막혀 '실패'로 나온다 — 이번 변경과 무관.
- verify-app 기본 desktop 캡처는 Streamlit 이 그리기 전이라 빈 화면(글자 27)이다 — `--script` 흐름 파일(프로젝트 안 .mjs)로 글자를 기다린 뒤 캡처해야 한다. 시작 명령은 `--start ".venv/bin/python -m streamlit run app.py --server.port 8501 --server.headless true --server.address 0.0.0.0" --port 8501`(설치는 기본 uv).
- Altair 범례는 scale domain 에 든 값을 모두 보여 준다 — 개수에서 뺀 등급(미산정)도 domain 에서 빼야 범례에서 사라진다.

## 실측
| 항목 | 값 | 출처 (날짜) |
|---|---|---|
| streamlit (.venv) | 1.67.0 | `.venv/bin/python -c "import streamlit"` (2026-11-11) |
| streamlit-js-eval 최신 | 1.0.0 | `pip index versions` (2026-11-11) |
