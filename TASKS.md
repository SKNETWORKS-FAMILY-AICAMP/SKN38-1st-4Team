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
- [ ] rainfall-all-districts — 보류(2026-11-11 사용자가 5개 구 우선 선택) · 미산정 643개 해소: 기상청 2025 시간 강수량으로 19개 구 추가 · writes build_rainfall.py, data/kma_hourly/*.csv, data/rainfall.csv, data/risk_audit.json, test_risk_inventory.py, README.md, RISK_MODEL.md, sql/skn_1st_4team.sql · verify `.venv/bin/python build_rainfall.py --check-only` 후 위 판정 명령
- [ ] restructure-reference-layout — 참고 저장소 SKN38-1st-1Team 구조(app.py 진입점·pages/ 번호 화면·services/·scripts/·sql/·data/·docs/)대로 app.py 와 루트 모듈을 분해·이동 · 1단계 분석 세션 4개 → docs/restructure/reference_*.md · 2단계 기능별 세션 · verify 판정 명령(기준 28 통과) + 앱 세 화면 확인

## 지켜야 할 제약
- (2026-11-11) "python라이브러리에서 GPS 라이브러리 이용해서 현재위치 기능 추가해줘."
- README 원칙: 프로젝트에 HTML·CSS·JavaScript 파일을 두지 않고 `unsafe_allow_html` 을 쓰지 않는다.
- (2026-11-11) "5개 구만 우선적으로 구현을 진행하려고 해"
- 위험점수 규칙(RISK_MODEL.md): 빠진 입력을 0으로 채우거나 가중치를 재분배하지 않는다.

## 인계
- 갱신: 2026-11-11 09:45 (restructure-reference-layout 진행 중 · rainfall-all-districts 는 보류)
- 다음 행동(restructure): 분석 세션 4개(ref-pages·ref-services·ref-scripts-sql·ref-data-docs, 09:22 사용자 중단 → 재개) 보고서가 docs/restructure/ 에 모이면 메인이 docs/restructure/target_map.md(옛→새 경로, 세션별 쓰기 목록 안 겹치게) 확정 → 기능별 세션 → 메인이 통합·옛 파일 삭제·검증·커밋
- 한도 대비(사용자 지시 2026-11-11 "세션이 한도에 걸릴 경우 codex cli를 이용해서 작업 계속 이어가도록 해"): 대본에 "You've hit your session limit" 가 마지막이면 .handoff/codex_fallback.py 가 herdr-launcher 로 codex(--effort high)를 띄워 .handoff/cards/<이름>.md 로 잇는다
- 기준점: git 커밋 57e85ef(구조 정리 전 전체, docs/restructure 제외) · 판정 명령+test_build_rainfall → 28 통과 · 실패 0 (09:24)
- 서비스 범위(service-five-districts, 끝남 09:40, 코드는 57e85ef 에 포함): 앱은 강수 자료가 있는 5개 구 163개만 표시. 구조 정리 때 유지할 것 — app.py 의 `FRAME = service_inventory()`·`SERVICE_AREA`·`unscored_count` 조건부 문구·분석 페이지 `counts.drop("미산정")`·도넛 범례 `domain=list(counts.index)`, test_risk_inventory 의 service 테스트
- 다음 행동(rainfall, 보류): 구를 늘릴 때만 「사용자 단계」 3번 로그인 → AWS 23지점(build_rainfall.STATIONS, 108 제외) + ASOS 108 의 2025 시간 강수량 CSV 를 data/kma_hourly/ 에 → `.venv/bin/python build_rainfall.py --check-only` → 쓰기 → risk_audit.json·SQL 덤프·문서 갱신. 강수 최대값(91)이 바뀌면 기존 163개 점수도 바뀐다
- 마지막 검증(서비스 범위): 판정 명령 → Ran 28 · OK · AppTest 홈 163개·구 선택 5개·분석 지표에 미산정 없음 · verify-app 흐름(홈·분석 캡처) 통과, 지도 배경만 인터넷 차단
- git: 2026-11-11 09:24 저장소 만듦(main). 커밋 안 된 파일은 `git status --short` 로 본다
- 미결정: 없음 (사용자가 2026-11-11 '5개 구 우선' 선택)

## 사용자 단계
1. 켜져 있는 앱(localhost:8501, 08:52 시작)을 끄고 다시 켠다 — 이전 코드를 메모리에 들고 있어 GPS 버튼이 안 보인다.
2. 실제 브라우저에서 ‘◎ 현재 위치’ → ‘GPS로 내 위치 찾기’ → 위치 ‘허용’. macOS 는 시스템 설정 > 개인정보 보호 및 보안 > 위치 서비스에서 브라우저도 켜져 있어야 한다.
3. (보류 — 구를 늘릴 때만) (강수) Claude 앱 오른쪽 브라우저 창에 열린 data.kma.go.kr 에서 직접 로그인한다(회원가입 필요 시 가입). 비밀번호는 Claude 가 입력하지 않는다.

## 결정
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
