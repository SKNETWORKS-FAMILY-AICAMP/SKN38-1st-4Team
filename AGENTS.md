# 에이전트 작업 지침 — 침착

이 저장소에서 일하는 AI 에이전트(Claude Code, Codex 등)와 사람이 함께 따르는 기준입니다. Codex 는 이 파일을 바로 읽고, Claude Code 는 `CLAUDE.md` 를 거쳐 읽습니다.

## 프로젝트

- 이름: 침착 — 데이터로 확인하는 내 주변의 침수 위험 주차장
- 하는 일: 2025년 강수량, 지형(고도), 과거 침수 이력 자료로 서울 5개 자치구(강북·강서·도봉·서대문·은평) 주차장별 **상대적** 침수 위험도(0~100점)를 계산하고, 내 위치 주변 주차장을 거리순으로 보여 주며 서로 비교하게 하는 Streamlit 웹앱
- 하지 않는 일: 실시간 침수 예측, 회원가입·로그인
- 지금 상태: 개발 환경, 문서, 앱 입력 자료(`data/parking_risk.csv`)와 그 읽기·검증 코드(`core/parking.py`)가 있고 화면 코드는 아직 없음

## 먼저 읽을 문서

| 문서 | 내용 |
|---|---|
| `docs/product-plan.md` | 화면 기획: 메뉴, 화면별 구성, 지운 기능, 색, 문구 규칙, 시안 이미지 목록 |
| `docs/risk-index.md` | 위험지수: 사용 자료와 출처, 분석 과정, 계산식, 가중치, 등급, 안내 문구, 앱 입력 자료 형식 |
| `README.md` | 개발 환경 준비, 실행, 검사, 작업 올리기 |

문서끼리 다르면 이 파일 → `docs/` 문서 → 시안 이미지 순으로 따릅니다. 시안 이미지(`docs/plan-images/`)에는 기획에서 지운 기능(로그인, 지상/지하, 분석 지역 등)이 남아 있으니 그림만 보고 만들지 않습니다.

## 기술 스택

- Python 3.11 이상(CI 는 3.12)
- `requirements.txt`: streamlit 1.67.0, pandas 3.1.1
- 차트는 altair, 지도는 pydeck 을 씁니다. 둘 다 streamlit 을 설치하면 같이 들어옵니다.
- `requirements-dev.txt`: ruff 0.17.4(코드 검사·포맷), pytest 9.2.0(테스트)
- 새 패키지는 팀과 합의한 뒤 판을 고정해(`==`) `requirements.txt` 에 넣습니다.

## 폴더 구조

지금은 환경 파일, 문서, `data/`, `analysis/build_parking_risk.py`, `core/parking.py`(읽기·검증), `tests/` 까지 있습니다. 코드를 만들 때 이 구조를 따르고, 구조를 바꾸면 이 절도 같은 PR 에서 고칩니다.

```text
SKN38-1st-4Team/
├── AGENTS.md                  에이전트 작업 지침(이 파일)
├── CLAUDE.md                  Claude Code 가 이 파일을 읽게 하는 연결
├── README.md                  사람용 시작 안내
├── streamlit_app.py           앱 시작점. st.navigation 으로 상단 메뉴 3개를 연결
├── app/                       화면(Streamlit 코드)
│   ├── ui.py                  공통 화면 요소: 안내 문구, 등급 배지·색, 요인 막대, 공통 CSS
│   └── views/
│       ├── explore.py         주차장 탐색(첫 화면): 주변 주차장 검색 탭, 주차장 상세 비교 탭, 아래 데이터 출처·계산 방법 탭
│       ├── dashboard.py       데이터 분석 결과 대시보드
│       └── faq.py             FAQ
├── core/                      계산(streamlit 을 import 하지 않음)
│   ├── risk.py                위험지수 계산, 가중치, 등급 경계와 색
│   ├── geo.py                 거리 계산(하버사인), 반경 선택지
│   ├── parking.py             앱 입력 자료 읽기·검증, 반경 검색, 정렬, 등급별 집계, 분포, 상·하위
│   └── faq.py                 FAQ 카테고리·질문·답변
├── analysis/                  원본 자료를 가공해 data/ 의 앱 입력 자료를 만드는 코드(노트북 포함)
├── data/
│   ├── parking_risk.csv       앱 입력 자료(형식은 docs/risk-index.md 「앱 입력 자료」)
│   └── raw/                   원본 자료(용량이 크면 올리지 않고 받는 곳을 docs 에 적음)
├── tests/                     pytest 테스트(test_*.py)
├── docs/
│   ├── product-plan.md        화면 기획
│   ├── risk-index.md          위험지수
│   └── plan-images/           기획 시안 이미지
├── .streamlit/config.toml     Streamlit 테마(흰색·파란색)
├── .github/workflows/ci.yml   PR·main 에 검사 자동 실행
├── requirements.txt           앱 실행 패키지
├── requirements-dev.txt       개발용 패키지
├── pyproject.toml             ruff·pytest 설정
├── .gitignore                 git 에 올리지 않을 파일
└── .gitattributes             윈도우·맥 줄바꿈 맞춤
```

## 코드 작성 규칙

- 계산은 `core/`, 화면은 `app/` 에 둡니다. `core/` 는 streamlit 을 import 하지 않고, 화면 코드는 `core` 함수를 불러 보여 주기만 합니다. 그래야 계산을 화면 없이 테스트할 수 있습니다.
- 가중치, 등급 경계, 등급 색, 반경 선택지, 안내 문구는 한 곳(`core/risk.py`, `core/geo.py`, `app/ui.py`)에만 둡니다. 화면 코드에 숫자나 문구를 따로 적지 않습니다.
- `core/` 함수를 만들거나 바꾸면 `tests/` 에 테스트를 같이 씁니다. 화면은 `streamlit.testing.v1.AppTest` 로 오류 없이 그려지는지 확인합니다.
- 화면 글은 한국어로 쓰고 `docs/product-plan.md` 「문구 규칙」을 따릅니다.
- 자료 파일은 `@st.cache_data` 로 한 번만 읽습니다.
- 자료에 꼭 있어야 할 열이 없거나 값이 범위(0~1)를 벗어나면 조용히 넘기지 말고 오류를 냅니다.

알아 둘 함정:

- Streamlit 마크다운에서 물결표가 두 번 나오면(`0~39점, 40~69점`) 그 사이가 취소선으로 그려집니다. 화면에 넣는 글의 `~` 는 `\~` 로 바꿉니다.
- `AppTest.from_file()` 에 상대 경로를 주면 테스트 파일 위치를 기준으로 찾습니다. `Path(__file__).resolve().parents[1]` 같은 절대 경로를 씁니다.
- 실행 중인 Streamlit 서버는 한 번 import 한 모듈을 다시 읽지 않습니다. `core/`·`app/ui.py` 를 고쳤으면 서버를 껐다 켭니다.

## 화면에서 반드시 지킬 것

1. 「2025년 데이터 기반 상대적 위험도 · 실시간 침수 예측 아님」 안내를 지도와 위험지수 옆에 항상 표시합니다.
2. 위험도는 모든 등급을 붉은 계열로 칠하고 등급이 높을수록 진하게 합니다. 초록·노랑처럼 「안전」으로 읽히는 색은 쓰지 않습니다.
3. 「안전」「안전한 주차장」처럼 위험이 없다고 읽히는 말을 쓰지 않습니다. 등급 이름은 「상대적 낮음 / 보통 / 상대적 높음」입니다.
4. 첫 화면 목록은 거리순으로만 정렬합니다. 검색 반경은 500m, 1km, 1.5km, 2km 넷입니다.
5. 상세 위험 요인은 강수량 위험 → 지형(고도) 위험 → 침수 이력 위험 순서로 보여 줍니다.
6. 만들지 않는 것: 회원가입·로그인과 회원 전용 기능, 주차장 유형(지상/지하), 대시보드의 분석 지역·자치구 지도·유형별 평균·분석 인사이트, 별도 「데이터 / 분석 기준」 페이지

## 비밀값

- API 키 같은 비밀값은 `.env` 또는 `.streamlit/secrets.toml` 에만 두고 커밋하지 않습니다. `.gitignore` 가 막아 둡니다.
- 코드는 `st.secrets` 나 환경 변수로 읽습니다. 키를 코드, 로그, 커밋 메시지, 오류 메시지, 화면에 쓰지 않습니다.
- 필요한 키 이름은 값을 비운 채 `.env.example` 에 적어 둡니다(이 파일은 올라갑니다).

## 끝내기 전 검사

아래가 모두 통과해야 작업이 끝난 것입니다. 포맷 검사가 실패하면 `ruff format .` 으로 고칩니다.

```bash
.venv/bin/python -m ruff check . && .venv/bin/python -m ruff format --check . && .venv/bin/python -m pytest
```

Windows(PowerShell)는 한 줄씩 실행합니다.

```powershell
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m ruff format --check .
.venv\Scripts\python.exe -m pytest
```

화면을 바꿨으면 `streamlit run streamlit_app.py` 로 직접 열어 바뀐 화면을 눈으로 확인합니다.

## git 작업 순서

팀 저장소(`SKNETWORKS-FAMILY-AICAMP/SKN38-1st-4Team`)를 각자 포크해서 작업합니다. 리모트는 둘입니다: `origin` 은 내 포크, `upstream` 은 팀 저장소. `upstream` 이 없으면 `git remote add upstream https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN38-1st-4Team.git` 로 더합니다.

1. `git switch main && git pull --ff-only upstream main && git push origin main` 으로 팀 저장소 최신을 받아 내 포크 main 을 맞추고, 작업 브랜치를 만듭니다: `git switch -c <종류>/<내용>` (예: `feat/explore-map`).
2. 한 브랜치에는 한 가지 일만 합니다. 관계없는 파일은 고치지 않습니다.
3. 올릴 파일만 골라 `git add` 하고, 커밋 전에 `git status` 로 확인합니다.
4. 커밋 메시지는 Conventional Commits 형식에 한국어 제목을 씁니다: `<종류>(<범위>): <요약>`. 종류는 feat, fix, docs, refactor, test, chore. 예: `feat(탐색): 반경 선택과 거리순 목록`
5. `git push -u origin <브랜치>` 로 내 포크에 올리고, 팀 저장소 `main` 을 base 로 PR 을 만듭니다. PR 본문은 문제 → 해결 → 영향 → 검증을 한 줄씩 씁니다.
6. 팀 저장소의 GitHub Actions 검사가 초록이면 squash 병합하고, 1번으로 돌아가 main 을 다시 맞춥니다. 팀 저장소 main 에 직접 push 하지 않고 force push 하지 않습니다. 내 포크 main 에서는 커밋하지 않고 팀 저장소 main 을 따라가게만 둡니다.
7. `.venv`, 비밀값, 100MB 넘는 파일(GitHub 가 거부함)은 올리지 않습니다.

## 모르는 것은 지어내지 않기

- 가중치(강수량 0.30, 침수 이력 0.45, 지형 0.25)와 등급 경계(0~39, 40~69, 70~100)는 팀이 정한 값입니다(2026-11-10). 시안의 예시값(0.45, 0.35, 0.20)은 쓰지 않습니다. 바꾸기 쉽게 한 곳에만 둡니다.
- 앱 입력 자료 형식은 `docs/risk-index.md` 「앱 입력 자료」를 따릅니다. 형식을 바꾸려면 그 문서를 먼저 고칩니다.
- 문서에 「팀 확인 필요」로 적힌 것은 임의로 정하지 말고, 필요하면 PR 설명에 제안으로 적습니다.
- 기획에 없는 기능은 더하지 않습니다.
