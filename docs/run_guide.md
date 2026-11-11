# 실행·개발 안내 — Python + Streamlit

`1차git-2`의 화면·기능을 그대로 유지하면서 **HTML·CSS·JavaScript 파일 없이** Python과 Streamlit만으로 다시 구성했습니다.
`unsafe_allow_html`도 쓰지 않습니다.

## 실행

Python 3.10 이상.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Windows에서는 기존처럼 `실행.bat`을 더블클릭해도 됩니다. VS Code의 "Run Python File"로 `app.py`를 실행해도 `launch.py`가 Streamlit을 띄웁니다.
기본 지도·GPS·위험도 조회에는 API 키가 필요 없습니다. 지도 배경 타일 로딩에 인터넷 연결이 필요합니다.

현재 위치는 `streamlit-js-eval` 라이브러리의 `get_geolocation()`이 브라우저 위치(휴대폰은 GPS, 노트북은 주로 Wi-Fi)를 받아 옵니다.
프로젝트에 JavaScript 파일을 추가하지 않고 라이브러리 안의 브라우저 코드를 씁니다. 브라우저는 `https` 주소나 `http://localhost`에서만 위치를 알려 주므로,
`http://192.168…` 같은 네트워크 주소로 접속하면 위치 권한 오류가 나고 기준 위치를 직접 골라야 합니다.

## 기존과 동일하게 유지한 것

- 로고(`assets/logo_main.png`), 자동차·물방울 지도 핀(`services/parking_marker.py` 원본 SVG), 점수별 물 높이·색상 그라데이션, 선택 핀 강조
- 사이드바 메뉴 3개: 홈(주차장 탐색) / FAQ / 분석 데이터 결과
- 히어로 문구와 태그, 상단 브랜드 바, 하단 푸터
- 검색(거리 제한 없음), 내 주변 반경(200m–2km, 기본 300m), 전체보기 ↔ 구별 보기, 가까운 거리순 목록 3개
- 핀 클릭·상세 보기 → 상세 패널, 비교에 담기(최대 3개), 주차장 상세 비교(정렬 3종)
- 핀 아래 점수 라벨(전체보기에서는 숨김), 점수 구간별 핀 범례
- 데이터 출처·참고 지표 탭, 분석 페이지(등급 도넛·구간 막대·상위/하위), FAQ 카테고리

## 바뀐 것 (JavaScript가 필요해 대체한 부분)

| 기존 (카카오 지도 JS 컴포넌트) | 이 버전 |
|---|---|
| 카카오 지도 | `st.pydeck_chart` (Streamlit 기본 포함, 키 불필요) |
| 지도 안 반경 슬라이더·전체보기 버튼 | 지도 위 Streamlit 슬라이더·토글 |
| ◎ 현재 위치 (브라우저 GPS) | ◎ 현재 위치 팝오버의 ‘GPS로 내 위치 찾기’(`streamlit-js-eval` 라이브러리) 또는 기준 장소 선택·좌표 입력 |
| 일반지도·위성지도·지형 전환 | 미지원 (기본 지도 1종) |
| 핀 클릭 시 정보창 | 핀에 마우스를 올리면 툴팁, 클릭하면 상세 패널 |
| `assets/design.css`, `style.css` 스타일 | `.streamlit/config.toml` 테마 색상 |

카카오 길찾기(`services/kakao_navi_view.py`, `services/kakao_navi.py`)는 원본처럼 화면에서 비활성 상태로 보관했습니다. API 키 설정 방법은 아래를 따릅니다.

## API 키 설정 (.env)

프로젝트 루트의 `.env` 파일에 카카오모빌리티 **REST API 키**를 입력합니다.

```dotenv
KAKAO_REST_API_KEY=발급받은_REST_API_키
```

`services/api_config.py`가 실행 폴더와 관계없이 루트 `.env`를 읽고, `services/kakao_navi.py`가 이 값으로 카카오 자동차 길찾기 요청을 인증합니다. 같은 이름의 운영 환경 변수가 있으면 그 값이 우선합니다. 파일 값은 API 요청 시 다시 읽으며, 키가 비어 있으면 외부 호출 없이 설정 안내를 표시합니다.

기존 환경에서는 `pip install -r requirements.txt`로 추가된 `python-dotenv`를 설치하고 앱을 다시 실행합니다. Windows의 `실행.bat`도 이 의존성을 확인·설치합니다. 키 설정만으로 비활성 길찾기 패널이 화면에 추가되지는 않습니다.

`.env`와 그 사본은 `.gitignore`에서 제외합니다. GitHub 웹 업로드 시에는 `.gitignore`가 파일 선택을 막아 주지 않으므로 직접 제외하세요. 다른 PC에서는 루트에 위 형식의 `.env`를 만들어 사용합니다.

## 예시 데이터와 제한

서비스는 강수 자료가 있는 5개 구(강북·강서·도봉·서대문·은평)에서 추정 위험점수가 산정된 주차장 137개만 제공합니다. `data/raw/parking_risk_result_recalculated.csv`의 `total_risk_score` 정수를 주차장 관리번호로 연결하며, 점수가 없는 주차장은 서비스 개수·검색·목록·지도·비교·분석에서 제외합니다.
침수심·거리·강수·저지대는 상세 화면의 참고 지표입니다. SQL 덤프는 전체 주차장 806개와 CSV에서 가져온 최종 점수를 담습니다.
다른 구를 추가하려면 2025년 기상청 시간별 강수 CSV를 `data/raw/kma_hourly/`에 두고 `python scripts/build_rainfall.py`로 강수 집계를 갱신합니다. 최종 위험지수는 점수 CSV에 해당 관리번호와 점수를 추가해야 표시됩니다.
점수는 상대 위험도이며 실시간 침수 예측이 아닙니다. 낮은 점수도 안전을 보장하지 않습니다. 거리는 모두 직선거리입니다.

## 폴더 구조

```text
├── app.py                    # Streamlit 진입점
├── .env                      # 로컬 API 키 (GitHub 업로드 제외)
├── pages/
│   ├── 0_Home.py             # 주차장 검색·지도·비교
│   ├── 1_FAQ.py
│   └── 2_Analysis_Results.py
├── services/                 # 자료 적재, 위험도, 지도·GPS, 공통 UI
├── scripts/                  # 강수 집계와 MySQL 덤프 생성
├── tests/                    # unittest와 검증 기준값
├── data/
│   ├── raw/                  # 주차장, 침수심, 저지대, 기상청 시간자료
│   │   └── parking_risk_result_recalculated.csv  # 제공된 최종 위험지수
│   ├── processed/            # 자치구별 강수 집계
│   └── risk_config.json      # 위험점수 계산 설정
├── sql/                      # FAQ 원본 SQL, MySQL 통합 덤프와 조회 쿼리
│   ├── Table07_faq.sql        # FAQ 원본 (화면에서 직접 읽음)
│   ├── skn_1st_4team.sql      # 전체 7개 테이블 통합 덤프
│   ├── faq_queries.sql
│   ├── parking_risk_queries.sql
│   └── flood_rainfall_queries.sql
├── docs/                     # 위험점수, 팀 공동작업, 구조 정리
├── assets/                   # 로고와 마커 참고 이미지
└── .streamlit/               # Streamlit 테마
```

위험점수 계산과 데이터 범위는 [위험점수 문서](risk_model.md), 팀원 실행과 업로드 절차는 [공동작업 안내](upload_guide.md)에 있습니다.
MySQL 덤프를 다시 생성하려면 프로젝트 루트에서 `python scripts/build_sql_dump.py`를 실행합니다.
FAQ는 `sql/Table07_faq.sql`을 직접 읽어 질문 27개와 카테고리 4개를 표시합니다. 질문·답변·카테고리를 수정하면 화면에도 반영되며, SQL 덤프는 위 생성 명령으로 갱신합니다.
GitHub 업로드 위치와 이번 FAQ 수정 파일 목록은 [공동작업 안내](upload_guide.md#faq-수정-업로드-위치)를 따릅니다.

## 테스트

```bash
python -m unittest discover -s tests -t .
```
