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
- [x] faq-sql-categories — 사용자 제공 `sql/Table07_faq.sql`을 화면·덤프 공통 원본으로 연결. FAQ 27개·카테고리 4개 선택 및 그룹 표시, 조회 SQL 3개 갱신. 폴더 이동 후 전체 테스트 33개 통과. Git 업로드 경로 13개는 `docs/upload_guide.md`에 지정, 업로드는 사용자 담당. 근거 `.handoff/faq-categories.md` (2026-11-11)

- [x] api-env — 루트 `.env` 생성·카카오 길찾기 클라이언트 인증 연결. 키가 없으면 HTTP 미호출, 운영 환경 변수 우선. 의존성·배치 검사·문서 갱신, 전체 테스트 37개 통과. 근거 `.handoff/api-env.md` (2026-11-11)
- [x] scored-service-only — 산정된 137개만 서비스 개수·검색·목록·지도·비교·분석에 포함. 미산정 안내 제거, 이전 세션 선택 초기화. 전체 38개 테스트 통과. 근거 `.handoff/scored-service-only.md` (2026-11-11)
- [x] remote-history-integration — 충돌 24개 해결·38개 테스트 통과 후 사용자 병합 커밋·push 완료. GitHub API로 main=186ecb7, 부모 b623d67·da6377f 확인. 최신 원격 README·이미지 4개·기존 앱 기능 보존, 루트 중복 CSV 제거. 근거 `.handoff/merge-current/report.md` (2026-11-11)
- [x] kakao-route-panel — 사용자가 `.env`에 키 입력(2026-11-11). 실서버 인증 성공(강남역→선릉역 2.12km). 홈 지도 상세 패널 아래 `route_panel` 연결, 출발지 문구를 기준 위치로 정정, 문서 3개 갱신. 테스트 39개 통과, 실제 키 AppTest 클릭 29.19km·49분, verify-app 흐름 통과 (2026-11-11)

## 지켜야 할 제약
- (2026-11-11) "python라이브러리에서 GPS 라이브러리 이용해서 현재위치 기능 추가해줘."
- README 원칙: 프로젝트에 HTML·CSS·JavaScript 파일을 두지 않고 `unsafe_allow_html` 을 쓰지 않는다.
- (2026-11-11) "5개 구만 우선적으로 구현을 진행하려고 해"
- 위험점수 규칙(RISK_MODEL.md): 빠진 입력을 0으로 채우거나 가중치를 재분배하지 않는다.
- (2026-11-11) 사용자 지시: Codex는 Git 명령을 직접 실행하지 않는다.

## 인계
- 갱신: 2026-11-11 (카카오 길찾기 패널 활성화·실서버 인증 확인, Claude 로컬 커밋)
- 상태(remote-history-integration): 완료. 로컬 main·origin/main·GitHub main=186ecb7c0f081a98874b39c57aead40cef870b67. 부모 b623d67·da6377f. MERGE_HEAD·index.lock·Vim 임시 파일 없음. `.handoff/merge-current/report.md:1`.
- 다음 행동: 사용자가 실행 중인 앱을 재실행해 상세 패널의 ‘자동차 경로 조회’ 확인. kakao-route-panel 로컬 커밋은 push 전(원격 반영은 사용자 결정). rainfall-all-districts는 기존 사용자 결정대로 보류.
- 마지막 검증: 임시 Python 3.12 `python -B -m unittest discover -s tests -t .` → 39 OK(1.919초). verify-app 흐름 `.handoff/verify_route_panel.mjs`(실행 시 tests/로 옮겨야 복사됨) 통과, 지도 배경만 인터넷 차단.
- 커밋 안 된 파일: 없음(kakao-route-panel 커밋에 이전 TASKS.md 기록 포함). `.env`·`.handoff/`는 제외 유지.
- Git 제약: Codex는 모든 Git 명령·인덱스 쓰기를 실행하지 않는다. 사용자가 스테이징·커밋·push를 진행한다.
- 복구: 실제 충돌 원본·양쪽 버전 `.handoff/merge-current/`, 이전 원본·준비본 `.handoff/merge-latest/`. 이전 인계 전문 `.handoff/merge-current/previous-handoff.md`. `.handoff/`는 업로드 제외. 이전 준비본으로 최신 README를 덮지 않는다.
- 서비스 기준: `services/parking_data.py:34`에서 5개 구 + score.notna() 필터. 점수 CSV 137곳만 지도·검색·비교·분석에 표시. 버전 scored-service-v5. 전체 데이터 806곳 중 669곳 점수 NULL 유지. `.handoff/scored-service-only.md`.
- 점수 경로: `data/raw/parking_risk_result_recalculated.csv`만 유지. 루트 중복 제거 전후 SHA-256 d30304771fa6364ce1b961d7bb771fec69505c2a8978cee86f081b34542d4934 동일. 위험점수 137개는 정수 21~80.
- FAQ: `sql/Table07_faq.sql` 원본 27개·4개 분류, `services/faq.py:7`에서 읽음. 덤프·조회 SQL 동기화. FAQ024의 원문 164곳과 현재 137곳 차이는 제공 문구 유지. `.handoff/faq-categories.md`.
- API: 키 입력됨(32자 REST 키, 값 미출력). `services/api_config.py:10`이 조회 때마다 루트 .env를 다시 읽고 운영 환경 변수 우선. 길찾기 패널 `pages/0_Home.py:184` 활성, 출발지=기준 위치. 실서버 인증 성공. `.handoff/api-env.md`.
- 구조 정리: `app.py` 실행, `docs/restructure/target_map.md` 4단계 완료. 상단 이동 전 테스트 명령 대신 현재 discover 명령 사용. Windows 배치·이번 실제 MySQL 적재·브라우저 시각 검증은 미실행.
- rainfall-all-districts 보류: 사용자 5개 구 우선 선택. 확대 시 AWS 23지점 + ASOS 108의 2025 시간 강수량을 data/raw/kma_hourly/에 확보 → `python scripts/build_rainfall.py --check-only`. 최종 점수 CSV는 별도 확보.
- 한도 대비: 사용자 지시로 만든 `.handoff/codex_fallback.py`와 `.handoff/sessions.json` 설명은 「결정」 참조. 설정·감시기 생존은 이번 확인하지 않음.
- 미결정: 없음. 병합 커밋·원격 업로드 완료.

## 사용자 단계
1. 켜져 있는 앱(localhost:8501, 08:52 시작)을 끄고 다시 켠다 — 이전 코드를 메모리에 들고 있어 GPS 버튼이 안 보인다.
2. 실제 브라우저에서 ‘◎ 현재 위치’ → ‘GPS로 내 위치 찾기’ → 위치 ‘허용’. macOS 는 시스템 설정 > 개인정보 보호 및 보안 > 위치 서비스에서 브라우저도 켜져 있어야 한다.
3. (보류 — 구를 늘릴 때만) (강수) Claude 앱 오른쪽 브라우저 창에 열린 data.kma.go.kr 에서 직접 로그인한다(회원가입 필요 시 가입). 비밀번호는 Claude 가 입력하지 않는다.
4. (restructure 한도 대비) 터미널 패널 'codex 폴더 신뢰 1회' 탭에 뜬 Codex 화면에서 이 폴더를 신뢰(Trust)로 고른 뒤 `/quit` 으로 닫는다 — 신뢰 전에는 감시기가 띄운 Codex 가 'blocked' 로 멈춘다.
5. (API .env) 키 입력 완료. 실행 중인 앱을 끄고 다시 켠다(화면 코드 변경 반영, 새 환경이면 먼저 `pip install -r requirements.txt`). 지도에서 주차장 ‘상세 보기’ → ‘자동차 경로 조회’. 실제 키·`.env` 사본은 업로드 제외.

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
- verify-app 은 `.gitignore`된 폴더(`.handoff/`)의 흐름 파일을 복사하지 않고, Streamlit 은 웹소켓 때문에 `networkidle` 대기가 끝나지 않는다 — 흐름 파일은 추적 폴더에 두고 `domcontentloaded` 로 연다.
- Altair 범례는 scale domain 에 든 값을 모두 보여 준다 — 개수에서 뺀 등급(미산정)도 domain 에서 빼야 범례에서 사라진다.

## 실측
| 항목 | 값 | 출처 (날짜) |
|---|---|---|
| streamlit (.venv) | 1.67.0 | `.venv/bin/python -c "import streamlit"` (2026-11-11) |
| streamlit-js-eval 최신 | 1.0.0 | `pip index versions` (2026-11-11) |
