# TASKS — 침착 앱 현재 위치(GPS) 기능
<!--
규칙 1: 「인계」는 40줄·3,000자 안에 쓴다. 넘치는 계약·긴 메모는 「결정」으로 옮긴다.
규칙 2: 「인계」 말고는 통째로 다시 쓰지 않는다. 할 일·제약·결정·함정·실측은 줄 단위로만 고친다.
-->

## 끝났다는 것
지도 위 ‘◎ 현재 위치’ 팝오버의 ‘GPS로 내 위치 찾기’가 브라우저 위치로 기준점·반경·거리를 바꾸고, 거부·대기도 안내한다.
판정: `.venv/bin/python -m unittest test_risk_model test_parking_marker test_map_payload test_risk_inventory test_gps_location`

## 할 일
- [x] gps-location — streamlit-js-eval 로 현재 위치 추가 · 검증 위 판정 명령 통과(24) · 앱 안 브라우저(8502)에서 거부·도착 두 경로 확인 · 커밋 없음(git 저장소 아님) (2026-11-11 09:05)
- [ ] rainfall-all-districts — 미산정 643개 해소: 기상청 2025 시간 강수량으로 19개 구 추가 · writes build_rainfall.py, data/kma_hourly/*.csv, data/rainfall.csv, data/risk_audit.json, test_risk_inventory.py, README.md, RISK_MODEL.md, sql/skn_1st_4team.sql · verify `.venv/bin/python build_rainfall.py --check-only` 후 위 판정 명령

## 지켜야 할 제약
- (2026-11-11) "python라이브러리에서 GPS 라이브러리 이용해서 현재위치 기능 추가해줘."
- README 원칙: 프로젝트에 HTML·CSS·JavaScript 파일을 두지 않고 `unsafe_allow_html` 을 쓰지 않는다.

## 인계
- 갱신: 2026-11-11 (rainfall-all-districts 진행 중)
- 다음 행동: 「사용자 단계」 3번(data.kma.go.kr 로그인) 완료 후 → AWS 23지점(build_rainfall.STATIONS, 108 제외) + ASOS 108 의 2025-01-01 01시~2026-01-01 00시 시간 강수량 CSV 를 data/kma_hourly/ 에 받기 → `.venv/bin/python build_rainfall.py --check-only` 로 기존 5개 구 재현 확인 → 쓰기 → risk_audit.json·테스트·문서·SQL 덤프 갱신
- 마지막 검증: `.venv/bin/python -m unittest test_build_rainfall test_risk_model` → 통과 10 · 실패 0 · 가짜 CSV 로 재현·결측 1시간·불일치 세 경로 모두 의도대로(스크래치패드 rain_test)
- 커밋 안 된 파일: GPS 쪽 parking_map.py, app.py, requirements.txt, prepare.bat, README.md, test_gps_location.py · 강수 쪽 build_rainfall.py, test_build_rainfall.py · TASKS.md (git 저장소 아님)
- 미결정: 없음 (사용자가 2026-11-11 '강수 자료 추가' 선택)

## 사용자 단계
1. 켜져 있는 앱(localhost:8501, 08:52 시작)을 끄고 다시 켠다 — 이전 코드를 메모리에 들고 있어 GPS 버튼이 안 보인다.
2. 실제 브라우저에서 ‘◎ 현재 위치’ → ‘GPS로 내 위치 찾기’ → 위치 ‘허용’. macOS 는 시스템 설정 > 개인정보 보호 및 보안 > 위치 서비스에서 브라우저도 켜져 있어야 한다.
3. (강수) Claude 앱 오른쪽 브라우저 창에 열린 data.kma.go.kr 에서 직접 로그인한다(회원가입 필요 시 가입). 비밀번호는 Claude 가 입력하지 않는다.

## 결정
- (2026-11-11) GPS 라이브러리는 streamlit-js-eval 1.0.0 의 get_geolocation() — 권한 거부·시간 초과를 Python 으로 돌려준다. streamlit-geolocation 0.0.10 은 오류를 돌려주지 않아 제외.
- (2026-11-11) 서버 쪽 위치 라이브러리(geocoder IP 위치, gpsd)는 서버 컴퓨터의 위치라 사용자 위치가 아니어서 제외.
- (2026-11-11) 구별 관측소: 구 이름과 같은 AWS 지점, 없으면 주소가 그 구인 지점. 관악 509(남현 425 아님), 동작 410 기상청(현충원 889 아님), 영등포 510(한강 418 아님), 종로는 AWS 지점명이 없어 ASOS 108 서울(송월동, 북악산 422 은 해발 334m 산 지점이라 제외). 출처: data.kma.go.kr 관측지점정보.
- (2026-11-11) 기존 5개 구 값을 같은 내려받기에서 그대로 재현해야만 rainfall.csv 를 덮어쓴다(build_rainfall.py 가 강제).

## 함정
- 브라우저 위치는 https 또는 http://localhost 에서만 된다 — http://192.168… 로 접속하면 거부 안내가 뜨고 기준 위치를 직접 골라야 한다.
- 실행 중인 Streamlit 서버는 parking_map.py 수정을 자동으로 다시 읽지 않았다 — 서버를 다시 켜야 반영된다.
- 기상자료개방포털은 로그인 없이 조회하면 10줄만 보여 주고 CSV 내려받기는 로그인이 필요하다 — 1년치 시간자료는 로그인 후 CSV 로만 받는다. 시간 자료는 1회 최대 1년.
- verify-app 은 인터넷이 없는 컨테이너라 지도 배경(basemaps.cartocdn.com) 요청이 막혀 '실패'로 나온다 — 이번 변경과 무관.

## 실측
| 항목 | 값 | 출처 (날짜) |
|---|---|---|
| streamlit (.venv) | 1.67.0 | `.venv/bin/python -c "import streamlit"` (2026-11-11) |
| streamlit-js-eval 최신 | 1.0.0 | `pip index versions` (2026-11-11) |
