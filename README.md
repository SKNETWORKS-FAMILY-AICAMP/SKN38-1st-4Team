# 침착 — 데이터로 확인하는 내 주변의 침수 위험 주차장

SKN38 1차 프로젝트 4팀. 2025년 강수량, 지형(고도), 과거 침수 이력 자료로 서울 주차장별 **상대적인** 침수 위험도를 비교해 보여 주는 Streamlit 웹앱입니다. 실시간 침수 예측이 아닙니다.

> 지금은 개발 환경과 문서만 준비된 상태이고 앱 코드는 아직 없습니다.

## 문서

| 문서 | 내용 |
|---|---|
| [AGENTS.md](AGENTS.md) | AI 에이전트(Claude Code, Codex)와 사람이 함께 따르는 작업 지침: 폴더 구조, 코드 규칙, 화면에서 지킬 것, 검사, git 순서 |
| [CLAUDE.md](CLAUDE.md) | Claude Code 가 AGENTS.md 를 읽게 하는 연결 |
| [docs/product-plan.md](docs/product-plan.md) | 화면 기획: 메뉴, 화면별 구성, 지운 기능, 색, 문구 규칙 |
| [docs/risk-index.md](docs/risk-index.md) | 위험지수: 사용 자료와 출처, 계산식, 가중치, 등급, 안내 문구, 앱 입력 자료 형식 |
| [docs/plan-images/](docs/plan-images/) | 기획 시안 이미지 |

## 개발 환경 준비

Python 3.11 이상이 필요합니다. 저장소를 받은 폴더에서 가상환경을 만들고 패키지를 설치합니다.

```bash
git clone https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN38-1st-4Team.git
cd SKN38-1st-4Team
python -m venv .venv
```

macOS·Linux:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
```

Windows(PowerShell):

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

> 예전에 저장소에 올라가 있던 `.venv` 폴더는 이제 git 이 관리하지 않습니다. 이 변경을 받은 뒤 `.venv` 가 지워졌다면 위 순서로 다시 만드세요.

## 앱 실행

앱 시작 파일(예: `streamlit_app.py`)을 만든 뒤 실행합니다. 브라우저에서 http://localhost:8501 이 열립니다.

```bash
.venv/bin/streamlit run streamlit_app.py
```

Windows 는 `.venv\Scripts\streamlit.exe run streamlit_app.py` 입니다.

## 검사

코드 검사(ruff)와 테스트(pytest)를 돌립니다. 테스트는 `tests/` 폴더에 `test_*.py` 로 둡니다. PR 을 올리면 GitHub Actions 가 같은 검사를 돌립니다.

```bash
.venv/bin/python -m ruff check . && .venv/bin/python -m ruff format --check . && .venv/bin/python -m pytest
```

## 작업 올리기

main 에 바로 올리지 않고 브랜치를 만들어 PR 로 올립니다.

```bash
git switch main && git pull
git switch -c <브랜치 이름>
git add <파일> && git commit -m "<무엇을 바꿨는지>"
git push -u origin <브랜치 이름>
```

GitHub 에서 PR 을 만들고, 검사가 초록이면 합칩니다.

## 저장소에 올리지 않는 것

`.gitignore` 가 막아 둡니다.

- 가상환경 `.venv/` — 팀원마다 운영체제와 경로가 달라서 각자 만듭니다.
- 비밀값 — API 키는 `.env` 나 `.streamlit/secrets.toml` 에 두고 올리지 않습니다.

## 환경 파일

| 파일 | 하는 일 |
|---|---|
| `requirements.txt` | 앱 실행에 필요한 패키지(streamlit, pandas) |
| `requirements-dev.txt` | 개발용 패키지(ruff, pytest) 추가 |
| `pyproject.toml` | ruff·pytest 설정 |
| `.streamlit/config.toml` | Streamlit 테마(흰색·파란색 기본) |
| `.github/workflows/ci.yml` | PR·main 에 검사 자동 실행 |
| `.gitignore` | git 에 올리지 않을 파일 |
| `.gitattributes` | 윈도우·맥 줄바꿈 차이 맞춤 |
