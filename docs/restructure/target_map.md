# 침착 폴더 구조 대응표

참고 저장소 SKN38-1st-1Team의 커밋 `61ef27d0`을 조사한 네 보고서와 침착의 현재 코드에 맞춰 이동한다.
기준은 기존 테스트 28개, 서비스 5개 구의 산정된 주차장 163개, 전체 806개를 기준으로 한 위험도 및 SQL이다.

| 순서 | 기존 위치 | 새 위치와 검증 |
| --- | --- | --- |
| 1 | 루트 기능 모듈 9개 | `services/`에 모으고 내부 호출·테스트·Windows 준비 파일의 import를 맞춘다. 기존 판정 테스트를 돌린다. |
| 2 | `app.py` 본문과 FAQ | `app.py`는 직접 실행·공통 초기화·화면 등록을 맡긴다. `pages/0_Home.py`, `pages/1_FAQ.py`, `pages/2_Analysis_Results.py`를 등록한다. 왼쪽 메뉴와 공통부는 `services/ui.py`, FAQ 원문은 `services/faq.py`로 이동한다. SQL 생성기는 FAQ 원문을 직접 가져온다. |
| 3 | `build_rainfall.py`, `sql/build_dump.py`, 루트 테스트 6개 | `scripts/build_rainfall.py`, `scripts/build_sql_dump.py`, `tests/`로 이동한다. `sql/`에는 기존 덤프와 조회 SQL을 둔다. `python -m unittest discover -s tests -t .`와 스크립트 진입점을 검증한다. |
| 4 | `data/`, 자산, 루트 문서 | 주차장·침수심·저지대 입력을 `data/raw/`, 기존 강수 집계값을 `data/processed/`, 감사 표본을 `tests/fixtures/`에 둔다. `services/data_paths.py`에서 경로를 관리하고 기존 해시를 새 경로로 검증한다. 문서는 `docs/`로 옮기고 README의 실행·검증 안내와 폴더 트리를 갱신한다. |

홈 전용 검색·상세·비교는 홈 화면에 모은다. 등급과 마커는 기존 마커 모듈을 공유하고 지도·GPS는 기존 모듈에서 관리한다. FAQ와 분석 주소는 각각 `/faq`와 `/analysis-results`다.

19개 구의 강수 자료 확보는 보류 상태다. 기존 강수 집계의 값은 유지하고, 이후 다운로드와 집계에 사용하는 경로를 문서와 스크립트에서 함께 갱신한다.

완료 조건은 기존 28개 테스트 통과, 홈·FAQ·분석 화면 진입, 5개 구와 163개 표시 유지, 전체 SQL 행과 스키마의 기준 일치, 파일 경로와 문서의 일치다. 각 단계의 검증과 재개 위치는 `TASKS.md`의 인계에 적는다.
