# 침착 — Streamlit 버전 (Python + Streamlit 전용)

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
API 키는 필요 없습니다. 지도 배경 타일 로딩에만 인터넷 연결이 필요합니다.

현재 위치는 `streamlit-js-eval` 라이브러리의 `get_geolocation()`이 브라우저 위치(휴대폰은 GPS, 노트북은 주로 Wi-Fi)를 받아 옵니다.
프로젝트에 JavaScript 파일을 추가하지 않고 라이브러리 안의 브라우저 코드를 씁니다. 브라우저는 `https` 주소나 `http://localhost`에서만 위치를 알려 주므로,
`http://192.168…` 같은 네트워크 주소로 접속하면 위치 권한 오류가 나고 기준 위치를 직접 골라야 합니다.

## 기존과 동일하게 유지한 것

- 로고(`assets/chimchak-logo.png`), 자동차·물방울 지도 핀(`parking_marker.py` 원본 SVG), 점수별 물 높이·색상 그라데이션, 선택 핀 강조
- 사이드바 메뉴 3개: 홈(주차장 탐색) / FAQ / 분석 데이터 결과
- 히어로 문구와 태그, 상단 브랜드 바, 하단 푸터
- 검색(거리 제한 없음), 내 주변 반경(200m–2km, 기본 300m), 전체보기 ↔ 구별 보기(산정된 곳만), 가까운 거리순 목록 3개
- 핀 클릭·상세 보기 → 상세 패널, 비교에 담기(최대 3개), 주차장 상세 비교(정렬 3종)
- 핀 아래 점수 라벨(전체보기에서는 숨김), 점수 구간별 핀 범례
- 데이터 출처·계산 방법 탭, 분석 페이지(등급 도넛·구간 막대·상위/하위), FAQ 카테고리
- 위험점수 계산(`risk_model.py`, `risk_data.py`, `parking_data.py`)과 테스트 파일은 원본 그대로

## 바뀐 것 (JavaScript가 필요해 대체한 부분)

| 기존 (카카오 지도 JS 컴포넌트) | 이 버전 |
|---|---|
| 카카오 지도 | `st.pydeck_chart` (Streamlit 기본 포함, 키 불필요) |
| 지도 안 반경 슬라이더·전체보기 버튼 | 지도 위 Streamlit 슬라이더·토글 |
| ◎ 현재 위치 (브라우저 GPS) | ◎ 현재 위치 팝오버의 ‘GPS로 내 위치 찾기’(`streamlit-js-eval` 라이브러리) 또는 기준 장소 선택·좌표 입력 |
| 일반지도·위성지도·지형 전환 | 미지원 (기본 지도 1종) |
| 핀 클릭 시 정보창 | 핀에 마우스를 올리면 툴팁, 클릭하면 상세 패널 |
| `assets/design.css`, `style.css` 스타일 | `.streamlit/config.toml` 테마 색상 |

카카오 길찾기(`kakao_panel.py`, `kakao_navi.py`)는 원본처럼 비활성 상태로 보관했습니다. 키는 코드에 적지 않고 환경 변수 `KAKAO_REST_API_KEY`에서만 읽습니다.

## 예시 데이터와 제한

서비스 지역은 강수 원본이 있는 5개 구(강북·강서·도봉·서대문·은평)이며, 앱은 이 구의 주차장 163개만 보여 줍니다. 모두 위험점수가 산정됩니다.
점수 계산과 정규화 기준(최대 최소거리 등)은 주차장 806개 전체로 하므로, 서비스 지역을 좁혀도 163개의 점수는 바뀌지 않습니다. SQL 덤프도 806개 전체를 담습니다.
다른 구는 2025년 기상청 시간별 강수 CSV 를 `data/kma_hourly/` 에 두고 `python build_rainfall.py` 로 `data/rainfall.csv` 에 행을 추가하면 서비스 지역에 자동으로 들어옵니다(기상자료개방포털 내려받기는 로그인 필요).
대표좌표 기반 추정 위험도이며 실시간 침수 예측이 아닙니다. 낮은 점수도 안전을 보장하지 않습니다. 거리는 모두 직선거리입니다.

## 테스트

```bash
python -m unittest test_risk_model test_parking_marker test_map_payload test_risk_inventory test_gps_location test_build_rainfall
```
